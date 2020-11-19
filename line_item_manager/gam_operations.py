from googleads import ad_manager
from typing import Tuple

from .config import config

log = config.getLogger('operations')

_CREATE_LOG_LINE = 'Create: "%s" w/ Rec(s): "%s"'
_QUERY_LOG_LINE = 'Service: "%s" Method: "%s" Params: "%s"'
_FETCH_ONE_LOG_LINE = 'Service: "%s" Method: "%s" Fetch One: "%s"'
_RESULTS_LOG_LINE = 'Service: "%s" Method: "%s" Results: "%s"'

class GAMOperations:
    service = ''
    method = ''
    create_method = ''
    query_fields: Tuple = ()
    create_fields: Tuple = ()

    def __init__(self, *args, **kwargs):
        self.params = kwargs
        self.query_params = {k:kwargs[k] for k in self.query_fields if k in kwargs} \
          if self.query_fields else self.params
        self.create_params = {k:kwargs[k] for k in self.create_fields if k in kwargs} \
          if self.create_fields else self.params

    def create(self, atts, validate=False):
        log.info(_CREATE_LOG_LINE, type(self).__name__, atts)
        results = self.dry_run_recs(atts) if self.dry_run else \
          getattr(self.svc(), self.create_method)(atts)
        if validate:
            self.validate(atts, results)
        return results

    def fetch(self, one=False, create=False, recs=None, validate=False):
        results = self._results(one=one)
        if create and recs:
            current = {self.check(r_) for r_ in results}
            new_recs = [r_ for r_ in recs if self.check(r_) not in current]
            if new_recs:
                results += self.create(new_recs)
        elif create and not results:
            results = self.create([self.create_params])[0]
        if validate:
            self.validate(recs, results)
        return results

    def fetchone(self, **kwargs):
        return self.fetch(one=True, **kwargs)

    def _results(self, one=False):
        log.debug(_QUERY_LOG_LINE, self.service, self.method, self.query_params)
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
                    log.debug(_FETCH_ONE_LOG_LINE, self.service, self.method, result)
                    return result
                results.append(result)
            _stm.offset += _stm.limit
        log.debug(_RESULTS_LOG_LINE, self.service, self.method, results)
        return results

    def statement(self):
        if not self.query_params:
            return None
        _stm = ad_manager.StatementBuilder(version=self.version)
        _stm.Where(' AND '.join([f"{k} = :{k}" for k in self.query_params]))
        _ = [_stm.WithBindVariable(k, v) for k, v in self.query_params.items()]
        return _stm

    def svc(self):
        return self.client.GetService(self.service, version=self.version)

    def validate(self, recs, results):
        raise NotImplementedError

    def check(self, rec):
        raise NotImplementedError

    @property
    def dry_run_recs(self):
        raise NotImplementedError

    @property
    def client(self):
        raise NotImplementedError

    @property
    def version(self):
        raise NotImplementedError

    @property
    def dry_run(self):
        raise NotImplementedError
