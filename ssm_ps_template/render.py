import json
import logging
import os
import pathlib
import typing
from urllib import parse

import flatdict
import yaml
from jinja2 import sandbox

from ssm_ps_template import ssm

LOGGER = logging.getLogger(__name__)


def path_to_dict(value: dict) -> dict:
    flat = flatdict.FlatDict(value, delimiter='/')
    return flat.as_dict()


def replace_dashes_with_underscores(value_in: typing.Union[dict, list]) \
        -> typing.Union[dict, list]:
    if isinstance(value_in, dict):
        output = {}
        for key, value in value_in.items():
            new_key = key.replace('-', '_')
            if isinstance(value, (dict, list)):
                output[new_key] = replace_dashes_with_underscores(value)
            else:
                output[new_key] = value
        return output
    elif isinstance(value_in, list):
        output = []
        for value in value_in:
            if isinstance(value, (dict, list)):
                output.append(replace_dashes_with_underscores(value))
            else:
                output.append(value)
        return output
    else:
        raise TypeError('Method invoked with incorrect data type')


class Renderer:

    def __init__(self, source: pathlib.Path):
        with source.open('r') as handle:
            self._source = handle.read()
        self._values: typing.Optional[ssm.Values] = None

    def render(self, values: ssm.Values) -> str:
        """Render the template to the internal buffer"""
        self._values = values
        environment = sandbox.ImmutableSandboxedEnvironment()
        environment.filters['dashes_to_underscores'] = \
            replace_dashes_with_underscores
        environment.filters['fromjson'] = lambda v: json.loads(v)
        environment.filters['fromyaml'] = lambda v: yaml.safe_load(v)
        environment.filters['path_to_dict'] = path_to_dict
        environment.filters['toyaml'] = lambda v: yaml.safe_dump(v)
        environment.globals['get_parameter'] = self._get_parameter
        environment.globals['get_parameters_by_path'] = \
            self._get_parameters_by_path
        environment.globals['parse_qs'] = parse.parse_qs
        environment.globals['unquote'] = parse.unquote
        environment.globals['urlparse'] = parse.urlparse
        return environment.from_string(self._source).render(
            **{'environ': os.environ})

    def _get_parameter(self,
                       key: str,
                       default: typing.Optional[str] = None) \
            -> typing.Optional[str]:
        return self._values.parameters.get(key, default)

    def _get_parameters_by_path(self,
                                path: str,
                                default: typing.Optional[dict] = None) \
            -> typing.Optional[dict]:
        return self._values.parameters_by_path.get(path, default)
