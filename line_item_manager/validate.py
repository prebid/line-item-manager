from typing import Generator

from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

class Validator:
    def __init__(self, schema: dict, config: dict):
        self.inst = Draft7Validator(schema)
        self.config = config

    def is_valid(self) -> bool:
        return self.inst.is_valid(self.config)

    def errors(self) -> Generator[ValidationError, None, None]:
        return self.inst.iter_errors(self.config)

    def fmt(self, _e: ValidationError) -> str:
        return f"Path({', '.join([str(_p) for _p in _e.path])}): {_e.message}"
