from django.core.management.base import BaseCommand
from django.core.cache import cache

from logger import logger


class Command(BaseCommand):
    help = 'Clear all cache'

    def handle(self, *args, **kwargs):
        cache.clear()
        logger.info('Cache cleared')
