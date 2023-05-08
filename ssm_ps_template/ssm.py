import logging
import typing

import boto3

LOGGER = logging.getLogger(__name__)


class ParameterStore:

    def __init__(self,
                 profile: typing.Optional[str] = None,
                 region: typing.Optional[str] = None):
        self._session = boto3.Session(profile_name=profile, region_name=region)
        self._client = self._session.client('ssm')

    def fetch_variables(self,
                        variables: list,
                        prefix: typing.Optional[str]) -> typing.Dict[str, str]:
        # Build the variables
        names = ['/'.join([prefix.rstrip('/'), v])
                 if prefix and not v.startswith('/') else v for v in variables]

        LOGGER.debug('Fetching %r', names)

        values = {}
        while names:
            response = self._client.get_parameters(
                Names=names[:10],
                WithDecryption=True)

            # Strip the prefix if needed
            for param in response['Parameters']:
                # LOGGER.debug('Param %r', param)
                name = param['Name']
                if name.startswith(prefix) and name not in variables:
                    name = name[len(prefix):]
                if param['Type'] == 'StringList':
                    values[name] = [p for p in param['Value'].split(',')
                                    if p.strip()]
                    LOGGER.debug('%s = %r', name, values[name])
                else:
                    values[name] = param['Value'].rstrip()
            names = names[10:]
        LOGGER.debug('Returning %r', values)
        return values
