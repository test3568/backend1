import sys

import ujson
from confluent_kafka import Consumer, TopicPartition, KafkaError
from django.conf import settings
from django.db import transaction

from app.typing_models import PolygonChannelMessage
from app.utils import send_message_to_all
from logger import logger
from polygons.models import Polygon, PolygonToUser

consumer_conf = {
    'bootstrap.servers': settings.KAFKA_SERVER,
    'group.id': 'polygons_back_consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'isolation.level': 'read_committed'
}

consumer = Consumer(consumer_conf)


def consume_messages():
    consumer.assign([TopicPartition(settings.KAFKA_CONSUMER_TOPIC, 0)])
    logger.info(f"Consumer starter")
    try:
        while True:
            msg = consumer.poll(timeout=1)

            if msg is None:
                continue

            error = msg.error()
            if error:
                logger.error(f"Kafka poll error: {error}")
                if error.code() == KafkaError.NOT_COORDINATOR:
                    logger.warning(f"NOT_COORDINATOR error code, exiting")
                    sys.exit(-1)
                continue

            # noinspection PyArgumentList
            msg_value = msg.value()
            try:
                message = ujson.loads(msg_value.decode('utf-8'))
            except ujson.JSONDecodeError:
                logger.error(f"Message JSONDecodeError: {msg_value}")
                continue

            try:
                logger.debug(f"Received message: {message}")
                if message["editing_polygon_id"] is None:
                    send_message_to_all(PolygonChannelMessage(
                        type=PolygonChannelMessage.Types.new_polygon_status,
                        uuid=message['request_uuid'],
                        status=PolygonChannelMessage.Statuses.no_intersections
                    ))
                    message = process_new_polygon(message)
                else:
                    send_message_to_all(PolygonChannelMessage(
                        type=PolygonChannelMessage.Types.edit_polygon_status,
                        uuid=message['request_uuid'],
                        status=PolygonChannelMessage.Statuses.no_intersections
                    ))
                    message = process_editing_polygon(message)
            except Exception:
                logger.exception(f'Unknown error with task: {message}')
                try:
                    send_message_to_all(PolygonChannelMessage(
                        type=PolygonChannelMessage.Types.new_polygon_status,
                        uuid=message['request_uuid'],
                        status=PolygonChannelMessage.Statuses.error_commit
                    ))
                except Exception:
                    logger.exception(f'Can\'t send websocket callback with error')
            finally:
                consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        logger.warning("Consumer interrupted.")
    finally:
        consumer.close()


def geojson_from_message(message) -> dict:
    return {
        "type": "Feature",
        "geometry": message['polygon'],
        "id": message['intersection_id'],
        "properties": {
            "name": message['name'],
            "antimeridian_crossing": message['antimeridian_crossing'],
            "edited_polygon_id": message['editing_polygon_id'],
            "intersection_polygon_ids": message['intersection_polygon_ids']
        }
    }


def check_message_errors(message, callback_type) -> bool:
    if message['error']:
        send_message_to_all(PolygonChannelMessage(
            type=callback_type,
            uuid=message['request_uuid'],
            status=PolygonChannelMessage.Statuses.error_intersections_check
        ))
        return False
    if message['intersection_polygon_ids']:
        geojson = geojson_from_message(message)
        send_message_to_all(PolygonChannelMessage(
            type=callback_type,
            uuid=message['request_uuid'],
            status=PolygonChannelMessage.Statuses.error_intersections_exist,
            intersection_polygon_ids=message['intersection_polygon_ids'],
            polygon_intersection=geojson
        ))
        return False
    return True


def process_new_polygon(message):
    status = check_message_errors(message, PolygonChannelMessage.Types.new_polygon_status)
    if not status:
        return message
    polygon_dump = ujson.dumps(message['polygon'])
    p = Polygon(name=message['name'], polygon=polygon_dump, antimeridian_crossing=message['antimeridian_crossing'])
    ptu = PolygonToUser(polygon=p, user_id=message['user_id'], by_user_id=None)
    with transaction.atomic():
        p.save()
        ptu.save()
    geojson = {
            "type": "Feature",
            "geometry": message['polygon'],
            "id": p.id,
            "properties": {
                "name": p.name,
                "antimeridian_crossing": p.antimeridian_crossing
            }
        }
    send_message_to_all(PolygonChannelMessage(
        type=PolygonChannelMessage.Types.new_polygon_status,
        uuid=message['request_uuid'],
        status=PolygonChannelMessage.Statuses.success,
        polygon=geojson,
    ))
    return message


def process_editing_polygon(message):
    status = check_message_errors(message, PolygonChannelMessage.Types.edit_polygon_status)
    if not status:
        return message
    polygon_dump = ujson.dumps(message['polygon'])
    p = Polygon.objects.get(pk=message['editing_polygon_id'])
    p.polygon = polygon_dump
    p.name = message['name']
    p.antimeridian_crossing = message['antimeridian_crossing']
    p.save()
    geojson = {
            "type": "Feature",
            "geometry": message['polygon'],
            "id": p.id,
            "properties": {
                "name": p.name,
                "antimeridian_crossing": p.antimeridian_crossing
            }
        }
    send_message_to_all(PolygonChannelMessage(
        type=PolygonChannelMessage.Types.edit_polygon_status,
        uuid=message['request_uuid'],
        status=PolygonChannelMessage.Statuses.success,
        polygon=geojson,
        editing_polygon_id=message['editing_polygon_id']
    ))
    return message
