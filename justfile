set default-list := true

# Export the current project's requirements into a requirements.txt without the
# current directory
requirements:
    uv export --format requirements.txt | grep -vE "-e \." > requirements.txt 

# Shortcut for running the setup script. Yes, I'm lazy
setup:
    bash setup
    
# Quickly uninstall amor for testing
uninstall:
    python3 -m pip uninstall amor -y

# Very lazy format command
fmt:
    uv format

healthcheck:
    uv format --check
    uv audit

sync args="":
    uv sync --exclude-newer="1 week" {{ args }}
