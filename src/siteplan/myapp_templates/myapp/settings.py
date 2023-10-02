
from siteplan.settings import *

ROOT_URLCONF = "myapp.urls"

INSTALLED_APPS = [
    "myapp"
] + INSTALLED_APPS

LARAVELMIX_MANIFEST_DIRECTORY = os.path.join(BASE_DIR, "myapp/static/mix/build")