import cv2


# https://github.com/mapbox/robosat/blob/a8e0e3d676b454b61df03897e43e003867b6ef48/robosat/features/core.py#L65-L77  noqa
def denoise(mask, eps):
    """Removes noise from a mask.
    Args:
      mask: the mask to remove noise from.
      eps: the morphological operation's kernel size for noise removal, in pixel.
    Returns:
      The mask after applying denoising.
    """

    struct = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (eps, eps))
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, struct)
