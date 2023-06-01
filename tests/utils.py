import os
import pathlib
import sys
import typing
import unittest

import boto3

TEST_PATH = pathlib.Path(__file__).parent
TEST_DATA_PATH = TEST_PATH / 'data'


def load_test_env() -> typing.NoReturn:
    path = TEST_PATH / '../build/test.env'
    if not path.exists():
        sys.stderr.write('Failed to find test.env.file\n')
        return
    try:
        with path.open('r') as f:
            for line in f:
                if line.startswith('export '):
                    line = line[7:]
                name, _, value = line.strip().partition('=')
                os.environ[name] = value
    except IOError:
        pass


class ParameterStoreTestCase(unittest.TestCase):
    def setUp(self) -> typing.NoReturn:
        super().setUp()
        load_test_env()
        self.client = boto3.client(
            'ssm', endpoint_url=os.environ['SSM_ENDPOINT_URL'])
        self.ssm_keys = set()

    def tearDown(self) -> typing.NoReturn:
        self.prune_parameters()
        super().tearDown()

    def prune_parameters(self) -> typing.NoReturn:
        if self.ssm_keys:
            client = boto3.client(
                'ssm', endpoint_url=os.environ['SSM_ENDPOINT_URL'])
            client.delete_parameters(Names=list(self.ssm_keys))

    def put_parameter(self, key: str,
                      value: typing.Union[str, typing.List[str]]) \
            -> typing.NoReturn:
        self.ssm_keys.add(key)
        if isinstance(value, list):
            self.client.put_parameter(
                Name=key, Value=','.join(value), Type='StringList')
        else:
            self.client.put_parameter(Name=key, Value=value, Type='String')

    def put_parameters(self, values: dict) -> typing.NoReturn:
        for key, value in values.items():
            self.put_parameter(key, value)
