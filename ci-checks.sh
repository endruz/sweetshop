
set -e

cd "$(dirname "$0")"

echo "> Running CI checks..."
echo "> Installing dependencies..."
uv sync --group dev

echo "> Linting code with ruff..."
uv run ruff check --no-cache

echo "> Checking code formatting with ruff..."
uv run ruff format --check --no-cache

echo "> Running type checks with ty..."
uv run ty check

echo "> Running tests with pytest..."
uv run pytest --cache-clear --cov=src/sweetshop
