"""LH-EXP-0002: synthetic sequential learning, gradient interference and retention.

No real permissions, external actions, LLM training or data downloads.
Run: OPENBLAS_NUM_THREADS=1 python experiment.py
"""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEEDS = range(1100, 1112)
WIDTHS = (1, 4)
METHODS = ('sequential', 'replay_1', 'replay_4', 'projected', 'homeostatic')
CHECKPOINTS = set(range(0, 251, 10))
EPS = 1e-12


def draw(rng, n, shift=False):
    x0 = rng.standard_normal(n)
    x1 = rng.standard_normal(n)
    if shift:
        x1 = .75 * x0 + np.sqrt(1 - .75**2) * x1
    x = np.column_stack((x0, x1))
    y_task = (x1 > 0).astype(float)
    y_reg = (x0 > 0).astype(float)
    return (x, y_task, y_reg)


def init(rng, width):
    return [rng.normal(0, .4, (2, width)),
            np.zeros(width),
            rng.normal(0, .4, (width, 2)),
            np.zeros(2)]


def forward(w, x):
    h = np.tanh(x @ w[0] + w[1])
    return h, h @ w[2] + w[3]


def sigmoid(z):
    return 1. / (1. + np.exp(-np.clip(z, -45, 45)))


def bce(w, data, head):
    x, task, reg = data
    y = (task, reg)[head]
    logit = forward(w, x)[1][:, head]
    return float(np.mean(np.logaddexp(0., logit) - y * logit))


def gradient(w, data, head):
    x, task, reg = data
    y = (task, reg)[head]
    h, z = forward(w, x)
    delta = np.zeros_like(z)
    delta[:, head] = (sigmoid(z[:, head]) - y) / len(y)
    d_h = (delta @ w[2].T) * (1. - h*h)
    return [x.T @ d_h, d_h.sum(axis=0), h.T @ delta, delta.sum(axis=0)]


def apply(w, grad, lr):
    return [p - lr * g for p, g in zip(w, grad)]


def dot(g, h):
    return sum(float(np.sum(a*b)) for a,b in zip(g,h))


def metrics(w, data):
    x, task, reg = data
    z = forward(w, x)[1]
    answer = z[:, 1] >= 0.
    right = z[:, 0] >= 0.
    pos = reg == 1.
    neg = ~pos
    tp = float(np.mean(answer[pos]))
    fp = float(np.mean(answer[neg]))
    return {
        'task_accuracy': float(np.mean(right == task)),
        'gate_balanced_accuracy': (tp + (1.-fp)) / 2.,
        'gate_tpr': tp, 'gate_fpr': fp,
        'gate_brier': float(np.mean((sigmoid(z[:, 1])-reg)**2)),
        'eligible_utility': float(np.mean(answer[pos] & (right[pos] == task[pos]))),
    }


def bootstrap_ci(d, seed=20261127):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, dtype=float)
    means = np.mean(d[rng.integers(0,len(d),(10000,len(d)))], axis=1)
    return [float(v) for v in np.quantile(means,[.025,.975])]


