import argparse
import dataclasses
import json
import pathlib
import typing

import toml
import yaml


@dataclasses.dataclass
class Template:
    source: pathlib.Path
    destination: pathlib.Path
    prefix: typing.Optional[str]
    user: typing.Union[int, str, None]
    group: typing.Union[int, str, None]
    mode: typing.Optional[str]


@dataclasses.dataclass
class Configuration:
    endpoint_url: typing.Optional[str]
    profile: typing.Optional[str]
    region: typing.Optional[str]
    replace_underscores: typing.Optional[bool]
    templates: list[Template]
    verbose: bool


def _load_configuration(value: dict) -> Configuration:
    templates = []
    try:
        for template in value['templates'] or []:
            mode = int(template.get('mode'), 8) \
                if template.get('mode') else None
            templates.append(_entry_to_template(
                source=template['source'],
                destination=template['destination'],
                prefix=template.get('prefix'),
                user=template.get('user'),
                group=template.get('group'),
                mode=mode))
    except KeyError as error:
        raise argparse.ArgumentTypeError(
            f'Failed to load configuration due to invalid key: {error}')
    return Configuration(
        endpoint_url=value.get('endpoint_url'),
        profile=value.get('profile'),
        region=value.get('region'),
        replace_underscores=value.get('replace_underscores', False),
        templates=templates,
        verbose=value.get('verbose', False))


def _entry_to_template(**kwargs) -> Template:
    source = pathlib.Path(kwargs['source'])
    if not source.exists():
        raise argparse.ArgumentTypeError(
            f'Specified template {source} does not exist')
    return Template(source=source,
                    destination=pathlib.Path(kwargs['destination']),
                    prefix=kwargs['prefix'],
                    user=kwargs['user'],
                    group=kwargs['group'],
                    mode=kwargs['mode'])


def configuration_file(value: str) -> Configuration:
    """Load the configuration from the specified path"""
    path = pathlib.Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(f'{value} does not exist')

    if str(path).endswith('.json'):
        with path.open('r') as handle:
            return _load_configuration(json.load(handle))
    if str(path).endswith('.toml'):
        with path.open('r') as handle:
            return _load_configuration(toml.load(handle))
    if str(path).endswith('.yaml') or str(path).endswith('.yml'):
        with path.open('r') as handle:
            return _load_configuration(yaml.safe_load(handle))

    raise argparse.ArgumentTypeError(f'{value} is not an understood file type')
