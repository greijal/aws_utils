import boto3
import pytest


LOCALSTACK_ENDPOINT = "http://localhost:4566"
REGION = "us-east-1"


@pytest.fixture(scope="module")
def s3_client():
    return boto3.client(
        "s3",
        region_name=REGION,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def s3_utils(s3_client):
    utils = S3Utils()
    utils.client = s3_client
    return utils


@pytest.fixture
def bucket_name(s3_client):
    name = "test-bucket"
    s3_client.create_bucket(Bucket=name)
    return name


def test_upload_and_list_buckets(s3_utils, bucket_name):
    buckets = s3_utils.list_buckets()
    assert bucket_name in buckets


def test_upload_file_and_delete(s3_utils, bucket_name, tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("conteúdo de teste")
    key = "test.txt"

    s3_utils.upload_file(str(file_path), bucket_name, key)

    objects = s3_utils.client.list_objects_v2(Bucket=bucket_name)
    assert any(obj["Key"] == key for obj in objects.get("Contents", []))

    s3_utils.delete_object(bucket_name, key)
    objects = s3_utils.client.list_objects_v2(Bucket=bucket_name)
    assert not objects.get("Contents", [])
