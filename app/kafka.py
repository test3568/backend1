from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from django.conf import settings

from app.typing_models import PolygonKafkaTaskData, PolygonChannelMessage
from app.utils import send_message_to_all
from logger import logger


class Kafka:
    def __init__(self):
        self.topic = settings.KAFKA_PRODUCER_TOPIC
        self.retries = []

        self.producer = Producer({
            'bootstrap.servers': settings.KAFKA_SERVER,
            'acks': 'all'
        })

        self.admin = AdminClient({
            "bootstrap.servers": settings.KAFKA_SERVER,
        })
        topic_list = [
            NewTopic("polygons", 1, 1),
            NewTopic("polygons_back", 1, 1)
        ]
        self.admin.create_topics(topic_list)

    @staticmethod
    def delivery_callback(err, msg):
        if err:
            logger.error(f"Message failed delivery to kafka: {err}")
            send_message_to_all(PolygonChannelMessage(
                type=PolygonChannelMessage.Types.new_polygon_status,
                uuid=msg["uuid"],
                status=PolygonChannelMessage.Statuses.error_send_for_intersection
            ))
        else:
            logger.debug(f"Produced event to topic {msg.topic()}: key = {msg.key()} value = {msg.value()}")

    def add_polygon(self, message: PolygonKafkaTaskData):
        self.producer.produce(self.topic, message.model_dump_json(), callback=self.delivery_callback)
        self.producer.poll(10000)
        self.producer.flush()


kafka = Kafka()
