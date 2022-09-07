import multiprocessing
from functools import partial
from pathlib import Path

import cv2 as cv

from DynamicFilter import Filter
from FilterFunctions import kmean_segmentation, noise_with_skimage

FILTER_FUNCTIONS = {
    'no_filter': lambda image: image,
    'averaging_blur': partial(cv.blur, ksize=(100, 100)),
    'small_gaussian_blur': partial(cv.GaussianBlur, ksize=(11, 11), sigmaX=0),
    'gaussian_blur': partial(cv.GaussianBlur, ksize=(101, 101), sigmaX=0),
    'small_median_blur': partial(cv.medianBlur, ksize=11),
    'high_median_blur': partial(cv.medianBlur, ksize=101),
    'bilateral_filter': partial(cv.bilateralFilter, d=9, sigmaColor=75, sigmaSpace=75),
    'k-means (k=2)': lambda image: kmean_segmentation(image, n_clusters=2),
    'k-means (k=3)': lambda image: kmean_segmentation(image, n_clusters=3),
    'k-means (k=4)': lambda image: kmean_segmentation(image, n_clusters=4),
    'k-means (k=5)': lambda image: kmean_segmentation(image, n_clusters=5),
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

FILTER_FUNCTIONS2 = {
    'no_filter': lambda image: {'no_filter': image},
    'averaging_blur': Filter(cv.blur, 'averaging_blur', ksize=[(10, 10), (50, 50), (100, 100)]),
}

NOISE_FUNCTIONS2 = {
    'no_noise': lambda image: {'no_noise': image},
    # 'gaussian_noise': lambda image: {'gaussian_noise': noise_with_skimage(image, mode='gaussian')},
    'gaussian_noise': Filter(partial(noise_with_skimage, mode='gaussian'), 'gaussian_noise', var=[0.01, 0.1]),
}


def apply_to_image(dict_of_functions: dict, cv_image, image_name: str) -> dict:
    generated_images = dict()

    for filter_name, filter_function in dict_of_functions.items():
        # generate new images based on filter function and defined parameters
        new_images = filter_function(cv_image)

        # update the dictionary of images
        generated_images.update(new_images)

    new_images = {f"{image_name}_{key}": value for key, value in generated_images.items()}
    return new_images


def noise_and_filter_image2(image_path: str | Path) -> dict[str, str]:
    new_images = dict()

    image_name = Path(image_path).stem
    image_color = cv.imread(image_path)
    image_bw = cv.cvtColor(image_color, cv.COLOR_BGR2GRAY)

    # Add noise to colored images and to black-white images:
    new_images.update(apply_to_image(NOISE_FUNCTIONS2, image_color, image_name))
    new_images.update(apply_to_image(NOISE_FUNCTIONS2, image_bw, f"{image_name}_bw"))
    print(new_images.keys())

    filtered = dict()
    for name, image in new_images.items():
        r = apply_to_image(FILTER_FUNCTIONS2, image, name)
        print("Filtering", r.keys())
        filtered.update(r)

    filtered[image_name] = image_color
    filtered[f"{image_name}_bw"] = image_bw

    print(filtered.keys())
    return filtered


def noise_and_filters_images2(image_paths: list[str | Path]) -> dict[str, str]:
    new_images = dict()

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(noise_and_filter_image2, image_paths)

    for result in results:
        new_images.update(result)

    return new_images


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
