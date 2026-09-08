import os

from celery import shared_task
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from kavenegar import KavenegarAPI

from core import settings


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    rate_limit="50/m",
)
def send_email_task(self, subject: str, message: str, to_email: str):
    send_mail(_(subject), _(message), settings.DEFAULT_FROM_EMAIL, [to_email])


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    rate_limit="30/m",
)
def send_sms_task(self, phone_number: str, message_text: str):
    api_key = os.environ.get("KAVENEGAR_API_KEY")
    api = KavenegarAPI(api_key)
    params = {
        "sender": "2000660110",
        "receptor": phone_number,
        "message": _(message_text),
    }
    api.sms_send(params)
