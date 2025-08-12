import boto3
import requests
import json
import time
from django.conf import settings
from botocore.exceptions import ClientError
import os

def upload_to_s3(file_obj, filename):
    """파일을 S3에 업로드하고 URL 반환"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # S3에 파일 업로드
        s3_key = f"ocr-images/{filename}"
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        
        # 공개 URL 생성
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
        return s3_url
        
    except ClientError as e:
        print(f"S3 업로드 오류: {e}")
        return None

def call_naver_ocr_api(image_url):
    """네이버 OCR API 호출"""
    try:
        headers = {
            'X-OCR-SECRET': settings.NAVER_OCR_SECRET,
            'Content-Type': 'application/json'
        }
        
        # 현재 타임스탬프 생성
        timestamp = str(int(time.time() * 1000))
        
        payload = {
            "version": "V2",
            "requestId": "1234",
            "timestamp": timestamp,
            "lang": "ko",
            "images": [
                {
                    "format": "jpg",
                    "name": "billing",
                    "url": image_url
                }
            ],
            "enableTableDetection": True
        }
        
        response = requests.post(
            settings.NAVER_OCR_API_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"OCR API 오류: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        print(f"OCR API 호출 오류: {e}")
        return None

def save_ocr_result_to_file(ocr_result, filename="ocr_table.json"):
    """OCR 결과를 JSON 파일로 저장"""
    try:
        file_path = os.path.join(settings.BASE_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_result, f, ensure_ascii=False, indent=2)
        return file_path
    except Exception as e:
        print(f"파일 저장 오류: {e}")
        return None
