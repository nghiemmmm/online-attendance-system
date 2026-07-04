import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import urllib.request

from app.utils.cloudinary import upload_to_cloudinary


def main():
    print("Testing REAL Cloudinary Upload using provided credentials...")
    # Sample tiny image bytes (red dot 1x1 GIF or download demo image)
    sample_url = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    with urllib.request.urlopen(sample_url) as resp:
        img_bytes = resp.read()

    url = upload_to_cloudinary(
        img_bytes, folder="online_attendance/test", public_id="test_sample"
    )
    print(f"Uploaded URL from Cloudinary: {url}")


if __name__ == "__main__":
    main()
