#!/usr/bin/env bash
set -euo pipefail

. $HOME/.profile

absolute_path=$(pwd)
pattern=":$absolute_path:"
if [ -z "${AMOR_DIR+x}" ]; then
    printf "\nSetting AMOR_DIR to the following:"
    printf "$absolute_path\n"
    echo "export AMOR_DIR=$absolute_path" >> $HOME/.profile
else
    printf '\n\e[93m%-6s\e[m\n' "AMOR_DIR is already set to: $AMOR_DIR"
fi

case :$PATH: in
    *$pattern*)
        printf '\n\e[93m%-6s\e[m\n' "$absolute_path already in PATH!"
        ;;
    *)
        printf '\n\e[93m%-6s\e[m\n' "Adding the following path to your system PATH:"
        printf "$absolute_path\n"
        echo "export PATH=\$AMOR_DIR:\$PATH" >> $HOME/.profile

        printf "\$HOME/.profile updated"
        ;;
esac

. $HOME/.profile
