#!/bin/zsh

set -e

local dir=$(dirname -- "$0")
local root=$(dirname -- "$dir")

local gimp_path='/Applications/GIMP.app/Contents'
local python_exec="${gimp_path}/MacOS/python3"

$python_exec -m venv .venv --upgrade --upgrade-deps

local python_v_exec="${root}/.venv/bin/python3"

$python_v_exec -m pip install -r "${dir}/requirements.txt"
