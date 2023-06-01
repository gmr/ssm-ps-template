from unittest import mock

import yaml

from ssm_ps_template import __main__, ssm
from tests import utils


class MainTestCase(utils.ParameterStoreTestCase):

    def test_render_templates(self):

        with (utils.TEST_DATA_PATH / 'main/data.yaml').open('r') as handle:
            self.put_parameters(yaml.safe_load(handle))

        args = __main__.parse_cli_arguments([
            '--prefix', '/my-application',
            str(utils.TEST_DATA_PATH / 'main/config.toml')])

        __main__.render_templates(args)

        with open('build/main-test.yaml', 'r') as handle:
            result = handle.read()

        with (utils.TEST_DATA_PATH / 'main/expectation.yaml').open() as handle:
            expectation = handle.read()

        self.assertEqual(result.strip(), expectation.strip())

    def test_ssm_error_exits(self):
        args = __main__.parse_cli_arguments([
            '--prefix', '/my-application',
            str(utils.TEST_DATA_PATH / 'main/config.toml')])

        with mock.patch(
                'ssm_ps_template.ssm.ParameterStore.fetch_variables') as func:
            func.side_effect = ssm.SSMClientException('Mock Error')
            with self.assertRaises(SystemExit) as system_exit:
                __main__.render_templates(args)
            self.assertEqual(str(system_exit.exception), '1')
