from http import HTTPStatus


def test_read_main(test_app):
    response = test_app.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Welcome to FastAPI Clean Arch Starter API"}
