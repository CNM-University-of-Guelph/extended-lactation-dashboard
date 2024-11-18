from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/data-upload/(?P<user_id>\d+)/$', consumers.DataUploadConsumer.as_asgi()),
]
