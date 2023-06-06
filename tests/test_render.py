import unittest

import yaml

from ssm_ps_template import render, ssm
from tests import utils


class DiscoveryTestCase(unittest.TestCase):

    def test_render(self):
        with (utils.TEST_DATA_PATH / 'render/values.yaml').open() as handle:
            data = yaml.safe_load(handle)

        values = ssm.Values(
            parameters=data['parameters'],
            parameters_by_path=data['parameters_by_path'])

        renderer = render.Renderer(
            utils.TEST_DATA_PATH / 'render/template.yaml.j2')
        result = renderer.render(values)

        path = utils.TEST_DATA_PATH / 'render/expectation.yaml'
        expectation = path.read_text('utf-8')
        self.assertEqual(result.strip(), expectation.strip())


class DashesToUnderscoresTestCase(unittest.TestCase):

    def test_replace_dashes_with_underscores(self):
        value = {
            'foo-bar': 'baz',
            'qux': {
                'quux-corgie': 'grault'
            },
            'quux-corgie': [
                {'grault-garply': 'waldo'},
                {'fred-plugh': 'xyzzy'}
            ],
            'grault': [
                'garply', 'waldo'
            ]
        }
        expectation = {
            'foo_bar': 'baz',
            'qux': {
                'quux_corgie': 'grault'
            },
            'quux_corgie': [
                {'grault_garply': 'waldo'},
                {'fred_plugh': 'xyzzy'},
            ],
            'grault': [
                'garply', 'waldo'
            ]
        }
        self.assertDictEqual(
            render.replace_dashes_with_underscores(value), expectation)

    def test_raises_on_bad_data_type(self):
        with self.assertRaises(TypeError):
            render.replace_dashes_with_underscores('foo')


class PathToDictTestCase(unittest.TestCase):

    def test_path_to_dict(self):
        value = {
            'foo/bar/baz': 'qux',
            'foo/bar/qux': 'quux'
        }
        expectation = {
            'foo': {
                'bar': {
                    'baz': 'qux',
                    'qux': 'quux'
                }
            }
        }
        self.assertDictEqual(render.path_to_dict(value), expectation)
