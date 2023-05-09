import pathlib
import unittest

from ssm_ps_template import discover


class DiscoverVariablesTestCase(unittest.TestCase):

    def test_case1a(self):
        variables = discover.Variables(
            pathlib.Path('tests/templates/case1a.tmpl'))
        values = variables.discover()
        self.assertListEqual(sorted(values),
                             ['complex/', 'foo/bar/baz', 'ssm_variable'])
