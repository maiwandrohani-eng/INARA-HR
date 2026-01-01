"""
File Storage Service
Handles file uploads to S3 or local filesystem
"""
import os
import uuid
from pathlib import Path
from typing import Optional, BinaryIO
import logging
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for file storage operations"""
    
    def __init__(self):
        # Check for Cloudflare R2 first (preferred naming), then fall back to S3 naming
        endpoint_url = settings.R2_ENDPOINT_URL or settings.S3_ENDPOINT_URL
        access_key = settings.R2_ACCESS_KEY_ID or settings.S3_ACCESS_KEY_ID
        secret_key = settings.R2_SECRET_ACCESS_KEY or settings.S3_SECRET_ACCESS_KEY
        bucket_name = settings.R2_BUCKET_NAME or settings.S3_BUCKET_NAME
        public_url = settings.R2_PUBLIC_URL or settings.S3_PUBLIC_URL
        region = settings.S3_REGION if settings.S3_REGION != "auto" else "auto"
        
        self.use_s3 = all([endpoint_url, access_key, secret_key, bucket_name])
        self.public_url = public_url
        self.storage_type = "r2" if settings.R2_ENDPOINT_URL else "s3" if self.use_s3 else "local"
        
        if self.use_s3:
            try:
                import boto3
                from botocore.config import Config
                
                # Configure region (R2 uses "auto", other S3-compatible services may need specific region)
                config_params = {"signature_version": "s3v4"}
                if region != "auto":
                    config_params["region_name"] = region
                
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(**config_params)
                )
                self.bucket_name = bucket_name
                storage_name = "Cloudflare R2" if settings.R2_ENDPOINT_URL else "S3-compatible"
                logger.info(f"File storage initialized with {storage_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize S3/R2, falling back to local storage: {str(e)}")
                self.use_s3 = False
                self.storage_type = "local"
        else:
            logger.info("File storage initialized with local filesystem")
            # Create uploads directory if it doesn't exist
            self.uploads_dir = Path("uploads")
            self.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder: str = "documents",
        employee_id: Optional[str] = None
    ) -> dict:
        """
        Upload a file to storage
        
        Returns:
            dict with file_path, file_url, and file_size
        """
        # Generate unique filename
        file_ext = Path(file_name).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        if employee_id:
            storage_path = f"{folder}/{employee_id}/{unique_filename}"
            local_path = self.uploads_dir / folder / employee_id / unique_filename if not self.use_s3 else None
        else:
            storage_path = f"{folder}/{unique_filename}"
            local_path = self.uploads_dir / folder / unique_filename if not self.use_s3 else None
        
        file_size = len(file_content)
        
        try:
            if self.use_s3:
                # Upload to S3
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=storage_path,
                    Body=file_content,
                    ContentType=self._get_content_type(file_ext)
                )
                
                # Generate URL - use public URL if configured, otherwise construct from endpoint
                if self.public_url:
                    # Cloudflare R2 public URL format
                    file_url = f"{self.public_url.rstrip('/')}/{storage_path}"
                else:
                    # Fallback to endpoint URL
                    endpoint_url = settings.R2_ENDPOINT_URL or settings.S3_ENDPOINT_URL
                    file_url = f"{endpoint_url}/{self.bucket_name}/{storage_path}"
                file_path = storage_path
            else:
                # Save to local filesystem
                if employee_id:
                    (self.uploads_dir / folder / employee_id).mkdir(parents=True, exist_ok=True)
                else:
                    (self.uploads_dir / folder).mkdir(parents=True, exist_ok=True)
                
                with open(local_path, 'wb') as f:
                    f.write(file_content)
                
                file_path = str(local_path)
                file_url = f"/uploads/{storage_path}"
            
            logger.info(f"File uploaded: {file_path} ({file_size} bytes)")
            
            return {
                "file_path": file_path,
                "file_url": file_url,
                "file_name": file_name,
                "file_size": file_size,
                "storage_type": self.storage_type
            }
        
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            if self.use_s3:
                # Extract key from path
                key = file_path.replace(f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/", "")
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            else:
                # Delete from local filesystem
                local_file = Path(file_path)
                if local_file.exists():
                    local_file.unlink()
            
            logger.info(f"File deleted: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> str:
        """Get URL for a file (with expiration for S3/R2)"""
        if self.use_s3:
            # If public URL is configured and file_path is a key, use public URL
            if self.public_url and not file_path.startswith('http'):
                return f"{self.public_url.rstrip('/')}/{file_path}"
            
            # Otherwise generate presigned URL
            # Extract key from file_path (remove endpoint/bucket prefix if present)
            endpoint_url = settings.R2_ENDPOINT_URL or settings.S3_ENDPOINT_URL
            if endpoint_url and endpoint_url in file_path:
                key = file_path.replace(f"{endpoint_url}/{self.bucket_name}/", "")
            elif settings.S3_ENDPOINT_URL and settings.S3_ENDPOINT_URL in file_path:
                key = file_path.replace(f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/", "")
            else:
                key = file_path
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        else:
            # Return local file URL
            return f"/uploads/{file_path}"
    
    def _get_content_type(self, file_ext: str) -> str:
        """Get MIME type from file extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
        }
        return content_types.get(file_ext.lower(), 'application/octet-stream')


# Singleton instance
file_storage = FileStorageService()

