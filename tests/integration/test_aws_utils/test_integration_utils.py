import time

import boto3
import pytest

from src.aws_utils.sqs_utils import SQSUtils

LOCALSTACK_ENDPOINT = "http://localhost:4566"
REGION = "us-east-1"


@pytest.fixture(scope="module")
def sqs_client():
    # Aguarda o LocalStack subir
    time.sleep(5)
    return boto3.client(
        "sqs",
        region_name=REGION,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture(scope="module")
def sqs_utils(sqs_client):
    session = boto3.Session(
        aws_access_key_id="test", aws_secret_access_key="test", region_name=REGION
    )
    # Força o endpoint do LocalStack
    session._session.set_config_variable("sqs", {"endpoint_url": LOCALSTACK_ENDPOINT})
    utils = SQSUtils(session)
    utils.client = sqs_client
    return utils


@pytest.fixture
def queue_url(sqs_client):
    response = sqs_client.create_queue(QueueName="test-queue")
    return response["QueueUrl"]


def test_send_and_receive_message(sqs_utils, queue_url):
    sended_body = "mensagem de teste"
    sqs_utils.send_message(queue_url, sended_body)
    messages = sqs_utils.receive_messages(queue_url)
    assert any(msg["Body"] == sended_body for msg in messages)


def test_get_message_count(sqs_utils, queue_url):
    sqs_utils.send_message(queue_url, "msg1")
    count = sqs_utils.get_message_count(queue_url)
    assert count >= 1


def test_purge_queue(sqs_utils, queue_url):
    sqs_utils.send_message(queue_url, "msg2")
    sqs_utils.purge(queue_url)
    time.sleep(1)
    count = sqs_utils.get_message_count(queue_url)
    assert count == 0
