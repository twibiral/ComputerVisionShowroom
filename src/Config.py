import os
from pathlib import Path

SOURCE_DIR = Path(os.path.realpath(__file__)).parent
TEMPLATE_DIR = SOURCE_DIR / "templates"

STATIC_DIR = SOURCE_DIR.parent / "static"
IMAGES_DIR = STATIC_DIR / "images"
