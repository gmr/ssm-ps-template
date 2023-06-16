import grp
import os
import pathlib
from unittest import mock

import yaml

from ssm_ps_template import __main__, ssm
from tests import utils


def delete_folder(path):
    if path.exists():
        for sub in path.iterdir():
            if sub.is_dir():
                delete_folder(sub)
            else:
                sub.unlink()
        path.rmdir()


class MainTestCase(utils.ParameterStoreTestCase):

    def test_render_templates(self):
        output_dir = pathlib.Path('./build/test').resolve()
        delete_folder(output_dir)

        with (utils.TEST_DATA_PATH / 'main/data.yaml').open('r') as handle:
            self.put_parameters(yaml.safe_load(handle))

        args = __main__.parse_cli_arguments([
            '--prefix', '/my-application',
            str(utils.TEST_DATA_PATH / 'main/config.toml')])

        __main__.render_templates(args)

        result_path = output_dir / 'main-test.yaml'
        self.assertEqual(result_path.stat().st_mode, 33152)  # 0o600

        expectation = utils.TEST_DATA_PATH / 'main/expectation.yaml'

        self.assertEqual(
            result_path.read_text('utf-8').strip(),
            expectation.read_text('utf-8').strip())

        # Run a second time for branch coverage
        __main__.render_templates(args)

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

    def test_chown_group(self):
        gids = os.getgroups()
        path = pathlib.Path('build/test-chown-group')
        path.write_text('test-data')

        __main__.chown(str(path), None, gids[0])
        self.assertEqual(path.stat().st_gid, gids[0])

        __main__.chown(str(path), None, grp.getgrgid(gids[1]).gr_name)
        self.assertEqual(path.stat().st_gid, gids[1])

    def test_chown_user(self):
        # This is a noop but will test the code branch
        uid = os.getuid()
        path = pathlib.Path('build/test-chown-user')
        path.write_text('test-data')

        __main__.chown(str(path), uid, None)
        self.assertEqual(path.stat().st_uid, uid)

        try:
            __main__.chown(str(path), os.getlogin(), None)
        except OSError:
            # Fails on GitHub Actions with "unable to determine login name"
            pass
        else:
            self.assertEqual(path.stat().st_uid, uid)
