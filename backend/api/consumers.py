from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

class ProgressConsumer(JsonWebsocketConsumer):
    def connect(self):
        # Get user ID from scope
        user = self.scope["user"]
        if not user.is_authenticated:
            self.close()
            return
            
        # Add to user-specific group
        self.group_name = f"user_{user.id}_progress"
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Remove from group
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )

    # This must match the "type" in send_progress_message
    def progress_message(self, event):
        # Send message to WebSocket
        self.send_json(event["message"])
