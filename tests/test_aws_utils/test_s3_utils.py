from unittest.mock import Mock, patch

import pytest

from src.aws_utils.s3_utils import S3Utils


@pytest.fixture
def mock_s3_client(mock_session):
    mock_client = Mock()
    mock_session.return_value.client.return_value = mock_client
    mock_client.meta.region_name = "us-east-1"
    return mock_client


class TestS3Utils:
    def test_init_default_session(self, mock_s3_client):
        s3_utils = S3Utils()
        assert s3_utils.client == mock_s3_client

    def test_init_custom_session(self):
        mock_session = Mock()
        mock_client = Mock()
        mock_session.client.return_value = mock_client

        s3_utils = S3Utils(session=mock_session)

        assert s3_utils.client == mock_client
        mock_session.client.assert_called_once_with("s3")

    def test_list_buckets(self, mock_s3_client):
        mock_s3_client.list_buckets.return_value = {
            "Buckets": [{"Name": "bucket1"}, {"Name": "bucket2"}]
        }

        s3_utils = S3Utils()
        result = s3_utils.list_buckets()

        assert result == ["bucket1", "bucket2"]
        mock_s3_client.list_buckets.assert_called_once()

    @patch("webbrowser.open")
    def test_open_bucket_in_console(self, mock_webbrowser, mock_s3_client):
        s3_utils = S3Utils()
        s3_utils.open_bucket_in_console("test-bucket")

        expected_url = "https://s3.console.aws.amazon.com/s3/buckets/test-bucket?region=us-east-1&tab=objects"
        mock_webbrowser.assert_called_once_with(expected_url)

    def test_delete_object_success(self, mock_s3_client):
        s3_utils = S3Utils()
        s3_utils.delete_object("test-bucket", "test-key")

        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key"
        )

    def test_delete_object_missing_params(self):
        s3_utils = S3Utils()
        with pytest.raises(ValueError):
            s3_utils.delete_object("", "")

    def test_delete_object_error(self, mock_s3_client):
        mock_s3_client.delete_object.side_effect = Exception("Test error")
        s3_utils = S3Utils()

        with pytest.raises(Exception, match="Test error"):
            s3_utils.delete_object("test-bucket", "test-key")

    @patch("os.path.exists")
    def test_upload_file(self, mock_exists, mock_s3_client):
        mock_exists.return_value = True
        s3_utils = S3Utils()

        s3_utils.upload_file("local/path.txt", "test-bucket", "remote/path.txt")

        mock_s3_client.upload_file.assert_called_once_with(
            "local/path.txt", "test-bucket", "remote/path.txt"
        )

    def test_upload_file_not_found(self):
        s3_utils = S3Utils()
        with pytest.raises(FileNotFoundError):
            s3_utils.upload_file("nonexistent.txt", "test-bucket")

    def test_upload_directory_not_found(self):
        s3_utils = S3Utils()
        with pytest.raises(NotADirectoryError):
            s3_utils.upload_directory("nonexistent", "test-bucket")
