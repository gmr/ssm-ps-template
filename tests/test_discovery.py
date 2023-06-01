import dataclasses
import unittest

import yaml

from ssm_ps_template import discovery
from tests import utils


class DiscoveryTestCase(unittest.TestCase):

    def test_discovery(self) -> None:
        expectation_path = utils.TEST_DATA_PATH / 'discovery/expectations.yaml'
        with expectation_path.open('r') as handle:
            values = yaml.safe_load(handle)
        expectation = discovery.Variables(
            set(values['parameters']), set(values['parameters_by_path']))

        template_path = utils.TEST_DATA_PATH / 'discovery/template.yaml.j2'
        discoverer = discovery.VariableDiscovery(template_path)
        result = discoverer.discover()

        self.assertDictEqual(
            dataclasses.asdict(result),
            dataclasses.asdict(expectation))
