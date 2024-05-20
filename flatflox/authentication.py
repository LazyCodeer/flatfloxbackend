from firebase_admin import auth
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions
import firebase_admin
from firebase_admin import credentials
from rest_framework.response import Response
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

FIREBASE_CREDENTIALS = settings.GOOGLE_CLOUD_CREDENTIALS
cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.debug('Authorization header not found')
            return None

        id_token = auth_header.split(' ').pop()
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            user, _ = User.objects.get_or_create(username=uid)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid Firebase ID token.')

        return (user, None)