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
