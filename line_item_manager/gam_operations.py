from pprint import pformat
from typing import Any, List, Optional, Tuple

from googleads import ad_manager
from googleads.common import ZeepServiceProxy
import yaml

from .config import config, VERBOSE2
from line_item_manager.utils import load_package_file

logger = config.getLogger('operations')

_CREATE_LOG_LINE = 'Create: "%s" w/ Rec(s):\n"%s"'
_QUERY_LOG_LINE = 'Service: "%s" Method: "%s" Params:\n"%s"'
_RESULTS_LOG_LINE = 'Service: "%s" Method: "%s" Results:\n"%s"'

def client(network_code: int, key_file: str) -> ad_manager.AdManagerClient:
    _cfg = load_package_file('googleads.yaml')
    _cfg['ad_manager']['network_code'] = network_code
    _cfg['ad_manager']['path_to_private_key_file'] = key_file
    return ad_manager.AdManagerClient.LoadFromString(yaml.dump(_cfg))

class GAMOperations:
    service: str = ''
    method: str = ''
    create_method: str = ''
    query_fields: Optional[Tuple[str, ...]] = None
    create_fields: Optional[Tuple[str, ...]] = None
    log_fields: Optional[Tuple[str, ...]] = None
    use_statement = True

    def __init__(self, **kwargs):
        self.params = kwargs
        self.query_params = {k:kwargs[k] for k in self.query_fields if k in kwargs} \
          if self.query_fields else self.params
        self.create_params = {k:kwargs[k] for k in self.create_fields if k in kwargs} \
          if self.create_fields else self.params

    def create(self, atts: List[dict], validate: bool=False, verbose: bool=True) -> List[dict]:
        logger.log(VERBOSE2, _CREATE_LOG_LINE, type(self).__name__, pformat(self.log_recs(atts)))
        results = self.dry_run_recs(atts) if self.dry_run else \
          getattr(self.svc(), self.create_method)(atts)
        if verbose:
            logger.log(VERBOSE2, _RESULTS_LOG_LINE, self.service, self.method, pformat(results))
        if validate:
            self.validate(atts, results)
        return results

    def fetch(self, one: bool=False, create: bool=False, recs: List[dict]=None,
              validate: bool=False) -> List[dict]:
        logger.log(VERBOSE2, _QUERY_LOG_LINE, self.service, self.method, pformat(self.query_params))
        results = self._results(one=one)
        if create and recs:
            current = {self.check(r_) for r_ in results}
            new_recs = [r_ for r_ in recs if self.check(r_) not in current]
            if new_recs:
                results += self.create(new_recs, verbose=False)
        elif create and not results:
            results = self.create([self.create_params], verbose=False)
        logger.log(VERBOSE2, _RESULTS_LOG_LINE, self.service, self.method, pformat(results))
        if validate:
            self.validate(recs, results)
        return results

    def fetchone(self, **kwargs) -> dict:
        recs = self.fetch(one=True, **kwargs)
        return recs[0] if recs else {}

    def _results(self, one: bool=False) -> List[dict]:
        if not self.use_statement:
            return [getattr(self.svc(), self.method)()]
        _stm = self.statement()
        results = []
        while True:
            response = getattr(self.svc(), self.method)(_stm.ToStatement())
            if not ("results" in response and response["results"]):
                break
            for result in response["results"]:
                if one:
                    return [result]
                results.append(result)
            if len(results) < _stm.limit:
                break
            _stm.offset += _stm.limit
        return results

    def statement(self) -> ad_manager.StatementBuilder:
        _stm = ad_manager.StatementBuilder(version=self.version)
        if self.query_params:
            _stm.Where(' AND '.join([f"{k} = :{k}" for k in self.query_params]))
            _ = [_stm.WithBindVariable(k, v) for k, v in self.query_params.items()]
        return _stm

    def svc(self) -> ZeepServiceProxy:
        return self.client.GetService(self.service, version=self.version) # type: ignore[union-attr]

    def log_recs(self, recs: List[dict]) -> List[dict]:
        if self.log_fields:
            return [{f_:r_[f_] for f_ in self.log_fields if f_ in r_} for r_ in recs]
        return recs

    @property
    def client(self) -> Optional[ad_manager.AdManagerClient]:
        raise NotImplementedError

    @property
    def version(self) -> str:
        raise NotImplementedError

    @property
    def dry_run(self) -> bool:
        raise NotImplementedError

    def dry_run_recs(self, recs: List[dict]) -> List[dict]:
        raise NotImplementedError

    def check(self, rec: dict) -> Any:
        raise NotImplementedError

    def validate(self, recs, results):
        raise NotImplementedError
