import argparse
import pathlib
import unittest

from ssm_ps_template import config
from tests import utils


def relative_test_data_path(path: str) -> pathlib.Path:
    return pathlib.Path('tests') / (utils.TEST_DATA_PATH / path).relative_to(
        pathlib.Path(__file__).parent)


class TestCase1(unittest.TestCase):

    def setUp(self) -> None:
        self.expectation = config.Configuration(
            templates=[
                config.Template(
                    source=relative_test_data_path('config/case1a.tmpl'),
                    destination=pathlib.Path('build/case1a.out'),
                    prefix='/foo/bar/baz'),
                config.Template(
                    source=relative_test_data_path('config/case1b.tmpl'),
                    destination=pathlib.Path('build/case1b.out'),
                    prefix=None)],
            endpoint_url=None,
            profile=None,
            region=None,
            replace_underscores=False,
            verbose=False)

    def test_load_json_file(self):
        self.assertEqual(
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case1.json'),
            self.expectation)

    def test_load_toml_file(self):
        self.assertEqual(
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case1.toml'),
            self.expectation)

    def test_load_yaml_file(self):
        self.assertEqual(
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case1.yaml'),
            self.expectation)


class TestCase2(unittest.TestCase):

    def test_invalid_file_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case2d.ini')

    def test_missing_configuration(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case.yaml')

    def test_missing_template_destination(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case2a.yaml')

    def test_missing_templates(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case2b.yaml')

    def test_missing_template_source(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case2c.yaml')

    def test_missing_template_source_file(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file(
                utils.TEST_DATA_PATH / 'config/case2d.yaml')
