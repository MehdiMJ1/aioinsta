from argparse import Namespace
import os
from pathlib import Path

from alembic.config import CommandLine, Config

from api.config import Config as AppConfig


BASE_PATH = Path(__file__).parent.resolve()


def main() -> None:
    """Setup and run alembic."""

    alembic = CommandLine()
    options = alembic.parser.parse_args()

    if "cmd" not in options:
        alembic.parser.error("too few arguments")
        exit(128)
    else:
        config = make_alembic_config(options)
        exit(alembic.run_cmd(config, options))


def make_alembic_config(
    cmd_opts: Namespace, base_path: str = BASE_PATH
) -> Config:
    """
    Create custom alembic config.

    :param cmd_opts: Default config
    :type cmd_opts: Namespace
    :param base_path: Path of config file
    :type base_path: str
    :return: Alembic configuration
    :rtype: Config
    """

    # Make path to config absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, cmd_opts=cmd_opts)

    # Make path to scripts absolute
    alembic_location = config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            "script_location", os.path.join(base_path, alembic_location)
        )

    # Set alembic db from application config
    config.set_main_option("sqlalchemy.url", AppConfig().db_url)

    return config


if __name__ == "__main__":
    main()
