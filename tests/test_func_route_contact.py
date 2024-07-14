


def test_creat_contact_success(client, get_token):

    new_contact = {
        'firstname': 'Joe',
        'lastname': 'test',
        'email': 'test@email.ua',
        'phone_number': '654321',
        'born_date': '2019-01-01',
        'description': 'my test contact'
    }

    expected_contact = {
        'firstname': 'Joe',
        'lastname': 'test',
        'email': 'test@email.ua',
        'phone_number': '654321',
        'born_date': '2019-01-01',
        'description': 'my test contact'
    }

    headers = {
        'Authorization': f'Bearer {get_token}'
    }

    responce = client.post('/api/contacts/', json=new_contact, headers=headers)

    assert responce.status_code == 200
    assert responce.json() == expected_contact


def test_create_contact_missing_fields(client, get_token):
    new_contact = {
        'firstname': 'Alice',
        'lastname': 'MissingFields',
        # Missing 'email', 'phone_number', 'born_date', 'description' fields
    }

    headers = {
        'Authorization': f'Bearer {get_token}'
    }

    response = client.post('/api/contacts/', json=new_contact, headers=headers)

    assert response.status_code == 422  



    

