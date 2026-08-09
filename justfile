set default-list := true

# Export the current project's requirements into a requirements.txt without the
# current directory
requirements:
    uv export --format requirements.txt --no-hashes --fork-strategy requires-python --no-dev --no-build --no-emit-project > requirements.txt 

# Shortcut for running the setup script. Yes, I'm lazy
setup:
    bash setup.sh
    
# Quickly uninstall amor for testing
uninstall version="3":
    python{{ version }} -m pip uninstall amor -y

# Very lazy format command
fmt:
    uv format

healthcheck:
    uv format --check
    uv audit

sync args="":
    uv sync --exclude-newer="1 week" {{ args }}

activate:
    #!/usr/bin/env bash
    . ./.venv/bin/activate

upgrade-pip version="3":
    python{{ version }} -m pip install --upgrade pip setuptools

dev: sync (uninstall "3.14") setup
