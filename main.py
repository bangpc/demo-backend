import os
from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import boto3
import uuid
from pymongo import MongoClient

# Optionally load environment variables from a .env file (for local dev)
from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "demo")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "images")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
images_collection = db[MONGO_COLLECTION]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")
    file_ext = os.path.splitext(file.filename)[1]
    key = f"{uuid.uuid4()}{file_ext}"
    s3_client.upload_fileobj(
        file.file,
        AWS_S3_BUCKET,
        key,
        ExtraArgs={"ContentType": file.content_type},
    )
    url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    image_doc = {
        "filename": file.filename,
        "s3_key": key,
        "url": url,
    }
    result = images_collection.insert_one(image_doc)
    return {
        "id": str(result.inserted_id),
        "filename": file.filename,
        "url": url,
    }

@router.get("/images")
def list_images():
    images = images_collection.find()
    return [
        {
            "id": str(img["_id"]),
            "filename": img["filename"],
            "url": img["url"],
        }
        for img in images
    ]

app.include_router(router)
