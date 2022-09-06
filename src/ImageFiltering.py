import multiprocessing
from functools import partial
from pathlib import Path

import cv2 as cv
import numpy as np
from skimage.util import random_noise

FILTER_FUNCTIONS = {
    'no_filter': lambda image: image,
    'averaging_blur': partial(cv.blur, ksize=(100, 100)),
    'small_gaussian_blur': partial(cv.GaussianBlur, ksize=(11, 11), sigmaX=0),
    'gaussian_blur': partial(cv.GaussianBlur, ksize=(101, 101), sigmaX=0),
    'small_median_blur': partial(cv.medianBlur, ksize=11),
    'high_median_blur': partial(cv.medianBlur, ksize=101),
    'bilateral_filter': partial(cv.bilateralFilter, d=9, sigmaColor=75, sigmaSpace=75),
    'k-means (k=2)': lambda image: kmean_segmentation(image,  n_clusters=2),
    'k-means (k=3)': lambda image: kmean_segmentation(image,  n_clusters=3),
    'k-means (k=4)': lambda image: kmean_segmentation(image,  n_clusters=4),
    'k-means (k=5)': lambda image: kmean_segmentation(image,  n_clusters=5),
}

NOISE_FUNCTIONS = {
    'no_noise': lambda image: image,
    'gaussian_noise': lambda image: noise_with_skimage(image, 'gaussian'),
    'salt': lambda image: noise_with_skimage(image, 'salt'),
    'pepper': lambda image: noise_with_skimage(image, 'pepper'),
    'salt_and_pepper': lambda image: noise_with_skimage(image, 's&p'),
    'speckle': lambda image: noise_with_skimage(image, 'speckle'),
    'poisson': lambda image: noise_with_skimage(image, 'poisson'),
}


def kmean_segmentation(cv2image, n_clusters):
    pixel_vals = cv2image.reshape((-1, 3))

    pixel_vals = np.float32(pixel_vals)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.85)

    retval, labels, centers = cv.kmeans(pixel_vals, n_clusters, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    segmented_data = centers[labels.flatten()]

    segmented_image = segmented_data.reshape(cv2image.shape)
    return segmented_image


def noise_with_skimage(cv2image, mode: str):
    return 255 * random_noise(np.asarray(cv2image), mode=mode).astype(np.uint8)


def filter_image(cv_image, image_name):
    return {f"{image_name}_{filter_name}": filter_function(cv_image)
            for filter_name, filter_function in FILTER_FUNCTIONS.items()}


def add_noise(cv2image, image_name):
    return {f"{image_name}_{noise_name}": noise_function(cv2image)
            for noise_name, noise_function in NOISE_FUNCTIONS.items()}


def noise_and_filter_image(image_path: str | Path) -> dict[str, str]:
    new_images = dict()

    image_name = Path(image_path).stem
    cv2image = cv.imread(image_path)

    noised = add_noise(cv2image, image_name)

    for name, image in noised.items():
        new_images.update(filter_image(image, name))

    return new_images


def noise_and_filters_images(image_paths: list[str | Path]) -> dict[str, str]:
    new_images = dict()

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(noise_and_filter_image, image_paths)

    for result in results:
        new_images.update(result)

    return new_images
