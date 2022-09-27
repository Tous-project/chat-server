# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import sys
from typing import Any, Optional

from hydra import compose, initialize
from omegaconf import DictConfig


class Config:
    __instance: Optional[Config] = None
    __cfg: Optional[DictConfig] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Config:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if self.__instance is None:
            return
        pattern = r"[\w\.]+[=]{1}[\w\.]+"
        args_parser = filter(lambda x: re.fullmatch(pattern, x), sys.argv)
        with initialize(config_path="../config", version_base=None):
            self.__instance.__cfg = compose(
                config_name="config", overrides=list(args_parser)
            )

    def __call__(self, config_name: str = None) -> DictConfig:
        if self.__instance is None:
            raise Exception("Config Allocate Exception")
        if self.__instance.__cfg is None:
            raise Exception("Config Initialize Exception")
        if config_name is None or not hasattr(self.__instance.__cfg, config_name):
            return self.__instance.__cfg
        return self.__instance.__cfg.get(config_name)

config = Config()

if __name__ == "__main__":
    print(config())
    print(config("app"))
