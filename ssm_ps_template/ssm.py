import logging
import typing

import boto3
import flatdict

LOGGER = logging.getLogger(__name__)


class ParameterStore:

    def __init__(self,
                 profile: typing.Optional[str] = None,
                 region: typing.Optional[str] = None):
        self._session = boto3.Session(profile_name=profile, region_name=region)
        self._client = self._session.client('ssm')
        self._ssm = boto3.client('ssm')

    def fetch_variables(self, variables: list,
                        prefix: typing.Optional[str]) -> typing.Dict[str, str]:
        # Build the variables
        names = [
            '/'.join([prefix.rstrip('/'), v])
            if prefix and not v.startswith('/') else v for v in variables
        ]

        paths = [name for name in names if name.endswith('/')]
        names = [name for name in names if not name.endswith('/')]

        LOGGER.debug('Fetching %r', names)

        values = {}
        while names:
            response = self._client.get_parameters(Names=names[:10],
                                                   WithDecryption=True)

            for param in response['Parameters']:
                values = self.add_parameter(param, prefix, variables, values)
            names = names[10:]

        path_values = flatdict.FlatDict(delimiter='/')
        for path in paths:
            paginator = self._client.get_paginator('get_parameters_by_path')
            for page in paginator.paginate(Path=path,
                                           Recursive=True,
                                           WithDecryption=True):
                for param in page['Parameters']:
                    LOGGER.debug('Param %r', param)
                    path_values = self.add_parameter(param, prefix, variables,
                                                     path_values)
        for key, value in path_values.as_dict().items():
            values[f'{key}/'] = value

        LOGGER.debug('Returning %r', values)
        return values

    @staticmethod
    def add_parameter(param: dict,
                      prefix: str,
                      variables: typing.List[str],
                      values: typing.Union[dict, flatdict.FlatDict]) \
            -> dict:
        """Process a parameter, stripping prefix if needed and coercing
        StringList to a list of strings.

        """
        if param['Name'].startswith(prefix) and param['Name'] not in variables:
            param['Name'] = param['Name'][len(prefix):]
        if param['Type'] == 'StringList':
            values[param['Name']] = [
                p for p in param['Value'].split(',') if p.strip()
            ]
            LOGGER.debug('%s = %r', param['Name'], values[param['Name']])
        else:
            values[param['Name']] = param['Value'].rstrip()
        return values
