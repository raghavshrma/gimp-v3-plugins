# # The generator3 module can be downloaded from this repository:
# # https://github.com/JetBrains/intellij-community/tree/master/python/helpers/generator3


import os
import subprocess
import sys

from gimp_modules import MODULES_LIST
import tools.generate as generate

_root = os.path.dirname(os.path.dirname(__file__))
_repo_path = os.path.join(
    _root, ".venv/lib/python3.10/site-packages/gi-stubs/repository"
)
# _repo_path = os.path.join(_root, "gi-stubs/repository")


def setup_repo():
    if not os.path.exists(_repo_path):
        os.makedirs(_repo_path, exist_ok=True)

    if not os.path.exists(os.path.join(_repo_path, "__init__.py")):
        with open(os.path.join(_repo_path, "__init__.py"), "w") as fd:
            fd.write("")
            fd.close()

    base = os.path.dirname(_repo_path)

    if not os.path.exists(os.path.join(base, "__init__.py")):
        with open(os.path.join(base, "__init__.py"), "w") as fd:
            fd.write("")
            fd.close()

def generate_stub(namespace: str, version: str):
    out_path = os.path.join(_repo_path, namespace + ".pyi")
    try:
        # print(f"Generating: {namespace} {version}", file=sys.stderr)
        stubs = generate.start(namespace, version, {})
        with open(out_path, "w") as fd:
            fd.write(stubs)
        print(f"Generated: {namespace} {version}")
        return (True, out_path)
    except Exception as e:
        print(f"Error Generating: {namespace} {version}", file=sys.stderr)
        print(e.with_traceback(), file=sys.stderr)
        print("---------------------------------", file=sys.stderr)
        return (False, out_path)


if __name__ == "__main__":
    setup_repo()
    failed_generations = []

    for namespace, version in MODULES_LIST:
        success, out_path = generate_stub(namespace, version)

        if not success:
            failed_generations.append(out_path)

    if failed_generations:
        print("Generating the following stubs failed:", file=sys.stderr)
        print(
            "\n".join(f"  - {path}" for path in failed_generations),
            file=sys.stderr,
        )
        sys.exit(1)
else:
    print("Not running as main.")
