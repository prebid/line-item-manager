from jsonschema import Draft7Validator

class Validator:
    def __init__(self, schema, config):
        self.inst = Draft7Validator(schema)
        self.config = config

    def is_valid(self):
        return self.inst.is_valid(self.config)

    def errors(self):
        return self.inst.iter_errors(self.config)

    def fmt(self, _e):
        return f"Path({', '.join([str(_p) for _p in _e.path])}): {_e.message}"
