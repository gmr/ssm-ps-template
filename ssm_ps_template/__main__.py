import argparse
from importlib import metadata
import logging
import time

from ssm_ps_template import config, render, ssm

LOGGER = logging.getLogger(__name__)


def parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Templating for SSM Parameter Store')
    parser.add_argument('--aws-profile', action='store', help='AWS Profile')
    parser.add_argument('--aws-region', action='store', help='AWS Region')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('config', type=config.configuration_file, nargs=1)
    return parser.parse_args()


def main():
    args = parse_cli_arguments()
    verbose = args.config[0].verbose or args.verbose
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    LOGGER.info('ssm-ps-template v%s', metadata.version('ssm-ps-template'))
    parameter_store = ssm.ParameterStore(
        profile=args.aws_profile or args.config[0].profile,
        region=args.aws_region or args.config[0].region)
    start_time = time.time()
    for template in args.config[0].templates:
        renderer = render.Renderer(
            source=template.source)
        variables = renderer.discover_variables()
        LOGGER.debug('Variables: %r', variables)
        values = parameter_store.fetch_variables(variables)
        with template.destination.open('w') as handle:
            handle.write(renderer.render(values))
        LOGGER.info('Rendered %s in %0.2f seconds',
                    template.destination, time.time() - start_time)
