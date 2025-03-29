#!/bin/zsh

set -e

dir=$(dirname -- "$0")
root=$(dirname -- "$dir")

gi_stub_dir="$root/.venv/lib/python3.10/site-packages/gi-stubs"
gi_repo_dir="${gi_stub_dir}/repository"

[[ -d "$gi_repo_dir" ]] || mkdir -p "$gi_repo_dir"

touch "${gi_stub_dir}/__init__.py"
touch "${gi_repo_dir}/__init__.py"
touch "${gi_repo_dir}/__init__.pyi"

echo "from typing import Optional

__version__: str

def check_version(version: str) -> None: ...
def require_version(namespace: str, version: str) -> None: ...
def require_versions(versions: dict[str, str]) -> None: ...
def get_required_version(namespace: str) -> Optional[str]: ...
def require_foreign(namespace: str, symbol: Optional[str] = None) -> None: ...
" >"${gi_stub_dir}/__init__.pyi"


gimp_path='/Applications/GIMP.app/Contents'
r_path="${gimp_path}/Resources"
python_exec="${gimp_path}/MacOS/python3"

BABL_PATH="$r_path/lib/babl-0.1" \
    GI_TYPELIB_PATH="$r_path/lib/girepository-1.0" \
    $python_exec "${dir}/generate_gimp_stubs.py"

# BABL_PATH="$r_path/lib/babl-0.1" \
#     GI_TYPELIB_PATH="$r_path/lib/girepository-1.0" \
#     $python_exec stubs/tools/generate.py Gimp 3.0 -u Gimp.pyi
