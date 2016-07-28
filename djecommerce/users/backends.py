from users.models import EcUser as User
from django.contrib.auth.backends import ModelBackend

class EmailAuthBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        try:
            try:
                user = User.objects.get(email=username)
            except:
                user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None