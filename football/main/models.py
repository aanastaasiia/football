from django.db import models

class Users(models.Model):
    username = models.CharField(max_length = 20, unique=True)
    password = models.CharField(max_length = 20)
    admin = models.BooleanField(default = False)
    cookie = models.JSONField(blank = True)

