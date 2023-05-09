import enum
import logging
import pathlib
import typing

from jinja2 import sandbox

LOGGER = logging.getLogger(__name__)


class State(enum.Enum):
    OFF = 0
    BLOCK_PENDING = 1
    BLOCK_ENDING = 2
    PROCESSING = 3
    COLLECTING = 4
    DEFINING = 5
    LOOPING = 6


BLOCK_BEGIN = 'block_begin'
BLOCK_END = 'block_end'
VARIABLE_BEGIN = 'variable_begin'
VARIABLE_END = 'variable_end'

KEYWORDS = {
    'and', 'in', 'or', 'if', 'else', 'not', 'set', 'loop.last', 'none', 'int',
    'True', 'False', 'toyaml'
}


class Variables:
    """Reads the template and parses out the variables to fetch"""

    def __init__(self, source: pathlib.Path):
        env = sandbox.ImmutableSandboxedEnvironment()
        with source.open('r') as handle:
            self._tokens = list(env.lex(env.preprocess(handle.read())))
        self._offset = 0

    def discover(self,
                 depth=0,
                 state=State.OFF,
                 ignore: typing.Optional[set] = None) -> typing.Set[str]:
        """Discover the variables that to look up in SSM Parameter Store

        Supports "fake" compound variables for SSM namespacing like:

            `{{ foo/bar/baz }}`

        """
        LOGGER.debug('In self.discover(%i, %s)', depth, state)
        if ignore is None:
            ignore = set({})
        variables = set({})

        for (line_no, ident, value) in self.tokens():
            if ident in ['data']:
                continue

            LOGGER.debug('D %s> %r, %r', line_no, ident, value)

            if ident == BLOCK_BEGIN:
                state = State.BLOCK_PENDING
            elif ident == BLOCK_END:
                state = State.OFF
            elif ident == VARIABLE_BEGIN:
                LOGGER.debug('Starting variable in %s', state)
                values = self._collect_value(ignore)
                remove = set({})
                for word in ignore:
                    for variable in values:
                        if variable.startswith(f'{word}.'):
                            remove.add(variable)
                variables |= values - remove

            elif state == State.BLOCK_PENDING and value == 'for':
                LOGGER.debug('Recursing, values at start %r', variables)
                self._offset += 1
                discovered = self.discover(depth + 1, State.LOOPING) - ignore
                remove = set({})
                for variable in discovered:
                    for word in ignore:
                        if variable.startswith(f'{word}.'):
                            remove.add(variable)
                variables |= discovered - remove
                LOGGER.debug('After recursing, values %r - %r - %r', variables,
                             ignore, remove)
                state = State.OFF
            elif state == State.BLOCK_PENDING and value == 'endif':
                state = State.OFF
            elif state == State.BLOCK_PENDING and value == 'endfor':
                break
            elif state == State.BLOCK_PENDING and value == 'set':
                self._offset += 1
                variables |= self._collect_value(ignore)
                state = State.OFF
            elif state == State.LOOPING:
                for (_line_no, sub_ident, sub_value) in self.tokens():
                    if sub_ident == 'whitespace':
                        LOGGER.debug('Skipping whitespace')
                        continue
                    if sub_ident == 'name' and sub_value == 'in':
                        self._offset += 1
                        variables |= self._collect_value(ignore)
                        state = State.OFF
                        break
                    elif sub_ident == 'name':
                        LOGGER.debug('Adding %r to ignore', sub_value)
                        ignore.add(sub_value)

        return variables - ignore

    def _collect_value(self, ignore, stop_on_keyword=False) -> typing.Set[str]:
        parts = []
        values = set({})
        for (line_no, ident, value) in self.tokens():
            LOGGER.debug('C %s > %r %r', line_no, ident, value)
            if ident == 'operator':
                if value in ['.', '-', '/']:
                    parts.append(value)
                elif value in ('=', '==', '!='):
                    val = ''.join(parts)
                    LOGGER.debug('Ignoring assignment previous parts: %r', val)
                    ignore.add(val)
                    LOGGER.debug('Ignore now %r', ignore)
                    parts = []
                elif value == '(':
                    LOGGER.debug('Discarding previous parts')
                    parts = []
                elif value in [')', ',', '|', '%']:
                    val = ''.join(parts)
                    if self._should_add_variable(val) and val not in ignore:
                        values.add(val)
                    parts = []
            elif ident == 'name':
                if stop_on_keyword and value in KEYWORDS:
                    break
                parts.append(value)
            elif ident == BLOCK_END:
                break
            elif ident == VARIABLE_END:
                break
        val = ''.join(parts)
        if self._should_add_variable(val) and val not in ignore:
            values.add(val)
        return values

    @staticmethod
    def _should_add_variable(value: str) -> bool:
        return value and value not in KEYWORDS

    def tokens(
            self) -> typing.Generator[typing.Tuple[int, str, str], None, None]:
        while self._offset < len(self._tokens):
            yield self._tokens[self._offset]
            self._offset += 1
