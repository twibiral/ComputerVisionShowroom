import logging
import multiprocessing
from functools import partial
from pathlib import Path

import cv2 as cv

import Config
from DynamicFilter import Filter
from FilterFunctions import kmean_segmentation, noise_with_skimage


GENERATED_IMAGES_DIR = str((Config.STATIC_DIR / "generated").absolute())

FILTER_FUNCTIONS = {
    'no_filter': lambda image: {'no_filter': image},
    'averaging_blur': Filter(cv.blur, 'averaging_blur', ksize=[(10, 10), (50, 50), (100, 100)]),
    'gaussian_blur': Filter(cv.GaussianBlur, 'gaussian_blur', ksize=[(3, 3), (5, 5), (11, 11), (51, 51), (101, 101)], sigmaX=0),
    'median_blur': Filter(cv.medianBlur, 'median_blur', ksize=[3, 5, 11, 51, 101]),
    'bilateral_filter': Filter(cv.bilateralFilter, 'bilateral_filter', d=9, sigmaColor=75, sigmaSpace=75),
    'k-means': Filter(kmean_segmentation, 'k-means', n_clusters=list(range(2, 11))),
}

NOISE_FUNCTIONS = {
    'no_noise': lambda image: {'no_noise': image},
    'gaussian_noise': Filter(partial(noise_with_skimage, mode='gaussian'), 'gaussian_noise', var=[0.01, 0.1]),
    'salt': Filter(partial(noise_with_skimage, mode='salt'), 'salt', amount=[0.01, 0.1, 0.2, 0.3]),
    'pepper': Filter(partial(noise_with_skimage, mode='pepper'), 'pepper', amount=[0.01, 0.1]),
    'salt_and_pepper': Filter(partial(noise_with_skimage, mode='s&p'), 'salt_and_pepper', amount=[0.01, 0.1]),
    'speckle': Filter(partial(noise_with_skimage, mode='speckle'), 'speckle', var=[0.01, 0.1]),
    'poisson': Filter(partial(noise_with_skimage, mode='poisson'), 'poisson'),
}


def apply_to_image(dict_of_functions: dict, cv_image, image_name: str) -> dict:
    generated_images = dict()

    for filter_name, filter_function in dict_of_functions.items():
        # generate new images based on filter function and defined parameters
        new_images = filter_function(cv_image)

        # update the dictionary of images
        if type(new_images) != dict:
            logging.error(f"Filter function {filter_name} did not return a dictionary!Returned {type(new_images)}")
        else:
            generated_images.update(new_images)

    new_images = {f"{image_name}_{key}": value for key, value in generated_images.items()}
    return new_images


def noise_and_filter_image(image_path: str | Path) -> int:
    new_images = dict()

    image_name = Path(image_path).stem
    image_color = cv.imread(image_path, cv.COLOR_BGR2RGB)
    image_bw = cv.cvtColor(image_color, cv.COLOR_BGR2GRAY)

    # Add noise to colored images and to black-white images:
    new_images.update(apply_to_image(NOISE_FUNCTIONS, image_color, image_name))
    new_images.update(apply_to_image(NOISE_FUNCTIONS, image_bw, f"{image_name}_bw"))

    filtered = dict()
    for name, image in new_images.items():
        filtered.update(apply_to_image(FILTER_FUNCTIONS, image, name))

    filtered[image_name] = image_color
    filtered[f"{image_name}_bw"] = image_bw

    for name, image in filtered.items():
        cv.imwrite(f"{GENERATED_IMAGES_DIR}/{name}.png", image)

    return len(filtered.keys())


def noise_and_filter_images(image_paths: list[str | Path]) -> int:
    # with multiprocessing.Pool(min(len(image_paths), multiprocessing.cpu_count())) as pool:
    with multiprocessing.Pool(6) as pool:
        results = pool.map(noise_and_filter_image, image_paths)

    return sum(results)
