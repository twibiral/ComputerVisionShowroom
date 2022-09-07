import logging
import os
from multiprocessing import Pool, cpu_count
from pathlib import Path

import cv2 as cv

import Config
import DynamicFilter
import ImageFiltering
from SiteGeneration import WebPage

IMAGES = [str(image.absolute()) for image in Config.IMAGES_DIR.iterdir()][15:16]


def save_images(images: dict[str, str], path: str | Path):
    with Pool(cpu_count()) as pool:
        result = pool.starmap_async(cv.imwrite, [(f"{path}/{name}.png", image) for name, image in images.items()])
        result.wait()
    pool.join()


def preparatory_clean_up():
    if not os.path.exists(Config.STATIC_DIR / "generated"):
        os.mkdir(Config.STATIC_DIR / "generated")
    for file in (Config.STATIC_DIR / "generated").iterdir():
        os.remove(file)


def get_all_filter_strings_for(func_dict):
    filter_strings = list()
    for filter_name, filter_function in func_dict.items():
        if type(filter_function) == DynamicFilter.Filter:
            filter_strings.extend(filter_function.get_filter_strings())

        else:
            filter_strings.append(filter_name)

    return filter_strings


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    preparatory_clean_up()

    logging.info(f"Generating noised and filtered images with {len(IMAGES)} images, "
                 f"{len(ImageFiltering.FILTER_FUNCTIONS)} filters and {len(ImageFiltering.NOISE_FUNCTIONS)} "
                 f"noise generators.")
    filtered_images = ImageFiltering.noise_and_filter_images(IMAGES)
    logging.info(f"Generated: {len(list(filtered_images.keys()))} images.")

    logging.info(f"Saving images...")
    save_images(filtered_images, Config.STATIC_DIR / "generated")

    logging.info(f"Generating web page...")
    web_page = WebPage(images=IMAGES,
                       noises=get_all_filter_strings_for(ImageFiltering.NOISE_FUNCTIONS),
                       filters=get_all_filter_strings_for(ImageFiltering.FILTER_FUNCTIONS))
    index_page = web_page.generate()
    logging.info(f"Done! -> {index_page}")
