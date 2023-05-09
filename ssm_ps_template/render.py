import io
import logging
import os
import pathlib
import typing
from urllib import parse

from jinja2 import sandbox
import yaml

LOGGER = logging.getLogger(__name__)


class Renderer:

    def __init__(self, source: pathlib.Path, variables: typing.List[str]):
        with source.open('r') as handle:
            self._source = handle.read()
        self._buffer = io.StringIO()
        self._variables = variables

    def render(self, values: typing.Dict) -> str:
        """Render the template to the internal buffer"""
        environment = sandbox.ImmutableSandboxedEnvironment()
        environment.filters['toyaml'] = lambda v: yaml.safe_dump(v)
        environment.globals['parse_qs'] = parse.parse_qs
        environment.globals['unquote'] = parse.unquote
        environment.globals['urlparse'] = parse.urlparse

        variables = {}
        for key in self._variables:
            variables[self._sanitize_variable(key)] = values.get(key)
        variables['environ'] = os.environ

        template = environment.from_string(self._patched_source())
        return template.render(**variables)

    def _patched_source(self) -> str:
        """Replace `foo/bar/baz` variables with `foo__bar__baz`"""
        source = str(self._source)
        for var in self._variables:
            if var != self._sanitize_variable(var):
                source = source.replace(var, self._sanitize_variable(var))
        return source

    @staticmethod
    def _sanitize_variable(value: str) -> str:
        return value.replace('/', '___').replace('-', '_')
