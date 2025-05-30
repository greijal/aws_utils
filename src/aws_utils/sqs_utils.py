import webbrowser
from typing import Dict, List, Optional
from configuration import ConfigurationManager
import boto3


class SQSUtils:
    MAX_BATCH_SIZE = 10
    CONSOLE_URL_TEMPLATE = "https://{region}.console.aws.amazon.com/sqs/v2/home?region={region}#/queues/{queue_name}"
    ALL_ATTRIBUTES = ["All"]
    MSG_COUNT_ATTRIBUTE = ["ApproximateNumberOfMessages"]

    def __init__(self, session: Optional[boto3.Session] = None) -> None:
        self.client = (session or boto3.Session()).client("sqs")
        self.config_manager = ConfigurationManager()

    def list_queues(self) -> List[str]:

        response = self.client.list_queues()
        list_queues = response.get("QueueUrls", [])
        while response.get("NextToken"):
            response = self.client.list_queues(NextToken=response["NextToken"])
            list_queues.extend(response.get("QueueUrls", []))

        return [(queue,queue.split("/")[-1]) for queue in list_queues]


    def get_message_count(self, queue_url: Optional[str] = None) -> int:
        if not queue_url:
            queue_url = self.config_manager.load_config().sqs
        attrs = self.client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=self.MSG_COUNT_ATTRIBUTE
        )
        return int(attrs["Attributes"]["ApproximateNumberOfMessages"])

    def open_in_console(self, queue_url: Optional[Optional] = None,
                        region: Optional[str] = None) -> None:

        if not queue_url:
            queue_url = self.config_manager.load_config().sqs
        if not region:
            region = self.config_manager.load_config().region

        queue_name = queue_url.split("/")[-1]
        console_url = self.CONSOLE_URL_TEMPLATE.format(
            region=region, queue_name=queue_name
        )
        webbrowser.open(console_url)

    def get_attributes(self, queue_url: str) -> Dict:
        response = self.client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=self.ALL_ATTRIBUTES
        )
        return response.get("Attributes", {})

    def purge(self, queue_url: str) -> None:
        self.client.pu(QueueUrl=queue_url)

    def receive_messages(self, queue_url: str) -> List[Dict]:
        response = self.client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=self.MAX_BATCH_SIZE,
            WaitTimeSeconds=2,
        )
        return response.get("Messages", [])

    def send_message(self, queue_url: str, body: str) -> None:
        response = self.client.send_message(QueueUrl=queue_url, MessageBody=body)
        print(f"[SQSUtils] Send message response: {response}")

    def send_messages_from_file(self, queue_url: str, file_path: str) -> None:
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        entries = [{"Id": str(i), "MessageBody": line} for i, line in enumerate(lines)]

        for batch in self._get_batches(entries):
            response = self.client.send_message_batch(QueueUrl=queue_url, Entries=batch)
            print(f"[SQSUtils] Send message response: {response}")

    def _get_batches(self, entries: List[Dict]) -> List[List[Dict]]:
        return [
            entries[i : i + self.MAX_BATCH_SIZE]
            for i in range(0, len(entries), self.MAX_BATCH_SIZE)
        ]
