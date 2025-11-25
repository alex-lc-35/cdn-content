""" processor/__init__.py """

from .default_processor import DefaultProcessor
from .markdown_processor import MarkdownProcessor
from .image_processor import ImageProcessor
from .ods_processor import OdsProcessor

PROCESSORS = {
    "png": ImageProcessor(),
    "jpg": ImageProcessor(),
    "jpeg": ImageProcessor(),
    "webp": ImageProcessor(),
    "md": MarkdownProcessor(),
    "html": DefaultProcessor(),
    "htm": DefaultProcessor(),
    "ods": OdsProcessor(),
}

def get_processor_for(ext):
    return PROCESSORS.get(ext.lower())
