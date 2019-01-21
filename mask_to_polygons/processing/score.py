import numpy as np
import shapely
import shapely.strtree
import shapely.geometry


def spacenet(predictions, ground_truth):
    pred_types = set([type(pred) for pred in predictions])
    truth_types = set([type(truth) for truth in ground_truth])

    if len(pred_types) == 0 or len(truth_types) == 0:
        return {'tp': 0, 'fp': 0, 'fn': 0}
    elif len(pred_types) != 1 or len(truth_types) != 1:
        raise Exception()

    pred_type = pred_types.pop()
    if pred_type == shapely.geometry.polygon.Polygon:
        pass
    elif pred_type == dict:
        predictions = [shapely.geometry.shape(g) for g in predictions]
    else:
        raise Exception()

    truth_type = truth_types.pop()
    if truth_type == shapely.geometry.polygon.Polygon:
        pass
    elif truth_type == dict:
        ground_truth = [shapely.geometry.shape(g) for g in ground_truth]
    else:
        raise Exception()

    tree = shapely.strtree.STRtree(ground_truth)

    def make_valid(p):
        if p.is_valid:
            return p
        else:
            (minx, miny, maxx, maxy) = p.bounds
            stretch = max(maxx - minx, maxy - miny)
            # Take care to handle bow ties:
            # https://github.com/Toblerity/Shapely/issues/462
            return p.buffer(stretch * 0.01)

    def iou(a, b):
        a = make_valid(a)
        b = make_valid(b)
        a_and_b = a.intersection(b).area
        a_or_b = a.union(b).area
        return a_and_b / a_or_b

    def not_already_matched(a):
        return not hasattr(a, 'iou_matched')

    tp = 0
    fp = 0
    fn = 0
    for pred in predictions:
        results = list(filter(not_already_matched, tree.query(pred)))
        scores = list(map(lambda a: iou(a, pred), results))
        if len(scores) > 0:
            argmax = np.argmax(scores)
            if max(scores) > 0.5:
                results[argmax].iou_matched = True
                tp = tp + 1
            else:
                fp = fp + 1
        else:
            fp = fp + 1
    fn = len(list(filter(not_already_matched, ground_truth)))

    return {'tp': tp, 'fp': fp, 'fn': fn}
