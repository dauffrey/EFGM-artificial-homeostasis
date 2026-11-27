"""Local numerical and metric unit checks for LH-EXP-0002 (not scientific validation)."""
import numpy as np
import experiment as exp


def test_gradients_finite_difference():
    rng = np.random.default_rng(8)
    dataset = exp.draw(rng, 37)
    for width in (1, 4):
        weights = exp.init(rng, width)
        for head in (0, 1):
            analytic = exp.gradient(weights, dataset, head)
            for group_index, group in enumerate(weights):
                for index in np.ndindex(group.shape):
                    old = group[index]
                    h = 1.e-5
                    group[index] = old + h
                    positive = exp.bce(weights, dataset, head)
                    group[index] = old - h
                    negative = exp.bce(weights, dataset, head)
                    group[index] = old
                    expected = (positive - negative) / (2 * h)
                    assert abs(analytic[group_index][index] - expected) < 1.e-7


def test_projection_removes_first_order_conflict():
    rng = np.random.default_rng(9)
    for width in (1, 4):
        w = exp.init(rng, width)
        gt = exp.gradient(w, exp.draw(rng, 90), 0)
        gr = exp.gradient(w, exp.draw(rng, 90), 1)
        inner = exp.dot(gt, gr)
        if inner < 0:
            projected = [a - inner/(exp.dot(gr,gr)+exp.EPS)*b
                         for a,b in zip(gt,gr)]
            assert exp.dot(projected, gr) >= -1.e-10


def test_always_abstain_is_not_good_regulation():
    rng = np.random.default_rng(11)
    w = exp.init(rng, 4)
    w[3][1] = -100.
    d = exp.draw(rng, 4096)
    result = exp.metrics(w, d)
    assert result['gate_fpr'] == 0.
    assert result['gate_tpr'] == 0.
    assert result['eligible_utility'] == 0.
    assert result['gate_balanced_accuracy'] == .5


if __name__ == '__main__':
    test_gradients_finite_difference()
    test_projection_removes_first_order_conflict()
    test_always_abstain_is_not_good_regulation()
    print('3/3 tests PASS')
