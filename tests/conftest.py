import pytest
from unittest.mock import Mock, patch
import boto3

@pytest.fixture
def mock_session():
    with patch('boto3.Session') as mock:
        yield mock

@pytest.fixture
def mock_sqs_client():
    with patch('boto3.Session') as mock_session:
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.meta.region_name = 'us-east-1'
        yield mock_client

@pytest.fixture
def mock_config_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    return config_file