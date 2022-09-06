import os
from pathlib import Path

import jinja2

import Config


__INDEX__ = "index.html"


class WebPage:
    def __init__(self, images: list[str], noises: list[str], filters: list[str]):
        self.clean_up()
        self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader(Config.TEMPLATE_DIR))
        self.images = [Path(image).stem for image in images]
        self.noises = noises
        self.filters = filters

    def clean_up(self):
        for file in Config.STATIC_DIR.iterdir():
            if os.path.isfile(file):
                os.remove(file)

    def generate_index(self):
        index_template = self.environment.get_template(__INDEX__)
        index_str = index_template.render(images=self.images, noises=self.noises, filters=self.filters)
        p = Config.STATIC_DIR / __INDEX__

        with open(p, "x") as index_file:
            index_file.write(index_str)

    def generate(self):
        self.generate_index()
        return str(Config.STATIC_DIR / __INDEX__).replace("\\", "/")
