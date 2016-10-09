import requests
from django.conf import settings

def send_mg_email(subject, body, from_name=False, to_email=[]):
	mg_url = "https://api.mailgun.net/v3/%s/messages" % (settings.MG_DOMAIN)
	mg_key = settings.MG_API_KEY
	if from_name:
		from_email = "%s <notifications@%s>" % (from_name, settings.MG_DOMAIN)

	#', '.join("{!s} <{!s}>".format(key,val) for (key,val) in to_email.items())
	msg_data = {
		"from": from_email,
		"to": ', '.join(to_email),
		"subject": subject,
		"html": body
	}
	requests.post(mg_url, auth=("api", mg_key), data=msg_data)

