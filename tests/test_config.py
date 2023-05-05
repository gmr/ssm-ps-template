import argparse
import pathlib
import unittest

from ssm_ps_template import config


class TestCase1(unittest.TestCase):

    def setUp(self) -> None:
        self.expectation = config.Configuration(
            templates=[
                config.Template(
                    source=pathlib.Path('tests/templates/case1a.tmpl'),
                    destination=pathlib.Path('build/case1a.out')),
                config.Template(
                    source=pathlib.Path('tests/templates/case1b.tmpl'),
                    destination=pathlib.Path('build/case1b.out')),
            ],
            profile=None,
            region=None,
            verbose=False)

    def test_load_json_file(self):
        self.assertEqual(
            config.configuration_file('tests/config/case1.json'),
            self.expectation)

    def test_load_toml_file(self):
        self.assertEqual(
            config.configuration_file('tests/config/case1.toml'),
            self.expectation)

    def test_load_yaml_file(self):
        self.assertEqual(
            config.configuration_file('tests/config/case1.yaml'),
            self.expectation)


class TestCase2(unittest.TestCase):

    def test_invalid_file_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case2d.ini')

    def test_missing_configuration(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case.yaml')

    def test_missing_template_destination(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case2a.yaml')

    def test_missing_templates(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case2b.yaml')

    def test_missing_template_source(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case2c.yaml')

    def test_missing_template_source_file(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            config.configuration_file('tests/config/case2d.yaml')
