# Mead: your simplest Flask blog engine

No Javascript, No tracking, No themes, only your words and SQLite !

## Create virtual environment

```
uv venv
```

## Activate the virtual environment

### On Linux/macOS:

```
source .venv/bin/activate
```

### On Windows:

```
.venv\Scripts\activate
```

## Install dependencies

```
uv pip install -r requirements.txt
```

## Update dependencies

```
uv pip compile requirements.txt --upgrade
```

## For development, also install development dependencies:

```
uv pip install pytest pytest-cov ruff
```

## Running the Blog

```
export FLASK_APP=app
export FLASK_DEBUG=1
uv run flask init-db
uv run flask run
```

