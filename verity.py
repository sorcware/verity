import atexit
import logging
import logging.config
import os

from flask import Flask

from api.src.config import VerityConfig
from api.src.data_handler import Database
from front.home import home_bp


def set_up_logging(config):
    os.makedirs("../logs", exist_ok=True)
    logging.config.dictConfig(config.LOGGING_CONFIG)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


if __name__ == "__main__":
    # config and logging
    verity_config = VerityConfig()
    logger = logging.getLogger(__name__)
    set_up_logging(verity_config)
    logger.info("app starting")

    # database initialise
    verity = Database(verity_config)
    logger.debug(verity_config)
    verity.build_database()

    # app initialise
    app = Flask("Verity", static_folder="./front/static/")
    app.config["SECRET_KEY"] = verity_config.SECRET_KEY
    app.config["DEBUG"] = True
    app.register_blueprint(home_bp)
    app.run()
