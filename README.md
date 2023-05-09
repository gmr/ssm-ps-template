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

| Directive     | Description                                                                          |
|---------------|--------------------------------------------------------------------------------------|
| `source`      | The source file of the template                                                      |
| `destination` | The destination path to write the rendered template to                               |
| `prefix`      | The prefix to prepend variables with if they do not start with a forward-slash (`/`) |

### Extended Templating Functionality

In addition to the base functionality exposed by Jinja2, the following Python functions have been added:

| Function   | Definition                                                                                                                                          |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `urlparse` | The [`urllib.parse.urlparse`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse) function from the Python standard library. |
| `parse_qs` | The [`urllib.parse.parse_qs`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs) function from the Python standard library. |
| `unquote`  | The [`urllib.parse.unquote`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.unquote) function from the Python standard library.   |

The following filters are added:

| Filter   | Description                         |
|----------|-------------------------------------|
| `toyaml` | Converts a dictionary value to YAML |

The following variables are exposed:

| Variable  | Definition                                                                                                              |
|-----------|-------------------------------------------------------------------------------------------------------------------------|
| `environ` | The [`os.environ`](https://docs.python.org/3/library/os.html#os.environ) dictionary for accessing environment variables |

### Configuration File Format

The application supports JSON, TOML, or YAML for configuration. The following example is in YAML:

### Example Configuration File

```yaml
templates:
  - source: /etc/ssm-templates/nginx-example
    destination: /etc/nginx/sites-available/example
    prefix: /namespaced/application/nginx/
  - source: /etc/ssm-templates/postgres-example
    destination: /etc/postgresql/14/main/postgresql.conf
    prefix: /namespaced/application/postgres/
profile: default
region: us-east-1
verbose: false
```

## Path Based Dictionaries

In more complex templates it's possible to need a dictionary of values from SSM instead of straight key/value usage.

This is achieved by setting a variable to a key with a trailing slash (`/`).

The following pattern will retrieve all keys under a path and return them as a nested dictionary with a `/` delimiter,
and then iterate over the key/value pairs:

```
{% set values = settings/ %}
{% for key, value in settings.items() %}
  {{ key }}: {{ value }}
{% endfor %}
```

Or to convert them to YAML:

```
settings: {% set values = settings/ %}
{{ values | toyaml | indent(2, first=True) }}
```

## Command Line Usage

```
usage: ssm-ps-template [-h] [--aws-profile AWS_PROFILE] [--aws-region AWS_REGION] [--prefix] [--verbose] config
Templating for SSM Parameter Store

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  --aws-profile AWS_PROFILE
                        AWS Profile
  --aws-region AWS_REGION
                        AWS Region
  --prefix              Default SSM Key Prefix
  --verbose
```
