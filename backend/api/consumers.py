from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

class ProgressConsumer(JsonWebsocketConsumer):
    def connect(self):
        logger.info(f"WebSocket connection attempt from user {self.scope['user']}")
        user = self.scope["user"]
        
        if not user.is_authenticated:
            logger.error("Unauthenticated WebSocket connection attempt")
            self.close()
            return
            
        self.group_name = f"user_{user.id}_progress"
        logger.info(f"Adding user to group: {self.group_name}")
        
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        logger.info("WebSocket connection accepted")

    def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    # This must match the "type" in send_progress_message
    def progress_message(self, event):
        # Send message to WebSocket
        self.send_json(event["message"])
