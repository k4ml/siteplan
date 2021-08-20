

A new way to Django development. Start small, grow big.

## Quickstart
Create the app directory:-

```
mkdir myapp && cd myapp
python3 -mvenv venv
venv/bin/pip install siteplan
```

Add the following code to `app.py`:-

```
from siteplan import App, run
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello world")

from django.urls import path
urlpatterns = [
    path("test/", index),
]

conf = {}
app = App(conf, urls=urlpatterns)

if __name__ == "__main__":
    run(app)

```

Then run it with `siteplan`:-

```
venv/bin/siteplan --app app:app run -b 127.0.0.1:9001
```
