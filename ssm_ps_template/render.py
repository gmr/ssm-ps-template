import enum
import io
import logging
import pathlib
import typing

import jinja2
from jinja2 import sandbox

LOGGER = logging.getLogger(__name__)


class DiscoveryMode(enum.Enum):
    SIMPLE = 1
    COMPOUND = 2


class Renderer:

    def __init__(self, source: pathlib.Path):
        with source.open('r') as handle:
            self._source = handle.read()
        self._buffer = io.StringIO()
        self._variables = set({})

    def discover_variables(self) -> typing.List[str]:
        """Discover the variables that to look up in SSM Parameter Store

        Supports "fake" compound variables for SSM namespacing like:

            `{{ foo/bar/baz }}`

        """
        environment = sandbox.ImmutableSandboxedEnvironment()
        body = environment.preprocess(self._source)
        tokens = list(environment.lex(body))
        mode, variable = DiscoveryMode.SIMPLE, []
        for offset, token in enumerate(tokens):
            if mode == DiscoveryMode.SIMPLE \
                    and token[1] == 'operator' \
                    and token[2] == '/':
                LOGGER.debug('Starting COMPOUND mode')
                mode = DiscoveryMode.COMPOUND
                variable = [token[2]]
            elif mode == DiscoveryMode.COMPOUND \
                    and token[1] == 'operator' \
                    and token[2] == '/' or token[2] == '-':
                LOGGER.debug('Ignoring / operator in COMPOUND mode')
                variable.append(token[2])
            elif mode == DiscoveryMode.SIMPLE \
                    and token[1] == 'name' \
                    and self._next_is_compound_operator(offset, tokens):
                LOGGER.debug('Starting COMPOUND mode')
                mode = DiscoveryMode.COMPOUND
                variable = [token[2]]
            elif mode == DiscoveryMode.COMPOUND \
                    and token[1] == 'name' \
                    and not self._next_is_compound_operator(offset, tokens):
                LOGGER.debug('Finishing COMPOUND mode')
                variable.append(token[2])
                self._variables.add(''.join(variable))
                mode = DiscoveryMode.SIMPLE
            elif mode == DiscoveryMode.COMPOUND and token[1] == 'name':
                LOGGER.debug('Appending token in COMPOUND: %s', token[2])
                variable.append(token[2])
            elif mode == DiscoveryMode.SIMPLE and token[1] == 'name':
                LOGGER.debug('Appending variable in SIMPLE: %s', token[2])
                self._variables.add(token[2])
        return list(self._variables)

    def render(self, values: typing.Dict) -> str:
        """Render the template to the internal buffer"""
        variables = {}
        for key, value in values.items():
            variables[self._sanitize_variable(key)] = value
        return jinja2.Template(
            self._patched_source(), autoescape=True).render(**variables)

    @staticmethod
    def _next_is_compound_operator(
            offset: int,
            tokens: typing.List[typing.Tuple[int, str, str]]) -> bool:
        """Check to see if the next token is a compound operator"""
        return tokens[offset + 1][1] == 'operator' \
            and (tokens[offset + 1][2] == '/' or tokens[offset + 1][2] == '-')

    def _patched_source(self) -> str:
        """Replace `foo/bar/baz` variables with `foo__bar__baz`"""
        source = str(self._source)
        for var in list(self._variables):
            if var != self._sanitize_variable(var):
                source = source.replace(var, self._sanitize_variable(var))
        return source

    @staticmethod
    def _sanitize_variable(value: str) -> str:
        return value.replace('/', '___').replace('-', '_')
