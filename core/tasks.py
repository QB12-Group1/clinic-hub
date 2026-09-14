import os

from celery import Task, shared_task
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


class SendSMSTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        kwargs = kwargs or {}

        fallback_email = kwargs.get("fallback_email") or (args[3] if len(args) > 3 else None)
        fallback_subject = kwargs.get("fallback_subject") or (args[4] if len(args) > 4 else None)
        fallback_message = kwargs.get("fallback_message_text") or (args[5] if len(args) > 5 else None)

        if fallback_email:
            subject = fallback_subject or str(_("Your Verification Code"))
            message = fallback_message or str(
                _("Your verification code could not be sent via SMS at this time. Please use this email instead.")
            )
            send_email_task.delay(
                subject=subject,
                message=message,
                to_email=fallback_email,
            )

        super().on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    rate_limit="30/m",
    base=SendSMSTask,
)
def send_sms_task(
    self,
    phone_number: str,
    message_text: str,
    fallback_email: str | None = None,
    fallback_subject: str | None = None,
    fallback_message_text: str | None = None,
):
    api_key = os.environ.get("KAVENEGAR_API_KEY")
    api = KavenegarAPI(api_key)
    params = {
        "sender": "2000660110",
        "receptor": phone_number,
        "message": _(message_text),
    }
    api.sms_send(params)