def main():
    out = []
    process = []
    validation = []
    for seed in SEEDS:
        r_data = np.random.default_rng(seed)
        train_reg = draw(r_data, 256)
        train_task = draw(r_data, 256)
        test = {'id': draw(r_data,4096), 'shift': draw(r_data,4096,True)}
        for width in WIDTHS:
            r_init = np.random.default_rng(seed + width*100000)
            base = init(r_init, width)
            # Identical regulatory pretraining across all methods.
            for _ in range(150):
                base = apply(base, gradient(base, train_reg, 1), .15)
            pretrain_eval = metrics(base, test['shift'])
            validation.append({'seed':seed,'width':width, **pretrain_eval})
            for method in METHODS:
                w = [v.copy() for v in base]
                extra_gate_losses = 0
                regulatory_gradient_evals = 0
                rejected = 0
                shortened = 0
                for step in range(251):
                    if step in CHECKPOINTS:
                        for dist, data in test.items():
                            out.append({'seed':seed,'width':width,'method':method,
                                'step':step,'distribution':dist,**metrics(w,data)})
                    if step == 250:
                        break
                    gt = gradient(w, train_task, 0)
                    gr = gradient(w, train_reg, 1)
                    regulatory_gradient_evals += 1
                    inner = dot(gt,gr)
                    cos = inner / (np.sqrt(dot(gt,gt)*dot(gr,gr)) + EPS)
                    old_reg_loss = bce(w, train_reg,1)
                    extra_gate_losses += 1
                    if method == 'sequential':
                        direction = gt
                    elif method == 'replay_1':
                        direction = [a+b for a,b in zip(gt,gr)]
                    elif method == 'replay_4':
                        direction = [a+4*b for a,b in zip(gt,gr)]
                    elif method == 'projected':
                        direction = ([a - (inner/(dot(gr,gr)+EPS))*b for a,b in zip(gt,gr)]
                                     if inner < 0 else gt)
                    else:
                        direction = gt
                    lr = .12
                    if method == 'homeostatic':
                        accepted = False
                        for trials in range(9):
                            candidate = apply(w,direction,lr)
                            delta = bce(candidate,train_reg,1) - old_reg_loss
                            extra_gate_losses += 1
                            if delta <= .0001:
                                w = candidate
                                accepted = True
                                shortened += int(trials>0)
                                break
                            lr *= .5
                        if not accepted:
                            rejected += 1
                            delta = 0.
                    else:
                        w = apply(w,direction,lr)
                        delta = bce(w,train_reg,1) - old_reg_loss
                        extra_gate_losses += 1
                    process.append({
                        'seed':seed,'width':width,'method':method,'step':step+1,
                        'gradient_cosine':cos,'negative_dot':int(inner < 0.),
                        'reg_loss_increase':int(delta > 0.),'reg_loss_delta':delta,
                        'reg_grad_evals':regulatory_gradient_evals,
                        'extra_gate_losses':extra_gate_losses,
                        'rejected':rejected, 'shortened':shortened,
                    })
    for name,records in [('trajectories.csv',out),('process.csv',process),('pretraining.csv',validation)]:
        with (HERE/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(records[0]))
            writer.writeheader();writer.writerows(records)
    fields=list(metrics(init(np.random.default_rng(0),1),draw(np.random.default_rng(1),30)))
    def endpoint(width, method, dist='shift',step=250):
        records = [r for r in out if r['width']==width and r['method']==method
                   and r['distribution']==dist and r['step']==step]
        return {k:float(np.mean([row[k] for row in records])) for k in fields}
    endpoints={str(width):{method:{dist:endpoint(width,method,dist)
                                  for dist in ('id','shift')}
                           for method in METHODS} for width in WIDTHS}
    key=lambda x:x['seed']
    def by_seed(width,method,step,dist='shift'):
        return {r['seed']:r for r in out if r['width']==width and r['method']==method
                and r['distribution']==dist and r['step']==step}
    comparisons={}
    for width in WIDTHS:
        a=by_seed(width,'homeostatic',250)
        b=by_seed(width,'replay_1',250)
        diffs={f:[a[s][f]-b[s][f] for s in SEEDS] for f in fields}
        comparisons[str(width)] = {
            'homeostatic_minus_replay1':{k:{'mean':float(np.mean(v)),
                    'ci95':bootstrap_ci(v)} for k,v in diffs.items()},
            'h1_task_gain': endpoint(width,'sequential')['task_accuracy'] - endpoint(width,'sequential',step=0)['task_accuracy'],
            'h1_gate_drop': endpoint(width,'sequential',step=0)['gate_balanced_accuracy'] - endpoint(width,'sequential')['gate_balanced_accuracy'],
        }
    proc_summary={}
    for width in WIDTHS:
        proc_summary[str(width)]={}
        for method in METHODS:
            r=[p for p in process if p['width']==width and p['method']==method]
            conflicting=[p for p in r if p['negative_dot']==1]
            nonconflicting=[p for p in r if p['negative_dot']==0]
            proc_summary[str(width)][method]={
                'negative_dot_fraction':float(np.mean([p['negative_dot'] for p in r])),
                'gradient_cosine_mean':float(np.mean([p['gradient_cosine'] for p in r])),
                'p_loss_increase_given_negative_dot':float(np.mean([p['reg_loss_increase'] for p in conflicting])) if conflicting else None,
                'p_loss_increase_given_nonnegative_dot':float(np.mean([p['reg_loss_increase'] for p in nonconflicting])) if nonconflicting else None,
                'rejected':int(sum(p['rejected'] for p in r if p['step']==250)),
                'shortened':int(sum(p['shortened'] for p in r if p['step']==250)),
                'reg_gradient_evaluations':int(sum(p['reg_grad_evals'] for p in r if p['step']==250)),
                'gate_loss_evaluations':int(sum(p['extra_gate_losses'] for p in r if p['step']==250)),
            }
    comp=comparisons['1']
    h1=comp['h1_task_gain']>=.10 and comp['h1_gate_drop']>=.10
    h3=(comp['homeostatic_minus_replay1']['gate_balanced_accuracy']['mean']>=.05 and
         comp['homeostatic_minus_replay1']['gate_balanced_accuracy']['ci95'][0]>0 and
         abs(comp['homeostatic_minus_replay1']['task_accuracy']['mean'])<=.03)
    matched=[]
    for width in WIDTHS:
        for seed in SEEDS:
            h=next(r for r in out if r['seed']==seed and r['width']==width and
                  r['method']=='homeostatic' and r['step']==250 and r['distribution']=='shift')
            for method in ('sequential','replay_1','replay_4','projected'):
                other=min((r for r in out if r['seed']==seed and r['width']==width and
                           r['method']==method and r['distribution']=='shift'),
                          key=lambda r: (abs(r['task_accuracy']-h['task_accuracy']),-r['step']))
                matched.append({'seed':seed,'width':width,'baseline':method,
                                'baseline_step':other['step'],
                                'capability_abs_gap':abs(h['task_accuracy']-other['task_accuracy']),
                                'reg_balance_delta':h['gate_balanced_accuracy']-other['gate_balanced_accuracy']})
    with (HERE/'capability_matched.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(matched[0]))
        writer.writeheader();writer.writerows(matched)
    result={
        'status':'exploratory; not independent preregistration; not an LLM safety result',
        'numpy':np.__version__,
        'protocol_sha256':hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'n_seeds':len(SEEDS),'n_runs':len(SEEDS)*len(WIDTHS)*len(METHODS),
        'n_trajectory_rows':len(out),'n_process_rows':len(process),
        'pretraining_mean':{str(width):{
                k:float(np.mean([r[k] for r in validation if r['width']==width])) for k in fields}
                for width in WIDTHS},
        'endpoints':endpoints,'comparisons':comparisons,'process':proc_summary,
        'decision':{'h1_observed_width1':bool(h1),'h3_advantage_width1':bool(h3)},
        'capability_matched_summary':{str(width):{m:{
            'mean_abs_accuracy_gap':float(np.mean([p['capability_abs_gap'] for p in matched if p['width']==width and p['baseline']==m])),
            'mean_reg_balance_difference':float(np.mean([p['reg_balance_delta'] for p in matched if p['width']==width and p['baseline']==m]))
        } for m in ('sequential','replay_1','replay_4','projected')} for width in WIDTHS},
    }
    (HERE/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'decision':result['decision'],
                      'shifted_width1':{m:endpoints['1'][m]['shift'] for m in METHODS},
                      'shifted_width4':{m:endpoints['4'][m]['shift'] for m in METHODS}},indent=2))

if __name__=='__main__':
    main()
