from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Yeh line check karegi ki user ne jo dala hai wo username se match karta hai YA email se
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Agar kisi wajah se ek hi email par multiple users hain (waise aisa hota nahi hai)
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
        
        # Password check karne ke liye
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None