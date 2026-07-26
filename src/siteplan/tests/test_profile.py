import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.mark.django_db
def test_profile_update_renders_django_umin_form():
    user = get_user_model().objects.create_user(
        email="profile@example.com", password="OldPass123!", name="Old Name"
    )
    client = Client()
    client.force_login(user)

    response = client.get("/profile/")
    assert response.status_code == 200
    body = response.content.decode()
    # django_umin form_page renders the title; form_card renders the fields.
    assert "Update Profile" in body
    assert 'name="name"' in body
    assert 'name="email"' in body
    assert 'type="email"' in body
    assert "/password/change/" in body


@pytest.mark.django_db
def test_password_change_renders_django_umin_form():
    user = get_user_model().objects.create_user(
        email="pwchange@example.com", password="OldPass123!"
    )
    client = Client()
    client.force_login(user)

    response = client.get("/password/change/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Change Password" in body
    assert 'name="old_password"' in body
    assert 'name="new_password1"' in body
    assert 'name="new_password2"' in body
    assert 'type="password"' in body


@pytest.mark.django_db
def test_profile_update_persists_and_redirects():
    user = get_user_model().objects.create_user(
        email="update@example.com", password="OldPass123!", name="Old Name"
    )
    client = Client()
    client.force_login(user)

    response = client.post(
        "/profile/", {"name": "New Name", "email": "updated@example.com"}
    )
    assert response.status_code == 302
    assert response.url == "/profile/"
    user.refresh_from_db()
    assert user.name == "New Name"
    assert user.email == "updated@example.com"


@pytest.mark.django_db
def test_password_change_persists_and_keeps_session():
    user = get_user_model().objects.create_user(
        email="pw@example.com", password="OldPass123!"
    )
    client = Client()
    client.force_login(user)

    response = client.post(
        "/password/change/",
        {
            "old_password": "OldPass123!",
            "new_password1": "Br@vo2026xyZ#",
            "new_password2": "Br@vo2026xyZ#",
        },
    )
    assert response.status_code == 302
    assert response.url == "/profile/"
    user.refresh_from_db()
    assert user.check_password("Br@vo2026xyZ#")
    # update_session_auth_hash should keep the user signed in.
    assert client.get("/profile/").status_code == 200
