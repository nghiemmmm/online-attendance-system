import os
import unittest
from unittest.mock import patch

from app.core.config import settings
from app.storage.cloudinary_storage import CloudinaryStorageService
from app.storage.local_storage import LocalStorageService
from app.storage.storage_factory import get_storage_service


class TestStorageAbstraction(unittest.TestCase):
    def setUp(self):
        self.dummy_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x00\x07\xff\xd9"  # 1x1 JPG bytes
        self.filename = "test_image.jpg"
        self.folder = "test_folder"

    def test_storage_factory_local(self):
        with patch.object(settings, "IMAGE_STORAGE_PROVIDER", "LOCAL"):
            # Reset cache singleton
            import app.storage.storage_factory as factory

            factory._storage_instance = None

            service = get_storage_service()
            self.assertIsInstance(service, LocalStorageService)

    def test_storage_factory_cloudinary(self):
        with patch.object(settings, "IMAGE_STORAGE_PROVIDER", "CLOUDINARY"):
            import app.storage.storage_factory as factory

            factory._storage_instance = None

            service = get_storage_service()
            self.assertIsInstance(service, CloudinaryStorageService)

    def test_local_storage_save_and_delete(self):
        local_service = LocalStorageService()
        metadata = local_service.save_image(
            file_bytes=self.dummy_bytes, filename=self.filename, folder=self.folder
        )

        self.assertEqual(metadata["storage_provider"], "LOCAL")
        self.assertIsNotNone(metadata["image_path"])
        self.assertTrue(os.path.exists(metadata["image_path"]))

        # Verify get URL
        url = local_service.get_image_url(metadata["public_id"])
        self.assertTrue(url.startswith("/"))

        # Delete file
        deleted = local_service.delete_image(metadata["public_id"])
        self.assertTrue(deleted)
        self.assertFalse(os.path.exists(metadata["image_path"]))

    @patch("app.storage.cloudinary_storage.upload_to_cloudinary")
    def test_cloudinary_storage_success(self, mock_upload):
        mock_upload.return_value = "https://res.cloudinary.com/test_url.jpg"

        cloudinary_service = CloudinaryStorageService()
        metadata = cloudinary_service.save_image(
            file_bytes=self.dummy_bytes, filename=self.filename, folder=self.folder
        )

        self.assertEqual(metadata["storage_provider"], "CLOUDINARY")
        self.assertEqual(
            metadata["secure_url"], "https://res.cloudinary.com/test_url.jpg"
        )
        mock_upload.assert_called_once()

    @patch("app.storage.cloudinary_storage.upload_to_cloudinary")
    @patch("time.sleep")
    def test_cloudinary_storage_retry_and_fallback(self, mock_sleep, mock_upload):
        # Mock upload_to_cloudinary to fail all 3 times
        mock_upload.side_effect = Exception("Cloudinary connection error")

        cloudinary_service = CloudinaryStorageService()
        metadata = cloudinary_service.save_image(
            file_bytes=self.dummy_bytes, filename=self.filename, folder=self.folder
        )

        # Should fallback to LOCAL storage
        self.assertEqual(metadata["storage_provider"], "LOCAL")
        self.assertTrue(os.path.exists(metadata["image_path"]))
        self.assertEqual(mock_upload.call_count, 3)  # 3 attempts
        self.assertEqual(mock_sleep.call_count, 2)  # Sleep between attempts: 1s, 2s

        # Cleanup
        os.remove(metadata["image_path"])
