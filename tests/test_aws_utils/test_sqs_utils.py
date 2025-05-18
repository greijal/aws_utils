from unittest.mock import Mock, patch
import pytest

from src.aws_utils.sqs_utils import SQSUtils


@pytest.fixture
def mock_sqs_client():
    with patch("boto3.Session") as mock_session:
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.meta.region_name = "us-east-1"
        yield mock_client


@pytest.fixture
def sqs_utils(mock_sqs_client):
    return SQSUtils()


class TestSQSUtils:
    def test_get_queues(self, sqs_utils, mock_sqs_client):
        mock_queues = ["queue1", "queue2"]
        mock_sqs_client.list_queues.return_value = {"QueueUrls": mock_queues}

        result = sqs_utils.get_queues()

        assert result == mock_queues
        mock_sqs_client.list_queues.assert_called_once()

    def test_get_message_count(self, sqs_utils, mock_sqs_client):
        queue_url = "test-queue-url"
        mock_sqs_client.get_queue_attributes.return_value = {
            "Attributes": {"ApproximateNumberOfMessages": "42"}
        }

        result = sqs_utils.get_message_count(queue_url)

        assert result == 42
        mock_sqs_client.get_queue_attributes.assert_called_once_with(
            QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )

    @patch("webbrowser.open")
    def test_open_in_console(self, mock_webbrowser, sqs_utils, mock_sqs_client):
        queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
        expected_url = "https://us-east-1.console.aws.amazon.com/sqs/v2/home?region=us-east-1#/queues/test-queue"

        sqs_utils.open_in_console(queue_url)

        mock_webbrowser.assert_called_once_with(expected_url)

    def test_get_attributes(self, sqs_utils, mock_sqs_client):
        queue_url = "test-queue-url"
        mock_attributes = {"VisibilityTimeout": "30", "DelaySeconds": "0"}
        mock_sqs_client.get_queue_attributes.return_value = {
            "Attributes": mock_attributes
        }

        result = sqs_utils.get_attributes(queue_url)

        assert result == mock_attributes
        mock_sqs_client.get_queue_attributes.assert_called_once_with(
            QueueUrl=queue_url, AttributeNames=["All"]
        )

    def test_purge(self, sqs_utils, mock_sqs_client):
        queue_url = "test-queue-url"

        sqs_utils.purge(queue_url)

        mock_sqs_client.purge_queue.assert_called_once_with(QueueUrl=queue_url)

    def test_receive_messages(self, sqs_utils, mock_sqs_client):
        queue_url = "test-queue-url"
        mock_messages = [{"MessageId": "1", "Body": "test message"}]
        mock_sqs_client.receive_message.return_value = {"Messages": mock_messages}

        result = sqs_utils.receive_messages(queue_url)

        assert result == mock_messages
        mock_sqs_client.receive_message.assert_called_once_with(
            QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=2
        )

    def test_send_message(self, sqs_utils, mock_sqs_client):
        queue_url = "test-queue-url"
        message_body = "test message"

        sqs_utils.send_message(queue_url, message_body)

        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=queue_url, MessageBody=message_body
        )

    def test_get_batches(self, sqs_utils):
        entries = [{"Id": str(i)} for i in range(25)]

        batches = sqs_utils._get_batches(entries)

        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5
