# SSM Parameter Store Template

Command line application to render templates with data from SSM Parameter Store

## Installation

The `ssm-ps-template` application is available via the [Python Package Index](https://pypi.org/project/ssm-ps-template/) and can be installed with pip:

```bash
pip install ssm-ps-template
```

## Templating

The application uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) for the templating engine.

## Configuration

The configuration file provides the ability to specify multiple templates, override AWS configuration, and change logging levels:

### Top-Level Configuration Directives

| Directive   | Description                                                                                                                      |
|-------------|----------------------------------------------------------------------------------------------------------------------------------|
| `templates` | An array of template directives as detailed in the next table.                                                                   |
| `profile`   | Specify the AWS profile to use. If unspecified will default to the `AWS_DEFAULT_PROFILE` environment variable or is unspecified  |
| `region`    | Specify the AWS region to use. If unspecified it will default to the `AWS_DEFAULT_REGION` environment variable or is unspecified |
| `verbose`   | Turn debug logging on. Possible values are `true` and `false`                                                                    |

### Template Configuration Directives

The `templates` directive in the configuration is an array of objects, defined by a `source` and `destination`.

| Directive     | Description                                            |
|---------------|--------------------------------------------------------|
| `source`      | The source file of the template                        |
| `destination` | The destination path to write the rendered template to |

### Configuration File Format

The application supports JSON, TOML, or YAML for configuration. The following example is in YAML:

### Example Configuration File

```yaml
templates:
  - source: /etc/ssm-templates/nginx-example
    destination: /etc/nginx/sites-available/example
  - source: /etc/ssm-templates/postgres-example
    destination: /etc/postgresql/14/main/postgresql.conf
profile: default
region: us-east-1
verbose: false
```

## Command Line Usage

```
usage: ssm-ps-template [-h] [--aws-profile AWS_PROFILE] [--aws-region AWS_REGION] [--verbose] config

Templating for SSM Parameter Store

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  --aws-profile AWS_PROFILE
                        AWS Profile
  --aws-region AWS_REGION
                        AWS Region
  --verbose
```
