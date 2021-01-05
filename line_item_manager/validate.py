from typing import Generator

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

class Validator:
    """A schema validator helper."""

    def __init__(self, schema: dict, config: dict):
        """Initialize Validator.

        Args:
          schema: validation schema
          config: config object to be validated
        """
        self.inst = Draft7Validator(schema)
        self.config = config

    def is_valid(self) -> bool:
        """Get boolean specifying if the config is valid.

        Returns:
          True if config is valid otherwise False
        """
        return self.inst.is_valid(self.config)

    def errors(self) -> Generator[ValidationError, None, None]:
        """Get iterator of errors from config validation.

        Returns:
          An iterator of all errors
        """
        return self.inst.iter_errors(self.config)

    def fmt(self, _e: ValidationError) -> str:
        """Format of an error showing the path and message.

        Args:
          _e: validation error

        Returns:
          A formatted string of the validation error
        """
        return f"Path({', '.join([str(_p) for _p in _e.path])}): {_e.message}"
