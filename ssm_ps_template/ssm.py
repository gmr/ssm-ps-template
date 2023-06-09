import dataclasses
import logging
import typing

import boto3
from botocore import exceptions

from ssm_ps_template import discovery

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Values:
    parameters: typing.Dict[str, str]
    parameters_by_path: typing.Dict[str, typing.Dict[str, str]]


class ParameterStore:

    def __init__(self,
                 profile: typing.Optional[str] = None,
                 region: typing.Optional[str] = None,
                 endpoint_url: typing.Optional[str] = None):
        self._session = boto3.Session(profile_name=profile, region_name=region)
        self._client = self._session.client('ssm', endpoint_url=endpoint_url)
        self._ssm = boto3.client('ssm')

    def fetch_variables(self,
                        variables: discovery.Variables,
                        prefix: str,
                        replace_underscores: bool) -> Values:
        try:
            return self._fetch_variables(
                variables, prefix, replace_underscores)
        except (exceptions.ClientError,
                exceptions.UnauthorizedSSOTokenError) as err:
            raise SSMClientException(str(err))

    def _fetch_variables(self,
                         variables: discovery.Variables,
                         prefix: str,
                         replace_underscores: bool) -> Values:
        values = Values({}, {})

        names, name_map = self._build_names(
            variables.parameters, prefix, replace_underscores)

        LOGGER.debug('Fetching Parameters %r', names)
        while names:
            response = self._client.get_parameters(
                Names=names[:10], WithDecryption=True)
            for param in response['Parameters']:
                values.parameters[name_map[param['Name']]] = \
                    self._parameter_value(param)
            names = names[10:]

        names, name_map = self._build_names(
            variables.parameters_by_path, prefix, replace_underscores)
        for key in name_map.values():
            values.parameters_by_path[key] = {}

        LOGGER.debug('Fetching Parameters By Path %r', names)
        paginator = self._client.get_paginator('get_parameters_by_path')
        for name in names:
            for page in paginator.paginate(
                    Path=name, Recursive=True, WithDecryption=True):
                for param in page['Parameters']:
                    key = param['Name'][len(name):]
                    values.parameters_by_path[name_map[name]][key] = \
                        self._parameter_value(param)

        return values

    @staticmethod
    def _build_names(variables: set,
                     prefix: str,
                     replace_underscores: bool) \
            -> typing.Tuple[typing.List[str], typing.Dict[str, str]]:
        names, name_map = [], {}
        for param in variables:
            value = param.replace('_', '-') if replace_underscores else param
            name = value if value.startswith('/') else f'{prefix}/{value}'
            name_map[name] = param
            names.append(name)
        return names, name_map

    @staticmethod
    def _parameter_value(parameter: dict) \
            -> typing.Union[str, typing.List[str]]:
        if parameter['Type'] == 'StringList':
            return [value.strip() for value in parameter['Value'].split(',')]
        return parameter['Value'].rstrip()


class SSMClientException(Exception):
    pass
