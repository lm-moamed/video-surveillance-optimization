from django.db import models
from django.conf import settings
from .whatsapp_send_record import send_whatsapp_message



class Userinfo(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone_number = models.CharField(max_length=15)
	status = models.BooleanField(default=False)
	userid = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self):
		return(f"{self.first_name} {self.last_name}")


class Stream(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	url = models.CharField(max_length=150)
	label = models.CharField(max_length=50)
	period = models.IntegerField(default=1)
	status = models.BooleanField(default=False)
	is_processing = models.BooleanField(default=False)
	userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.url} "


class Record(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	path = models.CharField(max_length=150)
	streamid = models.ForeignKey(Stream, on_delete=models.SET(None))
	userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.path}".split("\\")[-1]

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		# send_whatsapp_message(self)
