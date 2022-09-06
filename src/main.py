import logging
import os
from pathlib import Path

import cv2 as cv

import Config
import ImageFiltering
from SiteGeneration import WebPage

IMAGES = [str(image.absolute()) for image in Config.IMAGES_DIR.iterdir()]


def save_images(images: dict[str, str], path: str | Path):
    for name, image in images.items():
        cv.imwrite(f"{path}/{name}.png", image)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Cleanup: {Config.STATIC_DIR / 'generated'}")

    if not os.path.exists(Config.STATIC_DIR / "generated"):
        os.mkdir(Config.STATIC_DIR / "generated")

    for file in (Config.STATIC_DIR / "generated").iterdir():
        os.remove(file)

    logging.info(f"Images used: {[Path(image).name for image in IMAGES]}")

    logging.info(f"Generating noised and filtered images with {len(IMAGES)} images, "
                 f"{len(ImageFiltering.FILTER_FUNCTIONS)} filters and {len(ImageFiltering.NOISE_FUNCTIONS)} "
                 f"noise generators.")
    filtered_images = ImageFiltering.noise_and_filters_images(IMAGES)

    logging.info(f"Generated: {len(list(filtered_images.keys()))} images.")

    logging.info(f"Saving images...")
    save_images(filtered_images, Config.STATIC_DIR / "generated")

    logging.info(f"Done!")

    logging.info(f"Generating web page...")
    web_page = WebPage(images=IMAGES,
                       noises=ImageFiltering.NOISE_FUNCTIONS.keys(),
                       filters=ImageFiltering.FILTER_FUNCTIONS.keys())
    index_page = web_page.generate()
    logging.info(f"Done! -> {index_page}")

    # logging.info(f"Plotting some images.")
    # keys = list(filtered_images.keys())
    # random.shuffle(keys)
    #
    # for i in range(1, 3):
    #     plt.subplot(120+i)
    #     plt.imshow(cv.cvtColor(filtered_images[keys[i]], cv.COLOR_BGR2RGB))
    #     plt.title(keys[i])
    #     plt.xticks([]), plt.yticks([])
    #
    # plt.show()
