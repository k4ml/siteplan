
import pytest
from pytest_djangoapp import configure_djangoapp_plugin


def hook(settings):
    return settings


pytest_plugins = configure_djangoapp_plugin(
    settings="siteplan.settings",
)

@pytest.fixture
def user(user_model):
    user = user_model(email="user@xxx.com", username="user")
    user.save()
    return user
