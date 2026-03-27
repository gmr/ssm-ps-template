import os
import pathlib
import sys
import unittest

import boto3

TEST_PATH = pathlib.Path(__file__).parent
TEST_DATA_PATH = TEST_PATH / 'data'


def load_test_env() -> None:
    path = TEST_PATH / '../build/test.env'
    if not path.exists():
        sys.stderr.write('Failed to find test.env.file\n')
        return
    try:
        with path.open('r') as f:
            for line in f:
                line = line.removeprefix('export ')
                name, _, value = line.strip().partition('=')
                os.environ[name] = value
    except OSError:
        pass


class ParameterStoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        load_test_env()
        self.client = boto3.client(
            'ssm', endpoint_url=os.environ['SSM_ENDPOINT_URL']
        )
        self.ssm_keys = set()

    def tearDown(self) -> None:
        self.prune_parameters()
        super().tearDown()

    def prune_parameters(self) -> None:
        if self.ssm_keys:
            client = boto3.client(
                'ssm', endpoint_url=os.environ['SSM_ENDPOINT_URL']
            )
            client.delete_parameters(Names=list(self.ssm_keys))

    def put_parameter(self, key: str, value: str | list[str]) -> None:
        self.ssm_keys.add(key)
        if isinstance(value, list):
            self.client.put_parameter(
                Name=key, Value=','.join(value), Type='StringList'
            )
        else:
            self.client.put_parameter(Name=key, Value=value, Type='String')

    def put_parameters(self, values: dict) -> None:
        for key, value in values.items():
            self.put_parameter(key, value)
