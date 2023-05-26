import os
import pathlib
import typing
import unittest
import uuid

import boto3

from ssm_ps_template import ssm


def load_test_env() -> None:
    path = pathlib.Path('build/test.env')
    if not path.exists():
        path = pathlib.Path('../build/test.env')
        if not path.exists():
            raise RuntimeError('Failed to find test.env file')
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
    def setUp(self) -> None:
        super().setUp()
        load_test_env()
        self.client = boto3.client(
            'ssm', endpoint_url=os.environ['ENDPOINT_URL'])
        self.ssm = ssm.ParameterStore(endpoint_url=os.environ['ENDPOINT_URL'])
        self.ssm_keys = set({})

    def tearDown(self) -> None:
        self.prune_parameters()
        super().tearDown()

    def prune_parameters(self) -> None:
        if self.ssm_keys:
            client = boto3.client(
                'ssm', endpoint_url=os.environ['ENDPOINT_URL'])
            client.delete_parameters(Names=list(self.ssm_keys))

    def put_parameter(self, key: str, value: str,
                      parameter_type: str = 'String'):
        self.ssm_keys.add(key)
        self.client.put_parameter(Name=key, Value=value, Type=parameter_type)

    def put_parameters(self, values: dict, parameter_type='String'):
        for key, value in values.items():
            self.put_parameter(key, value, parameter_type)

    @staticmethod
    def flatten(values: dict, prefix: typing.Optional[str] = '') -> dict:
        output = {}
        for key, value in values.items():
            if prefix and not key.startswith('/'):
                key = f'{prefix.rstrip("/")}/{key}'
            if isinstance(value, dict):
                for child_key, child_value in value.items():
                    full_key = f'{key.rstrip("/")}/{child_key}'
                    if isinstance(child_value, list):
                        child_value = ','.join(child_value)
                    output[full_key.rstrip('/')] = child_value
            elif isinstance(value, list):
                output[key.rstrip('/')] = ','.join(value)
            else:
                output[key.rstrip('/')] = value
        return output

    def test_fetch_variables(self):
        expectation = {
            '/foo/bar/baz': str(uuid.uuid4()),
            '/foo/bar/corgie_qux': str(uuid.uuid4()),
            '/my_app/settings/value1': str(uuid.uuid4()),
            '/my_app/settings/value2': str(uuid.uuid4())
        }
        self.put_parameters(expectation)
        result = self.ssm.fetch_variables(
            ['/foo/bar/baz', '/foo/bar/corgie_qux', 'settings/'],
            '/my_app/', False)
        self.assertDictEqual(self.flatten(result, '/my_app/'), expectation)

    def test_fetch_variables_replacing_underscore(self):
        self.prune_parameters()
        values = {
            '/foo/bar/baz/qux': str(uuid.uuid4()),
            '/foo/bar/baz/quux': str(uuid.uuid4()),
            '/the-app/settings/value1': str(uuid.uuid4()),
            '/the-app/settings/value2': str(uuid.uuid4())
        }
        self.put_parameters(values)
        result = self.ssm.fetch_variables(
            ['/foo/bar/baz/qux', '/foo/bar/baz/quux', 'settings/'],
            '/the_app/', True)
        self.assertDictEqual(self.flatten(result, '/the-app/'), values)

    def test_fetch_variables_string_list(self):
        expectation = {
            '/my_string/list/value1': ','.join(
                [str(uuid.uuid4()), str(uuid.uuid4())]),
            '/my_string/list/value2': ','.join(
                [str(uuid.uuid4()), str(uuid.uuid4())])
        }
        self.put_parameters(expectation, 'StringList')
        result = self.ssm.fetch_variables(['list/'], '/my_string/', False)
        self.assertDictEqual(self.flatten(result, '/my_string/'), expectation)

    def test_fetch_variables_string_list_replace_underscore(self):
        expectation = {
            '/my-string/list/value1': ','.join(
                [str(uuid.uuid4()), str(uuid.uuid4())]),
            '/my-string/list/value2': ','.join(
                [str(uuid.uuid4()), str(uuid.uuid4())])
        }
        self.put_parameters(expectation, 'StringList')
        result = self.ssm.fetch_variables(['list/'], '/my_string/', True)
        self.assertDictEqual(self.flatten(result, '/my-string/'), expectation)
