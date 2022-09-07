import numpy as np
import cv2 as cv
from skimage.util import random_noise


def kmean_segmentation(cv2image, n_clusters):
    pixel_vals = cv2image.reshape((-1, 3))

    pixel_vals = np.float32(pixel_vals)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.85)

    retval, labels, centers = cv.kmeans(pixel_vals, n_clusters, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    segmented_data = centers[labels.flatten()]

    segmented_image = segmented_data.reshape(cv2image.shape)
    return segmented_image


def noise_with_skimage(cv2image, mode: str, **kwargs):
    return 255 * random_noise(np.asarray(cv2image), mode=mode, **kwargs).astype(np.uint8)