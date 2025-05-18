import questionary
import yaml
from abc import ABC, abstractmethod
from colorama import Fore, Style, init
from utils.sqs_utils import SQSUtils
from utils.s3_utils import S3Utils
from config.configuration import ConfigurationManager, AWSConfig


class MenuOptions:
    MAIN = ["SQS", "S3", "Configure", "Exit"]

    SQS = {
        "list_queues": "List queues",
        "display_message_count": "Count messages in queue",
        "open_queue_console": "Open queue in console",
        "display_queue_settings": "View queue settings",
        "clear_queue": "Clear queue",
        "scan_messages": "Scan messages",
        "send_message_to_queue": "Post message",
        "send_batch_messages": "Post messages from file",
        "back": "Back"
    }

    S3 = {
        "list_buckets": "List buckets",
        "open_bucket": "Open bucket in console",
        "delete_object": "Delete file",
        "upload_file": "Upload file",
        "upload_directory": "Upload directory",
        "back": "Back"
    }


class MenuHandler(ABC):
    def __init__(self, session, menu_options, menu_prompt):
        self.session = session
        self.menu_options = menu_options
        self.menu_prompt = menu_prompt
        self._actions = self._init_actions()

    @abstractmethod
    def _init_actions(self):
        pass

    def execute_menu(self):
        while True:
            action = questionary.select(
                self.menu_prompt,
                choices=list(self.menu_options.values())
            ).ask()

            if action == self.menu_options["back"]:
                break

            action_key = next(k for k, v in self.menu_options.items() if v == action)
            if action_key in self._actions:
                self._actions[action_key]()


class SQSActionExecutor(MenuHandler):
    def __init__(self, session):
        super().__init__(session, MenuOptions.SQS, "What would you like to do with SQS?")
        self.sqs = SQSUtils(session)

    def _init_actions(self):
        return {
            "list_queues": self._list_queues,
            "display_message_count": self._display_message_count,
            "open_queue_console": self._open_queue_console,
            "display_queue_settings": self._display_queue_settings,
            "clear_queue": self._clear_queue,
            "scan_messages": self._scan_messages,
            "send_message_to_queue": self._send_message_to_queue,
            "send_batch_messages": self._send_batch_messages
        }

    def _list_queues(self):
        queue_list = self.sqs.list_queues()
        print(Fore.GREEN + "Found queues:")
        for queue in queue_list:
            print(Fore.YELLOW + queue)

    def _display_message_count(self):
        queue_url = select_queue(self.sqs)
        count = self.sqs.get_message_count(queue_url)
        print(Fore.GREEN + f"Message count: {count}")

    def _open_queue_console(self):
        queue_url = select_queue(self.sqs)
        region = questionary.text("Enter region (or leave blank for default):").ask()
        self.sqs.open_queue_in_console(queue_url, region or None)

    def _display_queue_settings(self):
        queue_url = select_queue(self.sqs)
        attrs = self.sqs.get_queue_attributes(queue_url)
        print(Fore.GREEN + "Queue settings:")
        print(Fore.YELLOW + yaml.safe_dump(attrs, allow_unicode=True, default_flow_style=False))

    def _clear_queue(self):
        queue_url = select_queue(self.sqs)
        if questionary.confirm(f"Are you sure you want to clear the queue?\n{queue_url}").ask():
            self.sqs.purge_queue(queue_url)
            print(Fore.RED + "Queue cleared successfully!")

    def _scan_messages(self):
        queue_url = select_queue(self.sqs)
        messages = self.sqs.scan_messages(queue_url)
        if messages:
            print(Fore.GREEN + f"Found {len(messages)} messages:")
            for message in messages:
                print(Fore.YELLOW + message.get("Body", ""))
        else:
            print(Fore.YELLOW + "No messages found.")

    def _send_message_to_queue(self):
        queue_url = select_queue(self.sqs)
        body = questionary.text("Enter message:").ask()
        self.sqs.send_message(body, queue_url)
        print(Fore.GREEN + "Message sent!")

    def _send_batch_messages(self):
        queue_url = select_queue(self.sqs)
        file_path = questionary.text("Enter file path:").ask()
        self.sqs.send_batch_messages(file_path, queue_url)
        print(Fore.GREEN + "Batch messages sent!")


class S3ActionExecutor(MenuHandler):
    def __init__(self, session):
        super().__init__(session, MenuOptions.S3, "What would you like to do with S3?")
        self.s3 = S3Utils(session)

    def _init_actions(self):
        return {
            "list_buckets": self._list_buckets,
            "open_bucket": self._open_bucket,
            "delete_object": self._delete_object,
            "upload_file": self._upload_file,
            "upload_directory": self._upload_directory
        }

    def _list_buckets(self):
        buckets = self.s3.list_buckets()
        print(Fore.GREEN + "Found buckets:")
        for bucket in buckets:
            print(Fore.YELLOW + bucket)

    def _open_bucket(self):
        bucket = questionary.text("Enter bucket name (or leave blank for default):").ask()
        self.s3.open_bucket_in_console(bucket or None)

    def _delete_object(self):
        bucket = questionary.text("Bucket:").ask()
        key = questionary.text("Key (path/file) to delete:").ask()
        self.s3.delete_object(bucket, key)
        print(Fore.RED + "File deleted!")

    def _upload_file(self):
        bucket = questionary.text("Bucket:").ask()
        file_path = questionary.text("Local file path:").ask()
        key = questionary.text("Destination key in bucket (or leave blank to use file name):").ask()
        self.s3.upload_file(file_path, bucket, key or None)
        print(Fore.GREEN + "File uploaded!")

    def _upload_directory(self):
        bucket = questionary.text("Bucket:").ask()
        dir_path = questionary.text("Local directory path:").ask()
        prefix = questionary.text("Destination prefix in bucket (optional):").ask()
        self.s3.upload_directory(dir_path, bucket, prefix or "")
        print(Fore.GREEN + "Directory uploaded!")


def select_queue(sqs):
    queue_list = sqs.list_queues()
    choices = queue_list + ["Enter manually"]
    selected = questionary.select(
        "Select a queue or enter manually:",
        choices=choices
    ).ask()

    if selected == "Enter manually":
        return questionary.text("Enter queue URL:").ask()
    return selected


def main():
    init(autoreset=True)
    config_manager = ConfigurationManager()
    print(Fore.CYAN + Style.BRIGHT + "Welcome to AWS Utils CLI!\n")

    while True:
        choice = questionary.select(
            "Which AWS resource would you like to manage?",
            choices=MenuOptions.MAIN
        ).ask()

        if choice == "SQS":
            session = config_manager.create_session()
            SQSActionExecutor(session).execute_menu()
        elif choice == "S3":
            session = config_manager.create_session()
            S3ActionExecutor(session).execute_menu()
        elif choice == "Configure":
            region = questionary.text("Enter default region:").ask()
            profile = questionary.text("Enter default profile:").ask()
            config = AWSConfig(
                profile=profile.strip(),
                region=region.strip()
            )
            config_manager.save_config(config)
            print(Fore.GREEN + "Configuration saved successfully!")
        elif choice == "Exit":
            print(Fore.RED + "Exiting AWS Utils CLI.")
            break


if __name__ == "__main__":
    main()
