import dataclasses
import enum
import logging
import pathlib
import typing

from jinja2 import sandbox

LOGGER = logging.getLogger(__name__)

GET_PARAMETER = 'get_parameter'
GET_PARAMETERS_BY_PATH = 'get_parameters_by_path'
FUNCTIONS = {GET_PARAMETER, GET_PARAMETERS_BY_PATH}


class State(enum.Enum):
    OFF = 0
    BLOCK_PENDING = 1


@dataclasses.dataclass
class Variables:
    parameters: set
    parameters_by_path: set


class VariableDiscovery:
    """Reads the template and parses out the variables to fetch"""

    def __init__(self, source: pathlib.Path):
        env = sandbox.ImmutableSandboxedEnvironment()
        with source.open('r') as handle:
            self._tokens = list(env.lex(env.preprocess(handle.read())))
        self._offset = 0

    def discover(self) -> Variables:
        """Discover the variables that to look up in SSM Parameter Store"""
        variable_type, state = None, State.OFF
        variables = Variables(set(), set())
        for (line_no, ident, value) in self.tokens():
            if state == State.OFF and ident == 'name' and value in FUNCTIONS:
                state = State.BLOCK_PENDING
                variable_type = value
            elif state == State.BLOCK_PENDING and ident == 'string':
                value = value.strip('"').strip("'")
                if variable_type == GET_PARAMETER:
                    variables.parameters.add(value)
                elif variable_type == GET_PARAMETERS_BY_PATH:
                    variables.parameters_by_path.add(value)
                state, variable_type = State.OFF, None
        return variables

    def tokens(self) \
            -> typing.Generator[typing.Tuple[int, str, str], None, None]:
        while self._offset < len(self._tokens):
            yield self._tokens[self._offset]
            self._offset += 1
