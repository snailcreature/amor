#!/usr/bin/env bash
set -euo pipefail

absolute_path=$(pwd)
pattern=":$absolute_path:"
case :$PATH: in
    *$pattern*)
        printf '\n\e[93m%-6s\e[m\n' "$absolute_path already in PATH!"
        ;;
    *)
        printf '\n\e[93m%-6s\e[m\n' "Adding the following path to your system PATH:"
        printf "$absolute_path\n"
        echo "export AMOR_DIR=$absolute_path" >> $HOME/.profile
        echo "export PATH=\$AMOR_DIR:\$PATH" >> $HOME/.profile

        printf "\$HOME/.profile updated"
        ;;
esac
