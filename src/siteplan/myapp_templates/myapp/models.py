
from django.db import models

class MyPerson(models.Model):
    name = models.CharField(max_length=255)
