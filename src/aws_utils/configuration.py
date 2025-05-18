from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import boto3
import yaml


@dataclass
class AWSConfig:
    region: str = ""
    profile: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "AWSConfig":
        return cls(region=data.get("region", ""), profile=data.get("profile", ""))

    def to_dict(self) -> Dict[str, str]:
        return {"region": self.region, "profile": self.profile}

    def is_valid(self) -> bool:
        return bool(self.region or self.profile)


class ConfigurationManager:
    DEFAULT_CONFIG_FILENAME = "config.yaml"
    YAML_OPTIONS = {"allow_unicode": True, "default_flow_style": False}

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = (
            config_path or Path(__file__).parents[2] / self.DEFAULT_CONFIG_FILENAME
        )

    def load_config(self) -> AWSConfig:
        if not self.config_path.exists():
            print("Configuration file not found. Using default settings.")
            return AWSConfig()

        with open(self.config_path, "r") as file:
            config_data = yaml.safe_load(file) or {}
            return AWSConfig.from_dict(config_data)

    def save_config(self, config: AWSConfig) -> None:
        try:
            with open(self.config_path, "w") as file:
                config_dict = config.to_dict()
                yaml.safe_dump(
                    config_dict, file, allow_unicode=True, default_flow_style=False
                )
        except OSError as e:
            raise OSError(f"Erro ao salvar arquivo de configuração: {e}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Erro ao serializar configuração YAML: {e}")

    def _build_session_args(self, config: AWSConfig) -> Dict[str, str]:
        session_args = {}
        if config.region:
            session_args["region_name"] = config.region
        if config.profile:
            session_args["profile_name"] = config.profile
        return session_args

    def create_session(self) -> boto3.Session:
        config = self.load_config()
        session_args = self._build_session_args(config)
        return boto3.Session(**session_args)
