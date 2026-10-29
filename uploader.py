import os
import ssl

import boto3
import certifi
import urllib3
from botocore.config import Config
from botocore.httpsession import URLLib3Session

import config


def _build_client():
    endpoint = f"https://{config.R2_ENDPOINT}"

    # Força TLS 1.2+ e usa certificados do certifi — necessário no Windows
    # quando antivírus ou proxy intercepta conexões SSL
    os.environ["AWS_CA_BUNDLE"] = certifi.where()

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        config=Config(
            signature_version="s3v4",
            connect_timeout=15,
            retries={"max_attempts": 3},
        ),
        region_name="us-east-005",
        verify=certifi.where(),
    )


def upload(filepath: str) -> str:
    filename = os.path.basename(filepath)
    client = _build_client()

    print(f"Enviando {filename} para R2...")
    client.upload_file(
        filepath,
        config.R2_BUCKET_NAME,
        filename,
        ExtraArgs={"ContentType": "video/mp4"},
    )

    os.remove(filepath)
    print("Arquivo local removido.")

    if config.R2_PUBLIC_URL:
        url = f"{config.R2_PUBLIC_URL.rstrip('/')}/{filename}"
    else:
        url = f"https://{config.R2_ENDPOINT}/{config.R2_BUCKET_NAME}/{filename}"

    return url
