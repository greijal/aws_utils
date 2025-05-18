from pathlib import Path

import pytest

from src.aws_utils.configuration import AWSConfig, ConfigurationManager


class TestAWSConfig:
    def test_default_config(self):
        config = AWSConfig()
        assert config.region == ""
        assert config.profile == ""
        assert not config.is_valid()

    def test_custom_config(self):
        config = AWSConfig(region="us-east-1", profile="dev")
        assert config.region == "us-east-1"
        assert config.profile == "dev"
        assert config.is_valid()

    def test_from_dict_empty(self):
        config = AWSConfig.from_dict({})
        assert config.region == ""
        assert config.profile == ""

    def test_from_dict_with_data(self):
        data = {"region": "eu-west-1", "profile": "prod"}
        config = AWSConfig.from_dict(data)
        assert config.region == "eu-west-1"
        assert config.profile == "prod"

    def test_to_dict(self):
        config = AWSConfig(region="ap-south-1", profile="test")
        expected = {"region": "ap-south-1", "profile": "test"}
        assert config.to_dict() == expected

    def test_is_valid_with_region(self):
        config = AWSConfig(region="us-west-2")
        assert config.is_valid()

    def test_is_valid_with_profile(self):
        config = AWSConfig(profile="default")
        assert config.is_valid()


class TestConfigurationManager:
    def test_init_default_path(self):
        manager = ConfigurationManager()
        assert isinstance(manager.config_path, Path)

    def test_init_custom_path(self, tmp_path):
        config_path = tmp_path / "test_config.yaml"
        manager = ConfigurationManager(config_path)
        assert manager.config_path == config_path

    def test_load_config_nonexistent_file(self, tmp_path):
        manager = ConfigurationManager(tmp_path / "nonexistent.yaml")
        config = manager.load_config()
        assert isinstance(config, AWSConfig)
        assert not config.is_valid()

    def test_load_config_empty_file(self, tmp_path):
        config_path = tmp_path / "empty.yaml"
        config_path.touch()
        manager = ConfigurationManager(config_path)
        config = manager.load_config()
        assert isinstance(config, AWSConfig)
        assert not config.is_valid()

    def test_save_and_load_config(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        manager = ConfigurationManager(config_path)

        original_config = AWSConfig(region="us-east-1", profile="test")
        manager.save_config(original_config)

        loaded_config = manager.load_config()
        assert loaded_config.region == original_config.region
        assert loaded_config.profile == original_config.profile

    def test_build_session_args_empty(self):
        manager = ConfigurationManager()
        config = AWSConfig()
        args = manager._build_session_args(config)
        assert args == {}

    def test_build_session_args_full(self):
        manager = ConfigurationManager()
        config = AWSConfig(region="us-east-1", profile="test")
        args = manager._build_session_args(config)
        assert args == {"region_name": "us-east-1", "profile_name": "test"}

    @pytest.mark.parametrize(
        "config_data,expected_args",
        [
            ({"region": "us-east-1"}, {"region_name": "us-east-1"}),
            ({"profile": "dev"}, {"profile_name": "dev"}),
            ({}, {}),
        ],
    )
    def test_build_session_args_variants(self, config_data, expected_args):
        manager = ConfigurationManager()
        config = AWSConfig.from_dict(config_data)
        args = manager._build_session_args(config)
        assert args == expected_args
