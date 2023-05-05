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

    def fetch_variables(self, variables: list) -> typing.Dict[str, str]:
        response = self._client.get_parameters(
            Names=list(variables), WithDecryption=True)
        return {param['Name']: param['Value']
                for param in response['Parameters']}
