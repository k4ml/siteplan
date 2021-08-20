

A new way to Django development. Start small, grow big.

## Quickstart
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
siteplan --app app:app run -b 127.0.0.1:9001
```
