import os

import yaml

from api.src import config


def test_verity_config_default_secret_key(monkeypatch):
    """Test that the default secret key is used
    if the environment variable is not set."""
    testing_config = config.VerityConfig()
    assert testing_config.SECRET_KEY == "super_secret_key"


def test_verity_config_secret_key_from_env(monkeypatch):
    """Test that the secret key is loaded from the environment variable."""
    os.environ["SECRET_KEY"] = "a_real_secret"
    testing_config = config.VerityConfig()
    assert testing_config.SECRET_KEY == "a_real_secret"
    del os.environ["SECRET_KEY"]  # Clean up the environment


def test_verity_config_database_name(monkeypatch):
    """Test that the database name is correctly set."""
    testing_config = config.VerityConfig()
    assert testing_config.DATABASE == "api/data/verity.db"


def test_verity_config_config_file_directory(monkeypatch):
    """Test that the config file directory is set."""
    testing_config = config.VerityConfig()
    assert testing_config.CONFIG_FILE_DIRECTORY == "api/config_files"


def test_verity_config_load_config_file(monkeypatch):
    """Test that load_config_file handles successful YAML loading."""
    # Mock the YAML file content
    mock_config = {"logging_level": "INFO"}

    # Create a temporary file
    import tempfile

    temp_dir = tempfile.mkdtemp()
    mock_filepath = os.path.join(temp_dir, "logging_config.yaml")
    with open(mock_filepath, "w") as f:
        yaml.safe_dump(mock_config, f)

    # Configure monkeypatch to simulate file loading
    testing_config = config.VerityConfig()
    monkeypatch.setattr(testing_config, "CONFIG_FILE_DIRECTORY", temp_dir)
    loaded_config = testing_config.load_config_file("logging_config.yaml")
    assert loaded_config == mock_config

    # Clean up the temporary file
    import shutil

    shutil.rmtree(temp_dir)
