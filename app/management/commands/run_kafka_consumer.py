from django.core.management.base import BaseCommand

from app.kafka_consumer import consume_messages
from logger import logger


class Command(BaseCommand):
    help = 'Run the Kafka consumer'

    def handle(self, *args, **options):
        logger.info("Starting Kafka consumer...")
        consume_messages()
