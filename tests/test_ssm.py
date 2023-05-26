import os
import pathlib
import uuid
import unittest

import boto3
import flatdict

from ssm_ps_template import ssm


def load_test_env() -> None:
    path = pathlib.Path('build/test.env')
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
        self.ssm = ssm.ParameterStore(endpoint_url=os.environ['ENDPOINT_URL'])
        self.values = {
            '/foo/bar/baz': str(uuid.uuid4()),
            '/my-app/settings/value1': str(uuid.uuid4()),
            '/my-app/settings/value2': str(uuid.uuid4())
        }
        self.string_list_values = {
            '/my-string/list/value1': [str(uuid.uuid4()), str(uuid.uuid4())],
            '/my-string/list/value2': [str(uuid.uuid4()), str(uuid.uuid4())]
        }

        client = boto3.client('ssm', endpoint_url=os.environ['ENDPOINT_URL'])
        for key, value in self.values.items():
            client.put_parameter(Name=key, Value=value, Type='String')

        for key, value in self.string_list_values.items():
            client.put_parameter(
                Name=key, Value=','.join(value), Type='StringList')

    def tearDown(self) -> None:
        client = boto3.client('ssm', endpoint_url=os.environ['ENDPOINT_URL'])
        client.delete_parameters(Names=list(self.values.keys()))
        client.delete_parameters(Names=list(self.string_list_values.keys()))
        super().tearDown()

    def test_fetch_variables(self):
        values = self.ssm.fetch_variables([
            '/foo/bar/baz',
            'settings/'], prefix='/my-app/')
        recast = {
            '/foo/bar/baz': values['/foo/bar/baz'],
            '/my-app/settings/value1': values['settings/']['value1'],
            '/my-app/settings/value2': values['settings/']['value2']
        }
        self.assertDictEqual(recast, self.values)

        values = self.ssm.fetch_variables(
            ['list/'], prefix='/my-string/')
        recast = {
            '/my-string/list/value1': values['list/']['value1'],
            '/my-string/list/value2': values['list/']['value2']
        }
        self.assertDictEqual(recast, self.string_list_values)
