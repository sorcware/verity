import logging

logger = logging.getLogger(__name__)

# TODO: Make this into a proper class so we can scale currrency handling


class CurrencyBrain:
    def convert_to_universal_currency(input_value: float) -> int:
        """
        Converts the the input value to remove all decimal places and return an int.
        This will be the starting point for our universal currency,
        (see docs/data_dictionary).
        for now, we will just focus on making this an int.
        it will need change later once we have the basics done
        """
        logger.info(f"received {input_value} to convert to universal currency")
        input_value = float(input_value)
        while input_value % 1 != 0:
            logger.debug(f"input value is not a whole number {input_value}")
            input_value = input_value * 10
        logger.info(f"returning {int(input_value)}")
        return int(input_value)
