set default-list := true

# Export the current project's requirements into a requirements.txt without the
# current directory
requirements:
    uv export --format requirements.txt | grep -vE "-e \." > requirements.txt 
