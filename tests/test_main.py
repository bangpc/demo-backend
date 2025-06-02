import io
import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from main import app

# Update test client initialization
client = TestClient(app)

@pytest.fixture
def mock_s3_upload():
    with patch("main.s3_client.upload_fileobj") as mock_upload:
        yield mock_upload

@pytest.fixture
def mock_mongo_insert_find():
    with patch("main.images_collection.insert_one") as mock_insert, \
         patch("main.images_collection.find") as mock_find:
        mock_insert.return_value.inserted_id = "mocked_id"
        mock_find.return_value = [
            {
                "_id": "mocked_id",
                "filename": "test.png",
                "url": "https://bucket.s3.region.amazonaws.com/key"
            }
        ]
        yield mock_insert, mock_find

def test_upload_image_success(mock_s3_upload, mock_mongo_insert_find):
    file_content = b"test image content"
    response = client.post(
        "/upload",
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mocked_id"
    assert data["filename"] == "test.png"
    assert data["url"].startswith("https://")

def test_upload_image_invalid_type(mock_s3_upload):
    response = client.post(
        "/upload",
        files={"file": ("test.txt", io.BytesIO(b"abc"), "text/plain")},
    )
    assert response.status_code == 400

def test_list_images(mock_s3_upload, mock_mongo_insert_find):
    response = client.get("/images")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["filename"] == "test.png"
    assert data[0]["id"] == "mocked_id"
