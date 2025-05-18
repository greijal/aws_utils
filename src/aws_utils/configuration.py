from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
import yaml
import boto3


@dataclass
class AWSConfig:
    region: str = ""
    profile: str = ""


    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'AWSConfig':
        return cls(
            region=data.get('region', ''),
            profile=data.get('profile', '')
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            'region': self.region,
            'profile': self.profile
        }

    def is_valid(self) -> bool:
        return bool(self.region or self.profile)


class ConfigurationManager:
    DEFAULT_CONFIG_FILENAME = "config.yaml"
    YAML_OPTIONS = {
        'allow_unicode': True,
        'default_flow_style': False
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parents[1] / self.DEFAULT_CONFIG_FILENAME

    def load_config(self) -> AWSConfig:
        if not self.config_path.exists():
            return AWSConfig()

        with open(self.config_path, "r") as file:
            config_data = yaml.safe_load(file) or {}
            return AWSConfig.from_dict(config_data)

    def save_config(self, config: AWSConfig) -> None:
        with open(self.config_path, "w") as file:
            yaml.safe_dump(config.to_dict(), file, **self.YAML_OPTIONS)

    def _build_session_args(self, config: AWSConfig) -> Dict[str, str]:
        session_args = {}
        if config.region:
            session_args['region_name'] = config.region
        if config.profile:
            session_args['profile_name'] = config.profile
        return session_args

    def create_session(self) -> boto3.Session:
        config = self.load_config()
        session_args = self._build_session_args(config)
        return boto3.Session(**session_args)
