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


@dataclasses.dataclass
class Configuration:
    templates: list[Template]
    profile: typing.Optional[str]
    region: typing.Optional[str]
    verbose: bool


def _load_configuration(value: dict) -> Configuration:
    try:
        return Configuration(
            templates=[_entry_to_template(**template)
                       for template in value['templates']],
            profile=value.get('profile'),
            region=value.get('region'),
            verbose=value.get('verbose', False))
    except KeyError as error:
        raise argparse.ArgumentTypeError(
            f'Failed to load configuration due to invalid key: {error}')


def _entry_to_template(**kwargs) -> Template:
    source = pathlib.Path(kwargs['source'])
    if not source.exists():
        raise argparse.ArgumentTypeError(
            f'Specified template {source} does not exist')
    return Template(
        source=source,
        destination=pathlib.Path(kwargs['destination']))


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
