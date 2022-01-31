import json

import pytest


@pytest.mark.parametrize(
    "age",
    (
            "",
            "abc",
            "-12",
            999,
            "56",
            20,
    )
)
def test_user_age(client, auth, age):
    auth.login()

    response = client.get("/user/age")
    r_dict = json.loads(response.data)

    assert response.status_code == 403
    assert "age not set" in r_dict['status']

    response = client.post(f"/user/age?age={age}")
    r_dict = json.loads(response.data)
    valid_ages = [str(x) for x in range(1, 101)]

    if age == "" or age is None:
        assert response.status_code == 403
        assert "age is required" in r_dict['status']
    elif str(age).lstrip("-").isnumeric() and str(age) not in valid_ages:
        assert response.status_code == 403
        assert "age must be between 1 and 100" in r_dict['status']
    elif not str(age).isnumeric():
        assert response.status_code == 403
        assert "age must be a positive integer number" in r_dict['status']
    else:
        assert response.status_code == 200
        assert "age successfully set" in r_dict['status']

        response = client.get("/user/age")
        r_dict = json.loads(response.data)

        assert response.status_code == 200
        assert "age successfully retrieved" in r_dict['status']
