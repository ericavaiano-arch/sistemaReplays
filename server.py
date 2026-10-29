import os
import certifi

os.environ["AWS_CA_BUNDLE"] = certifi.where()

from flask import Flask, jsonify, redirect, request, Response, stream_with_context
from flask_cors import CORS
import boto3
from botocore.config import Config

import config

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)


def _s3():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{config.R2_ENDPOINT}",
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4", connect_timeout=15),
        region_name="us-east-005",
        verify=certifi.where(),
    )


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/clips")
def list_clips():
    s3 = _s3()
    resp = s3.list_objects_v2(Bucket=config.R2_BUCKET_NAME)
    clips = []
    for obj in resp.get("Contents", []):
        name = obj["Key"]
        download_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": config.R2_BUCKET_NAME,
                "Key": name,
                "ResponseContentDisposition": f'attachment; filename="{name}"',
            },
            ExpiresIn=3600,
        )
        clips.append({
            "name": name,
            "size": obj["Size"],
            "last_modified": obj["LastModified"].isoformat(),
            "download_url": download_url,
        })
    clips.sort(key=lambda c: c["last_modified"], reverse=True)
    return jsonify(clips)


@app.route("/api/clips/<path:filename>/stream")
def stream_clip(filename):
    """Proxy do vídeo — passa o range request ao Backblaze e devolve ao browser."""
    s3 = _s3()

    kwargs = {"Bucket": config.R2_BUCKET_NAME, "Key": filename}
    range_header = request.headers.get("Range")
    if range_header:
        kwargs["Range"] = range_header

    obj = s3.get_object(**kwargs)
    status = 206 if range_header else 200

    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Length": str(obj["ContentLength"]),
    }
    if "ContentRange" in obj:
        headers["Content-Range"] = obj["ContentRange"]

    body = obj["Body"]

    def generate():
        while True:
            chunk = body.read(65536)
            if not chunk:
                break
            yield chunk

    return Response(
        stream_with_context(generate()),
        status=status,
        headers=headers,
    )


if __name__ == "__main__":
    print("Abrindo interface em http://localhost:5000")
    app.run(debug=False, port=5000, threaded=True)
