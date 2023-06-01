import dataclasses
import os
import uuid
from unittest import mock

from botocore import exceptions

from ssm_ps_template import discovery, ssm
from tests import utils


class ParameterStoreTestCase(utils.ParameterStoreTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ssm = ssm.ParameterStore(
            endpoint_url=os.environ['SSM_ENDPOINT_URL'])

    def test_fetch_variables(self):
        values = {
            '/foo/bar/baz': str(uuid.uuid4()),
            '/foo/bar/corgie_qux': str(uuid.uuid4()),
            '/foo/bar/settings/value1': str(uuid.uuid4()),
            '/foo/bar/settings/value2': str(uuid.uuid4())
        }
        self.put_parameters(values)
        self.put_parameter('/foo/bar/list_value', ['foo', 'bar', 'baz'])

        variables = discovery.Variables(
            {'baz', 'corgie_qux', 'list_value'}, {'settings/'})
        result = self.ssm.fetch_variables(variables, '/foo/bar', False)

        expectation = ssm.Values(
            {
                'baz': values['/foo/bar/baz'],
                'corgie_qux': values['/foo/bar/corgie_qux'],
                'list_value': ['foo', 'bar', 'baz']
            },
            {
                'settings/': {
                    'value1': values['/foo/bar/settings/value1'],
                    'value2': values['/foo/bar/settings/value2']
                }
            })

        self.assertDictEqual(
            dataclasses.asdict(result), dataclasses.asdict(expectation))

    def test_fetch_variables_with_dashes(self):
        values = {
            '/foo/bar/baz': str(uuid.uuid4()),
            '/foo/bar/corgie-qux': str(uuid.uuid4()),
            '/foo/bar/app-settings/value1': str(uuid.uuid4()),
            '/foo/bar/app-settings/value2': str(uuid.uuid4()),
            '/other-prefix/value': str(uuid.uuid4())
        }
        self.put_parameters(values)

        variables = discovery.Variables(
            {'baz', 'corgie_qux', '/other-prefix/value'}, {'app_settings/'})
        result = self.ssm.fetch_variables(variables, '/foo/bar', True)

        expectation = ssm.Values(
            {
                'baz': values['/foo/bar/baz'],
                'corgie_qux': values['/foo/bar/corgie-qux'],
                '/other-prefix/value': values['/other-prefix/value']
            },
            {
                'app_settings/': {
                    'value1': values['/foo/bar/app-settings/value1'],
                    'value2': values['/foo/bar/app-settings/value2']
                }
            })

        self.assertDictEqual(
            dataclasses.asdict(result), dataclasses.asdict(expectation))

    def test_fetch_variables_raises(self):
        with mock.patch(
                'ssm_ps_template.ssm.ParameterStore._fetch_variables') as func:
            func.side_effect = exceptions.ClientError(
                error_response={'err': 'Mock Error'},
                operation_name='Mock Operation')
            with self.assertRaises(ssm.SSMClientException):
                self.ssm.fetch_variables(
                    discovery.Variables(set(), set()), '/foo/bar', True)
