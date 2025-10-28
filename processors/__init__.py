""" processor/__init__.py """

from .default_processor import DefaultProcessor
from .markdown_processor import MarkdownProcessor
from .image_processor import ImageProcessor

PROCESSORS = {
    "png": ImageProcessor(),
    "jpg": ImageProcessor(),
    "jpeg": ImageProcessor(),
    "webp": ImageProcessor(),
    "md": MarkdownProcessor(),
    "html": DefaultProcessor(),
    "htm": DefaultProcessor(),
}

def get_processor_for(ext):
    return PROCESSORS.get(ext.lower())
