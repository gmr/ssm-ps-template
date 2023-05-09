import pathlib
import unittest

import yaml

from ssm_ps_template import discover, render


class RenderingTestCase(unittest.TestCase):

    def test_case1a(self):
        variables = discover.Variables(
            pathlib.Path('tests/templates/case1a.tmpl'))
        renderer = render.Renderer(pathlib.Path('tests/templates/case1a.tmpl'),
                                   list(variables.discover()))

        output = renderer.render({
            'ssm_variable': 'Variable',
            'foo/bar/baz': 'Corgie!',
            'complex/': {
                'foo': 'bar',
                'baz': 'corgie'
            }
        })
        with open('tests/expectations/case1a.out', 'r') as handle:
            expectation = handle.read()

        value = yaml.safe_load(output)
        expected = yaml.safe_load(expectation)
        self.assertDictEqual(value, expected)
        self.assertEqual(
            output.split('\n')[0].strip(),
            expectation.split('\n')[0].strip())

    def test_case1b(self):
        variables = discover.Variables(
            pathlib.Path('tests/templates/case1b.tmpl'))
        renderer = render.Renderer(pathlib.Path('tests/templates/case1b.tmpl'),
                                   list(variables.discover()))
        output = renderer.render({
            '/foo/bar/baz': 'postgresql://localhost:5432/postgres',
            '/qux/corgie': 'redis://localhost:6379/0'
        })
        with open('tests/expectations/case1b.out', 'r') as handle:
            expectation = handle.read()
        self.assertEqual(output.strip(), expectation.strip())
