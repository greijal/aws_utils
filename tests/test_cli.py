import pytest
from unittest.mock import Mock, patch
from cli import MenuHandler, SQSActionExecutor, S3ActionExecutor, MenuOptions


class TestMenuHandler:
    def setup_method(self):
        class ConcreteMenuHandler(MenuHandler):
            def _init_actions(self):
                return {"test_action": lambda: None}

        self.session = Mock()
        self.menu_options = {"test_action": "Test Action", "back": "Voltar"}
        self.handler = ConcreteMenuHandler(self.session, self.menu_options, "Teste")

    @patch('questionary.select')
    def test_execute_menu_back_option(self, mock_select):
        mock_select.return_value.ask.return_value = "Voltar"
        self.handler.execute_menu()
        mock_select.assert_called_once()


class TestSQSActionExecutor:
    def setup_method(self):
        self.session = Mock()
        self.executor = SQSActionExecutor(self.session)
        self.executor.sqs = Mock()

    def test_init(self):
        assert isinstance(self.executor.menu_options, dict)
        assert len(self.executor._actions) == 8

    @patch('questionary.select')
    def test_list_queues(self, mock_select):
        self.executor.sqs.list_queues.return_value = ["queue1", "queue2"]
        self.executor._list_queues()
        self.executor.sqs.list_queues.assert_called_once()



@patch('cli.ConfigurationManager')
def test_main_exit(mock_config_manager):
    with patch('questionary.select') as mock_select:
        mock_select.return_value.ask.return_value = "Exit"
        from cli import main
        main()
        mock_select.assert_called()