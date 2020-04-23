from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.
# User = get_user_model()

class users(AbstractUser):
	pass
	mobileno = models.CharField(max_length=10)

class events(models.Model):
	name = models.CharField(max_length=50)
	orgname = models.CharField(max_length=50)
	address = models.CharField(max_length=100, blank=True)
	capacity = models.IntegerField()
	price = models.IntegerField()
	event_type = models.CharField(max_length=20)
	contact = models.CharField(max_length=10)
	event_date = models.DateTimeField()
	lat = models.FloatField(null=True)
	lng = models.FloatField(null=True)
	org = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	photo = models.ImageField(upload_to='events/')

class event_types(models.Model):
	etype = models.CharField(max_length=50)

class event_registration(models.Model):
	fullname = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	mobileno = models.CharField(max_length=10)
	usr = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	evnt = models.ForeignKey(events, on_delete=models.CASCADE,null=True)