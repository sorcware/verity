import os

import yaml


class VerityConfig:
    def __init__(self):
        self.SECRET_KEY = os.environ.get("SECRET_KEY") or "super_secret_key"
        self.DATABASE = "api/data/verity.db"
        self.CONFIG_FILE_DIRECTORY = "api/config_files"
        self.LOGGING_CONFIG = self.load_config_file("logging_config.yaml")
        self.DATABASE_SCHEMA = self.load_config_file("verity_schema.yaml")

    def load_config_file(self, file):
        config = ""
        filepath = os.path.join(self.CONFIG_FILE_DIRECTORY, file)
        try:
            with open(filepath, "r") as f:
                try:
                    config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    print(e)
                    return yaml.YAMLError
            return config
        except FileNotFoundError:
            raise FileNotFoundError
