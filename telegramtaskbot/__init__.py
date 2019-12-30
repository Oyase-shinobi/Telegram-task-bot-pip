import logging

from .Bot import TelegramTaskBot
from .Tasks.GenericTask import GenericTask
from .Tasks.Task import Task
from .Tasks.UrlTask import UrlTask

logging.getLogger(__name__).addHandler(logging.NullHandler())
