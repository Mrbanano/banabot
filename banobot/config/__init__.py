"""Configuration module for nanobot."""

from banobot.config.loader import load_config, get_config_path
from banobot.config.schema import Config

__all__ = ["Config", "load_config", "get_config_path"]
