import os
import django
import datetime
import json

os.environ["DJANGO_SETTINGS_MODULE"] = "siteplan.settings"
django.setup()

from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(email="admin@siteplan.co").exists():
    User.objects.create_superuser(email="admin@siteplan.co", password="picard data")
