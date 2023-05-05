import pathlib
import unittest

from ssm_ps_template import render


class DiscoverVariablesTestCase(unittest.TestCase):

    def test_case1a(self):
        renderer = render.Renderer(
            pathlib.Path('tests/templates/case1a.tmpl'))
        variables = renderer.discover_variables()
        self.assertListEqual(sorted(variables),
                             ['foo/bar/baz', 'ssm_variable'])


class RenderingTestCase(unittest.TestCase):

    def test_case1a(self):
        renderer = render.Renderer(
            pathlib.Path('tests/templates/case1a.tmpl'))
        renderer.discover_variables()
        output = renderer.render({
            'ssm_variable': 'Variable',
            'foo/bar/baz': 'Corgie!'})
        with open('tests/expectations/case1a.out', 'r') as handle:
            expectation = handle.read()
        self.assertEqual(output.strip(), expectation.strip())

    def test_case1b(self):
        renderer = render.Renderer(
            pathlib.Path('tests/templates/case1b.tmpl'))
        renderer.discover_variables()
        output = renderer.render({
            '/foo/bar/baz': 'postgresql://localhost:5432/postgres',
            '/qux/corgie': 'redis://localhost:6379/0'})
        with open('tests/expectations/case1b.out', 'r') as handle:
            expectation = handle.read()
        self.assertEqual(output.strip(), expectation.strip())
