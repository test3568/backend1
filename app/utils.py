from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer
from django.conf import settings

from app.typing_models import PolygonChannelMessage


def send_message_to_all(message: PolygonChannelMessage) -> None:
    channel_layer: RedisChannelLayer | None = get_channel_layer()
    msg = {
        "type": "group_message",
        "message": message.model_dump(mode='json')
    }
    async_to_sync(channel_layer.group_send)(
        settings.CHANNEL_GROUP_NAME,
        msg
    )
