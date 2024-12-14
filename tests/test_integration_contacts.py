def test_create_contact(client, get_token):
    """
    Test the creation of a new contact.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 201.
        - The returned data contains the correct contact details.
        - The response includes an "id" field.
    """
    response = client.post(
        "/api/contacts",
        json={
            "firstname": "test_contact",
            "lastname": "string",
            "email": "string@string.com",
            "phone": "string",
            "birthdate": "2024-12-13T04:31:17.916Z",
            "additional": "string",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["firstname"] == "test_contact"
    assert data["lastname"] == "string"
    assert data["email"] == "string@string.com"
    assert data["phone"] == "string"
    assert data["additional"] == "string"
    assert "id" in data


def test_get_contact(client, get_token):
    """
    Test retrieving a single contact by ID.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data contains the correct contact details.
        - The response includes an "id" field.
    """
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "test_contact"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    """
    Test retrieving a non-existent contact.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 404.
        - The error message indicates that the contact was not found.
    """
    response = client.get(
        "/api/contacts/99", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    """
    Test retrieving a list of contacts.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data is a list.
        - The list contains valid contact data.
    """
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["firstname"] == "test_contact"
    assert "id" in data[0]


def test_update_contact(client, get_token):
    """
    Test updating an existing contact.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data reflects the updated contact details.
        - The response includes an "id" field.
    """
    response = client.put(
        "/api/contacts/1",
        json={
            "firstname": "test_contact_1",
            "lastname": "string",
            "email": "string@string.com",
            "phone": "string",
            "birthdate": "2024-12-13T04:31:17.916Z",
            "additional": "string",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "test_contact_1"
    assert "id" in data


def test_update_contact_not_found(client, get_token):
    """
    Test updating a non-existent contact.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 404.
        - The error message indicates that the contact was not found.
    """
    response = client.put(
        "/api/contacts/2",
        json={
            "firstname": "string",
            "lastname": "string",
            "email": "string@string.com",
            "phone": "string",
            "birthdate": "2024-12-13T04:31:17.916Z",
            "additional": "string",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    """
    Test deleting an existing contact.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 200.
        - The returned data contains the deleted contact details.
    """
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["firstname"] == "test_contact_1"
    assert "id" in data


def test_repeat_delete_contact(client, get_token):
    """
    Test deleting a contact that has already been deleted.

    Args:
        client (TestClient): The test client for sending HTTP requests.
        get_token (str): A valid authentication token.

    Asserts:
        - Response status code is 404.
        - The error message indicates that the contact was not found.
    """
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
