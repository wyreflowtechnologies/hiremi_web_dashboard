from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import Register

class RegisterAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Register.objects.get(email=email)
            if check_password(password, user.password):
                return user
        except Register.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Register.objects.get(pk=user_id)
        except Register.DoesNotExist:
            return None
