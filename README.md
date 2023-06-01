# SSM Parameter Store Template

Command line application to render templates with data from SSM Parameter Store

## Installation

The `ssm-ps-template` application is available via the [Python Package Index](https://pypi.org/project/ssm-ps-template/) and can be installed with pip:

```bash
pip install ssm-ps-template
```

## Templating

The application uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) for the templating engine. All functionality available to Jinja2 templates by default are exposed in the application.

### Getting Parameter Store Values

The application exposes `get_parameter(name: str, default: typing.Optional[str] = None)` in templates to access the values in SSM Parameter Store.

In the following example we assume there are Parameter Store values for the keys `/my-application/foo` and `/my-application/bar` and that the application is called with a prefix of `/my-appliction`:

```yaml
foo: {{ get_parameter('/my-application/foo'}}
bar: {{ get_parameter('/my-application/bar'}}
```
Will render as:
```yaml
foo: bar
baz: qux
```

Additionally, there is another function exposed `get_parameters_by_path(path: str, default: typing.Optional[str] = None)` which will return a dictionary for the specified path.

The following example will iterate over the results:
```
{% for key, value in get_parameters_by_path('settings/').items() %}
  {{ key }}: {{ value }}
{% endfor %}
```

Or you can use a Jinja filter to convert them to YAML:
```
{{ get_parameters_by_path('settings/') | toyaml | indent(2, first=True) }}
```

### Performance Considerations

The parameter names are gathered in a pre-processing step to minimize calls to SSM Parameter Store.

## Configuration

The configuration file provides the ability to specify multiple templates, override AWS configuration, and change logging levels:

### Top-Level Configuration Directives

| Directive             | Description                                                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------|
| `templates`           | An array of template directives as detailed in the next table.                                                                   |
| `endpoint_url`        | Specify an endpoint URL to use to override the default URL used to contact SSM Parameter Store                                   |
| `profile`             | Specify the AWS profile to use. If unspecified will default to the `AWS_DEFAULT_PROFILE` environment variable or is unspecified  |
| `region`              | Specify the AWS region to use. If unspecified it will default to the `AWS_DEFAULT_REGION` environment variable or is unspecified |
| `replace_underscores` | Replace underscores with dashes when asking for values from SSM Parameter Store                                                  |
| `verbose`             | Turn debug logging on. Possible values are `true` and `false`                                                                    |

### Template Configuration Directives

The `templates` directive in the configuration is an array of objects, defined by a `source` and `destination`.

| Directive     | Description                                                                          |
|---------------|--------------------------------------------------------------------------------------|
| `source`      | The source file of the template                                                      |
| `destination` | The destination path to write the rendered template to                               |
| `prefix`      | The prefix to prepend variables with if they do not start with a forward-slash (`/`) |

### Extended Templating Functionality

In addition to the base functionality exposed by Jinja2, the following Python functions have been added:

| Function                 | Definition                                                                                                                                          |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `get_parameter`          | Get a string value from SSM Parameter Store                                                                                                         |
| `get_parameters_by_path` | Get a dictionary value from SSM Parameter Store                                                                                                     |
| `urlparse`               | The [`urllib.parse.urlparse`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse) function from the Python standard library. |
| `parse_qs`               | The [`urllib.parse.parse_qs`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs) function from the Python standard library. |
| `unquote`                | The [`urllib.parse.unquote`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.unquote) function from the Python standard library.   |

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

## Command Line Usage

```
usage: ssm-ps-template [-h] [--aws-profile AWS_PROFILE] [--aws-region AWS_REGION] [--prefix PREFIX] [--verbose] config

Templating for SSM Parameter Store

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  --aws-profile AWS_PROFILE
                        AWS Profile
  --aws-region AWS_REGION
                        AWS Region
  --endpoint-url SSM_ENDPOINT_URL
                        Specify an endpoint URL to use when contacting SSM Parameter Store.
  --prefix PREFIX       Default SSM Key Prefix
  --replace-underscores
                        Replace underscores in variable names to dashes when looking for values in SSM
  --verbose
```
Note that the default SSM prefix can also be set with the `PARAMS_PREFIX` environment variable and
the endpoint URL setting cn be set with the `SSM_ENDPOINT_URL` environment variable.
