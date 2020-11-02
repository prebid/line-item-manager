from googleads import ad_manager

class ResourceNotFound(Exception):
    """
    Raised when specified resource is not found
    """

class GAMOperations:
    service = None
    method = None
    create_method = None

    def __init__(self, *args, **kwargs):
        self.params = kwargs

    def fetch(self, one=False, create=False, validate=False):
        result = self._results(one=one)
        if not result and create:
            result = self._create()[0]
        if validate:
            self.validate(result)
        return result

    def _results(self, one=False):
        _stm = self.statement()
        if not _stm:
            return getattr(self.svc(), self.method)()
        results = []
        while True:
            response = getattr(self.svc(), self.method)(_stm.ToStatement())
            if not ("results" in response and response["results"]):
                break
            for result in response["results"]:
                if one:
                    return result
                results.append(result)
            _stm.offset += _stm.limit
        return results

    def create_template(self):
        keys = self.create_args or self.key_words.keys()
        return {k: self.key_words[k] for k in keys}

    def _create(self):
        return self.create([self.create_template()])

    def create(self, atts):
        return getattr(self.svc(), self.create_method)(atts)

    def validate(self, result):
        if not result:
            raise ResourceNotFound('Service: {self.service_name}, Method: {self.method}, Atts: {self.key_words}')

    def fetchone(self):
        return self.fetch(one=True)

    def svc(self):
        return self.client.GetService(self.service, version=self.version)

    def statement(self):
        if not self.params:
            return None
        _stm = ad_manager.StatementBuilder(version=self.version)
        _stm.Where(' AND '.join([f"{k} = :{k}" for k in self.params]))
        _ = [_stm.WithBindVariable(k, v) for k, v in self.params.items()]
        return _stm

    @property
    def client(self):
        raise NotImplementedError

    @property
    def version(self):
        raise NotImplementedError

    @property
    def dry_run(self):
        raise NotImplementedError

