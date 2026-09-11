from django.contrib.auth import get_user_model
from django.forms.models import ModelForm

User = get_user_model()


class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "email")
