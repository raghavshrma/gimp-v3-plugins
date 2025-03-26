#!/bin/zsh

set -e

local dir=$(dirname -- "$0")

local gimp_path='/Applications/GIMP.app/Contents'
local r_path="${gimp_path}/Resources"
local python_exec="${gimp_path}/MacOS/python3"

local out_root="$(dirname -- "$dir")/.venv/lib/gimp"
local out_cache="${out_root}/cache"
local out_stubs="${out_root}/stubs"

rm -rf "$out_cache"
rm -rf "$out_stubs"

mkdir -p "$out_cache"
mkdir -p "$out_stubs"

BABL_PATH="$r_path/lib/babl-0.1" \
    GI_TYPELIB_PATH="$r_path/lib/girepository-1.0" \
    $python_exec stubs
