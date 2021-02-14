from celery import shared_task
from django.conf import settings
from . import models
import sendgrid
import os
from sendgrid.helpers.mail import *

@shared_task
def send_mails(id):
    form = models.Form.objects.get(pk=id)
    students = form.team.students.all()
    emails = list(students.values_list('admin__username',flat=True))
    sg = sendgrid.SendGridAPIClient(api_key='')
    subject = "SPEsys - Email Reminder for Incomplete Form"
    recipients = []

    for i in emails:
        recipients.append({'email':i})
    data = {
        "personalizations": [
            {
            "to": recipients,
            "subject": subject
            }
        ],
        "from": {
            "email": settings.FROM_EMAIL
        },
        "content": [
            {
            "type": "text/plain",
            "value": f" You have {td_format(form.expiry_date - form.created_on)} days left to submit your form.\n"
                     f"Log in to your portal at www.spesys.com to submit your evaluation form now."
            }
        ]
        }
    response = sg.client.mail.send.post(request_body=data)
    print(response.status_code)


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('day',         60*60*24),
        ('hour',        60*60),
        ('minute',      60),
    ]

    strings=[]
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value , seconds = divmod(seconds, period_seconds)
            has_s = 's' if period_value > 1 else ''
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)
