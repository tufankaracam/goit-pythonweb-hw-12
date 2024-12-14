from unittest.mock import patch
from tests.conftest import test_user
from src.database.models import UserRole


def test_get_me(client, get_token):
    """
    Test retrieving the current authenticated user's information.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data contains the user's username, email, and avatar.
    """
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@patch("src.services.upload_file.UploadFileService.upload_file")
def test_update_avatar_user(mock_upload_file, client, get_token):
    """
    Test updating the avatar for the current authenticated user.

    Args:
        mock_upload_file (Mock): Mock for the upload_file method in UploadFileService.
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data contains the updated avatar URL.
        - The upload_file method is called once with the correct parameters.
    """
    fake_url = "http://example.com/avatar.jpg"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_token}"}
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["avatar"] == fake_url

    mock_upload_file.assert_called_once()


@patch("src.services.users.UserService.update_user_role")
def test_update_user_role(mock_update_user_role, client, get_token):
    """
    Test updating another user's role.

    Args:
        mock_update_user_role (Mock): Mock for the update_user_role method in UserService.
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data matches the new role.
        - The update_user_role method is called once with the correct parameters.
    """
    new_role = UserRole.ADMIN
    mock_update_user_role.return_value = new_role

    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.patch(
        "/api/users/update-role",
        headers=headers,
        params={"user_id": 2, "new_role": "admin"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data == new_role

    mock_update_user_role.assert_called_once_with(2, "admin")


def test_update_own_role(client, get_token):
    """
    Test attempting to update the authenticated user's own role.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 406.
        - The error message indicates that the user cannot update their own role.
    """
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.patch(
        "/api/users/update-role",
        headers=headers,
        params={"user_id": 1, "new_role": "admin"},
    )

    assert response.status_code == 406, response.text
    data = response.json()
    assert data["detail"] == "Admin can not change self role"
