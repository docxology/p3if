# P3IF Installation Guide

## System requirements

P3IF requires Python 3.13 or later. The repository selects Python 3.13 for local
checkouts and tracks its dependencies in `uv.lock`. [Python pin](../../.python-version) ·
[Package metadata](../../pyproject.toml) · [Dependency lock](../../uv.lock)

## Install from a local checkout

With Git and uv available, run this from the repository root to install the
package and its runtime dependencies.

```sh
uv sync --locked --no-dev
```

For development, run `uv sync --locked` to include the default development
requirements. The package guide also documents editable installation with pip.
[Package guide](../package-guide.md#quick-start)

## Verification

From the repository root, check the installed CLI and validate the tracked
interchange example.

```sh
uv run --no-sync p3if --version
uv run --no-sync p3if validate examples/interchange/framework-v1.json
```

After the development install, run `uv run --no-sync pytest tests/` to use the
repository test suite.

## Configuration

The interchange CLI reads the local JSON snapshot supplied on the command line.
The Python configuration utility accepts an explicit JSON configuration path.
[Interchange guide](../interchange.md) · [Configuration utility](../../src/p3if/utils/config.py)

## Updating P3IF

After updating your checkout, rerun the `uv sync` command you used to install it.
Then run the CLI checks above to verify the refreshed environment.

## Troubleshooting

Check the interpreter in the project environment with
`uv run --no-sync python --version`. The script guide lists the maintained tools
for local development and performance checks. [Script guide](../../scripts/README.md#core-scripts)
