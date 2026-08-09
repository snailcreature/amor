#!/usr/bin/env bash
set -euo pipefail

if [ ! -d "$HOME/.local/share" ]; then
    mkdir -p "$HOME/.local/share"
fi

if [ -d "$HOME/.local/share/amor" ]; then
    rm -rf $HOME/.local/share/amor
fi

pushd "$HOME/.local"

git clone https://github.com/snailcreature/amor.git amor --depth=1

cd amor

bash ./setup.sh

popd
