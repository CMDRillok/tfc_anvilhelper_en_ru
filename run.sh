#!/usr/bin/env bash
# Запуск помощника наковальни TFC.
# Если Tkinter установлен локально (без root), подхватываем библиотеки из ~/.local/tk-root.
set -euo pipefail

cd "$(dirname "$0")"

TK_ROOT="${TK_ROOT:-$HOME/.local/tk-root}"
if [ -d "$TK_ROOT/usr/lib" ]; then
    export LD_LIBRARY_PATH="$TK_ROOT/usr/lib:${LD_LIBRARY_PATH:-}"
    export TCL_LIBRARY="$TK_ROOT/usr/lib/tcl8.6"
    export TK_LIBRARY="$TK_ROOT/usr/lib/tk8.6"
fi

exec python3 tfctk.py
