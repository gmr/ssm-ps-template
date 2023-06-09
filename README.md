# SSM Parameter Store Template

Command line application to render templates with data from SSM Parameter Store

[![codecov](https://codecov.io/gh/gmr/ssm-ps-template/branch/main/graph/badge.svg?token=KGneS7mP9t)](https://codecov.io/gh/gmr/ssm-ps-template)

## Installation

The `ssm-ps-template` application is available via the [Python Package Index](https://pypi.org/project/ssm-ps-template/) and can be installed with pip:

```bash
pip install ssm-ps-template
```

## Templating

The application uses [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) for the templating engine. All functionality available to Jinja2 templates by default are exposed in the application.

### Using Prefixes

The application has a default prefix of `/` that is prepended to parameter names that do not start with a leading slash (`/`).

This functionality allows you to group your variables under a path prefix like `/my-application/settings` and then only refer to the individual key values like `password` instead of referencing the full path of `/my-application/settings/password`.

If you reference a parameter name with a leading slash it will not prepend the prefix to the parameter name.

### Getting Parameter Store Values

The application exposes `get_parameter(name: str, default: typing.Optional[str] = None)` in templates to access the values in SSM Parameter Store.

In the following example we assume there are Parameter Store values for the keys `/my-application/foo` and `/my-application/bar` and that the application is called with a prefix of `/my-appliction`:

```yaml
foo: {{ get_parameter('/my-application/foo') }}
bar: {{ get_parameter('/my-application/bar') }}
```

Will render as:

```yaml
foo: bar
baz: qux
```

Additionally, there is another function exposed `get_parameters_by_path(path: str, default: typing.Optional[dict] = None)` which will return a dictionary for the specified path.

The following example will iterate over the results:

```yaml
{% for key, value in get_parameters_by_path('settings/', {}).items() %}
  {{ key }}: {{ value }}
{% endfor %}
```

Or you can use Jinja filters to convert them to YAML:

```yaml
{{ get_parameters_by_path('settings/') | path_to_dict | toyaml | indent(2, first=True) }}
```

For values in ParameterStore that are stored as `StringList`, they are automatically transformed as a list of strings. Given the following value:

| Key                           | Value                            |
|-------------------------------|----------------------------------|
| `/my-application/connections` | `amqp://server1, amqp://server2` |

And the following template:

```yaml
Connections:
{% for connection in get_parameter('/my-application/connections', []) %}
  - {{ connection }}
```

The following would be rendered:

```yaml
Connections:
  - amqp://server1
  - amqp://server2
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

The `templates` directive in the configuration is an array of objects:

| Directive     | Description                                                                          |
|---------------|--------------------------------------------------------------------------------------|
| `source`      | The source file of the template                                                      |
| `destination` | The destination path to write the rendered template to                               |
| `prefix`      | The prefix to prepend variables with if they do not start with a forward-slash (`/`) |
| `user`        | An optional username or uid to set as the owner of the rendered file                 |
| `group`       | An optional group or gid to set as the group of the rendered file                    |
| `mode`        | Optional file mode and permissions set using chmod                                   |

If there are parent directories in the `destination` path that do not exist, they will be created.

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

| Filter                  | Description                                                                                                  |
|-------------------------|--------------------------------------------------------------------------------------------------------------|
| `coerce_types`          | Recursively cast bools, ints, and NULL from strings in data structures                                       |
| `dashes_to_underscores` | Recursively replaces dashes with underscores in keys in data structures returned by `get_parameters_by_path` |
| `fromjson`              | Convert a JSON blob to a data structure                                                                      |
| `fromyaml`              | Convert a YAML blob to a data structure                                                                      |
| `path_to_dict`          | Converts a dict with forward-slash delimited keys (`/`) to a nested dict using the `/` as the key delimiter  |
| `toyaml`                | Converts a dictionary value to YAML                                                                          |

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
    user: postgres
    group: postgres
    mode: 0600
profile: default
region: us-east-1
verbose: false
```

## Command Line Usage

```sh
usage: ssm-ps-template [-h] [--aws-profile AWS_PROFILE] [--aws-region AWS_REGION] [--endpoint-url ENDPOINT_URL] [--prefix PREFIX] [--replace-underscores]
                       [--verbose] [--version]
                       config

Command line application to render templates with data from SSM Parameter Store

positional arguments:
  config

optional arguments:
  -h, --help            show this help message and exit
  --aws-profile AWS_PROFILE
                        AWS Profile (default: None)
  --aws-region AWS_REGION
                        AWS Region (default: None)
  --endpoint-url ENDPOINT_URL
                        Specify an endpoint URL to use when contacting SSM Parameter Store. (default: None)
  --prefix PREFIX       Default SSM Key Prefix (default: /)
  --replace-underscores
                        Replace underscores in variable names to dashes when looking for values in SSM (default: False)
  --verbose
  --version             show program's version number and exit
```

Note that the default SSM prefix can also be set with the `PARAMS_PREFIX` environment variable and
the endpoint URL setting cn be set with the `SSM_ENDPOINT_URL` environment variable.
