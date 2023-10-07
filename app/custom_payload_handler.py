from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings

def custom_payload_handler(user):
    """
    Custom payload handler to include user_id in the response
    """
    payload = api_settings.JWT_PAYLOAD_HANDLER(user)
    payload['user_id'] = user.id
    payload['username'] = user.username  # or any other field you need
    return payload

# Set the payload handler in TOKEN_AUTHENTICATION settings
TOKEN_AUTHENTICATION = {
    'TOKEN_PAYLOAD_HANDLER': 'app.custom_payload_handler'
}
