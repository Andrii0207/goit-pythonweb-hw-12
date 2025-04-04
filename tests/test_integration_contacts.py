from datetime import datetime, timedelta

contact_data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivan.ivanov@example.com",
        "phone": "123456789",
        "birth_date": "2020-01-01"
    }


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == "Ivan"
    assert data["last_name"] == "Ivanov"
    assert data["email"] == "ivan.ivanov@example.com"
    assert "id" in data

def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Ivan"
    assert data["last_name"] == "Ivanov"
    assert data["email"] == "ivan.ivanov@example.com"
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]

def test_update_contact(client, get_token):
    contact_update_data = {
        "first_name": "Ivan Updated",
        "last_name": "Ivanov last name",
        "email": "ivan.updated@example.com",
        "phone": "987654321",
        "birth_date": "2020-01-01"
    }
    response = client.put(
        "/api/contacts/1",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Ivan Updated"
    assert data["email"] == "ivan.updated@example.com"
    assert "id" in data

def test_update_contact_not_found(client, get_token):
    contact_update_data = {
        "first_name": "Nonexistent Contact",
        "last_name": "Ivan last name",
        "email": "nonexistent@example.com",
        "phone": "000000000",
        "birth_date": "2020-01-01"
    }
    response = client.put(
        "/api/contacts/999",
        json=contact_update_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Ivan Updated"
    assert "id" in data

def test_delete_contact_not_found(client, get_token):
    response = client.delete(
        "/api/contacts/999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

def test_get_upcoming_birthdays(client, get_token):
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    contact = {**contact_data, "birth_date":tomorrow_str, "email":"birth@gmail.com"}
    res = client.post("/api/contacts", json=contact, headers={"Authorization": f"Bearer {get_token}"})
    print(res.json())

    response = client.get("/api/contacts/birthdays", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "birth_date" in data[0]