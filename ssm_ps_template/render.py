import logging
import os
import pathlib
import typing
from urllib import parse

import yaml
from jinja2 import sandbox

from ssm_ps_template import ssm

LOGGER = logging.getLogger(__name__)


class Renderer:

    def __init__(self, source: pathlib.Path):
        with source.open('r') as handle:
            self._source = handle.read()
        self._values: typing.Optional[ssm.Values] = None

    def render(self, values: ssm.Values) -> str:
        """Render the template to the internal buffer"""
        self._values = values
        environment = sandbox.ImmutableSandboxedEnvironment()
        environment.globals['get_parameter'] = self._get_parameter
        environment.globals['get_parameters_by_path'] = \
            self._get_parameters_by_path
        environment.filters['toyaml'] = lambda v: yaml.safe_dump(v)
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
                                default: typing.Optional[str] = None) \
            -> typing.Optional[dict]:
        return self._values.parameters_by_path.get(path, default)
