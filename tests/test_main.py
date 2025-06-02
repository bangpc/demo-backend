import io
import os
import pytest
from unittest.mock import MagicMock, patch
import asyncio

# Patch environment variables for AWS and Mongo
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_S3_BUCKET"] = "bucket"
os.environ["AWS_REGION"] = "region"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
os.environ["MONGO_DB"] = "demo"
os.environ["MONGO_COLLECTION"] = "images"

# Ensure the parent directory is in sys.path for module resolution
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import create_app, get_clients

@pytest.fixture
def mock_clients():
    s3_client = MagicMock()
    images_collection = MagicMock()
    AWS_S3_BUCKET = "bucket"
    AWS_REGION = "region"
    return s3_client, AWS_S3_BUCKET, AWS_REGION, images_collection

def test_upload_image_success(mock_clients):
    s3_client, AWS_S3_BUCKET, AWS_REGION, images_collection = mock_clients
    # Simulate insert_one returning an object with inserted_id
    images_collection.insert_one.return_value.inserted_id = "mocked_id"
    # Prepare a fake UploadFile
    class DummyFile:
        def __init__(self, content):
            self.file = io.BytesIO(content)
            self.filename = "test.png"
            self.content_type = "image/png"
    file = DummyFile(b"test image content")
    # Patch get_clients to return our mocks
    with patch("main.get_clients", return_value=mock_clients):
        app = create_app()
        # Get the upload_image function from the router
        upload_func = [r for r in app.router.routes if r.path == "/upload"][0].endpoint
        # Call the async function directly
        result = asyncio.run(upload_func(file=file))
        assert result["id"] == "mocked_id"
        assert result["filename"] == "test.png"
        assert result["url"].startswith("https://")

def test_upload_image_invalid_type(mock_clients):
    class DummyFile:
        def __init__(self, content):
            self.file = io.BytesIO(content)
            self.filename = "test.txt"
            self.content_type = "text/plain"
    file = DummyFile(b"abc")
    with patch("main.get_clients", return_value=mock_clients):
        app = create_app()
        upload_func = [r for r in app.router.routes if r.path == "/upload"][0].endpoint
        with pytest.raises(Exception) as excinfo:
            asyncio.run(upload_func(file=file))
        # Check the exception detail for HTTPException
        assert getattr(excinfo.value, "detail", None) == "Invalid image file"

def test_list_images(mock_clients):
    s3_client, AWS_S3_BUCKET, AWS_REGION, images_collection = mock_clients
    images_collection.find.return_value = [
        {
            "_id": "mocked_id",
            "filename": "test.png",
            "url": "https://bucket.s3.region.amazonaws.com/key"
        }
    ]
    with patch("main.get_clients", return_value=mock_clients):
        app = create_app()
        list_func = [r for r in app.router.routes if r.path == "/images"][0].endpoint
        result = list_func()
        assert isinstance(result, list)
        assert result[0]["filename"] == "test.png"
        assert result[0]["id"] == "mocked_id"
