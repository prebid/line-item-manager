from pprint import pformat

from googleads import ad_manager

from .config import config, VERBOSE2

logger = config.getLogger('operations')

_CREATE_LOG_LINE = 'Create: "%s" w/ Rec(s):\n"%s"'
_QUERY_LOG_LINE = 'Service: "%s" Method: "%s" Params:\n"%s"'
_RESULTS_LOG_LINE = 'Service: "%s" Method: "%s" Results:\n"%s"'

class GAMOperations:
    service = ''
    method = ''
    create_method = ''
    query_fields = None
    create_fields = None
    log_fields = None

    def __init__(self, **kwargs):
        self.params = kwargs
        self.query_params = {k:kwargs[k] for k in self.query_fields if k in kwargs} \
          if self.query_fields else self.params
        self.create_params = {k:kwargs[k] for k in self.create_fields if k in kwargs} \
          if self.create_fields else self.params

    def create(self, atts, validate=False, verbose=True):
        logger.log(VERBOSE2, _CREATE_LOG_LINE, type(self).__name__, pformat(self.log_recs(atts)))
        results = self.dry_run_recs(atts) if self.dry_run else \
          getattr(self.svc(), self.create_method)(atts)
        if verbose:
            logger.log(VERBOSE2, _RESULTS_LOG_LINE, self.service, self.method, pformat(results))
        if validate:
            self.validate(atts, results)
        return results

    def fetch(self, one=False, create=False, recs=None, validate=False):
        logger.log(VERBOSE2, _QUERY_LOG_LINE, self.service, self.method, pformat(self.query_params))
        results = self._results(one=one)
        if create and recs:
            current = {self.check(r_) for r_ in results}
            new_recs = [r_ for r_ in recs if self.check(r_) not in current]
            if new_recs:
                results += self.create(new_recs, verbose=False)
        elif create and not results:
            results = self.create([self.create_params], verbose=False)[0]
        logger.log(VERBOSE2, _RESULTS_LOG_LINE, self.service, self.method, pformat(results))
        if validate:
            self.validate(recs, results)
        return results

    def fetchone(self, **kwargs):
        return self.fetch(one=True, **kwargs)

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
            if len(results) < _stm.limit:
                break
            _stm.offset += _stm.limit
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

    def log_recs(self, recs):
        if self.log_fields:
            return [{f_:r_[f_] for f_ in self.log_fields if f_ in r_} for r_ in recs]
        return recs

    @property
    def client(self):
        raise NotImplementedError

    @property
    def version(self):
        raise NotImplementedError

    @property
    def dry_run(self):
        raise NotImplementedError

    @property
    def dry_run_recs(self):
        raise NotImplementedError

    def check(self, rec):
        raise NotImplementedError

    def validate(self, recs, results):
        raise NotImplementedError
