from fastapi import status
from test.conftest import mock_landlord_schema, base_url

auth_url_base = f'{base_url}/auth'

def test_register_landlord_returns_201(client, mock_landlord_schema):
    landlord_schema = mock_landlord_schema

    response = client.post(f'{auth_url_base}/register/landlord', json=landlord_schema.model_dump())
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED

    assert data['first_name']  == landlord_schema.first_name
    assert data['email'] == landlord_schema.email
    assert data['last_name'] == landlord_schema.last_name
    assert data['phone_no'] == landlord_schema.phone_no

    assert 'id' in data
    assert 'password' not in data



def test_register_duplicate_email_returns_400(client, add_landlord_to_db, mock_landlord_schema):
    l_schema = mock_landlord_schema
    response = client.post(f'{auth_url_base}/register/landlord', json=l_schema.model_dump())
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert data['detail'] == f'User: {add_landlord_to_db.email} already exists'



def test_login_user_returns_200(client, add_landlord_to_db, mock_landlord_schema):
    l_schema = mock_landlord_schema
    payload = {
        'username': l_schema.email,
        'password': l_schema.password
    }
    response = client.post(f'{auth_url_base}/login', data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert 'access_token' in data
    assert data['token_type'] == 'bearer'



def test_login_user_email_invalid_returns_401(client, mock_landlord_schema):
    l_schema  = mock_landlord_schema

    payload = {
        'username': l_schema.email,
        'password': l_schema.password
    }
    response = client.post(f'{auth_url_base}/login', data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert not 'access_token' in data
    assert not 'token_type' in data
    assert data['detail'] == 'Invalid email or password.'


def test_login_user_password_invalid_returns_401(client, add_landlord_to_db):
    payload = {
        'username': add_landlord_to_db.email,
        'password': 'Donald2345'
    }
    response = client.post(f'{auth_url_base}/login', data=payload)
    data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert not 'access_token' in data
    assert not 'token_type' in data
    assert data['detail'] == 'Invalid email or password.'


def test_register_tenant_returns_201(client, mock_tenant_schema, add_lodge_to_db):
    t_payload = mock_tenant_schema.model_dump()

    response = client.post(f'{auth_url_base}/register/tenant', json=t_payload)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data['tenant_type'] == mock_tenant_schema.tenant_info.tenant_type
    assert data['emergency_contact_name'] == mock_tenant_schema.tenant_info.emergency_contact_name
    assert data['emergency_contact_phone_no'] == mock_tenant_schema.tenant_info.emergency_contact_phone_no
    assert 'id' in data
    assert 'user_id' in data
    assert data['user'] != {}


def test_register_tenant_lodge_not_exist_returns_404(client, mock_tenant_schema):
    t_payload = mock_tenant_schema.model_dump()

    response = client.post(f'{auth_url_base}/register/tenant', json=t_payload)
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['detail'] == 'Lodge could not be found'


