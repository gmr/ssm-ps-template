import argparse
import logging
import os
import sys
import time
import typing
from importlib import metadata

from botocore import exceptions

from ssm_ps_template import config, discover, render, ssm

LOGGER = logging.getLogger(__name__)


def parse_cli_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Templating for SSM Parameter Store')
    parser.add_argument('--aws-profile', action='store', help='AWS Profile')
    parser.add_argument('--aws-region', action='store', help='AWS Region')
    parser.add_argument('--endpoint-url', action='store',
                        help=('Specify an endpoint URL to use when contacting '
                              'SSM Parameter Store.'),
                        default=os.environ.get('ENDPOINT_URL'))
    parser.add_argument('--prefix', action='store',
                        help='Default SSM Key Prefix',
                        default=os.environ.get('PARAMS_PREFIX', ''))
    parser.add_argument('--replace-underscores', action='store_true',
                        help=('Replace underscores in variable names to dashes'
                              ' when looking for values in SSM'))
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('config', type=config.configuration_file, nargs=1)
    return parser.parse_args()


def render_templates(args: argparse.Namespace) -> typing.NoReturn:
    parameter_store = ssm.ParameterStore(
        profile=args.aws_profile or args.config[0].profile,
        region=args.aws_region or args.config[0].region,
        endpoint_url=args.endpoint_url or args.config[0].endpoint_url)

    start_time = time.time()
    for template in args.config[0].templates:
        if not args.prefix and not template.prefix:
            LOGGER.error('The prefix for %s must not be empty.',
                         template.source)
            sys.exit(1)

        prefix = args.prefix or template.prefix
        if not prefix.endswith('/'):
            prefix = f'{args.prefix}/'

        variable_discovery = discover.Variables(template.source)
        variables = sorted(variable_discovery.discover())

        try:
            values = parameter_store.fetch_variables(
                variables, prefix, args.replace_underscores)
        except (exceptions.ClientError,
                exceptions.UnauthorizedSSOTokenError) as err:
            LOGGER.error('Error fetching parameters: %s', err)
            sys.exit(2)

        renderer = render.Renderer(source=template.source, variables=variables)
        with template.destination.open('w') as handle:
            handle.write(renderer.render(values))

        LOGGER.info('Rendered %s in %0.2f seconds', template.destination,
                    time.time() - start_time)


def main():
    args = parse_cli_arguments()

    verbose = args.config[0].verbose or args.verbose
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    for logger in ['boto3', 'botocore', 'urllib3']:
        logging.getLogger(logger).setLevel(logging.INFO)

    LOGGER.info('ssm-ps-template v%s', metadata.version('ssm-ps-template'))
    render_templates(args)
