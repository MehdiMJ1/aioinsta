from os import getenv
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent.resolve()


class Config:
    """Base application configuration class."""

    APP_NAME = "aioinsta"

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            if hasattr(self, attribute):
                try:
                    setattr(self, attribute, value)
                except AttributeError:
                    pass

    @property
    def db_url(self) -> str:
        """
        Property to get db connection url

        :raise ValueError: DB_URL env variable not present
        """

        if (db_url := getenv("DB_URL")) is not None:
            return db_url

        raise ValueError("You need to set DB_URL env variable")

    def load_params(self) -> dict:
        """
        Load all configuration params.

        :return: Configuration params
        :rtype: dict
        """

        return {
            attribute: getattr(self, attribute)
            for attribute in self.__dir__()
            if not attribute.startswith("__") and attribute.endswith("")
        }

    @classmethod
    def load_config(cls, **kwargs):
        """
        Make configuration and return it.

        :param kwargs: Params to override
        :type kwargs: dict
        :return: Configuration params
        :rtype: dict
        """

        config = cls(**kwargs)

        return config.load_params()

    def get_db_params(self) -> dict:
        """Get all db params."""

        return {}


class TestConfig(Config):
    @property
    def get_db_params(self):
        """Get params of test db."""

        return {
            "user": getenv("TEST_DB_USER", "s.hidenko"),
            "pass": getenv("TEST_DB_PASS", "test_pass"),
            "db": getenv("TEST_DB_DB", "test_db"),
            "host": getenv("TEST_DB_HOST", "localhost"),
            "post": getenv("TEST_DB_PORT", 5432),
        }

    @property
    def db_url(self) -> str:
        """Return sqlite db path"""

        params = self.get_db_params

        return "postgresql://{user}:{pass}@{host}:{post}".format(**params)
