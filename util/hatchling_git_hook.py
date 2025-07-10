from hatchling.builders.hooks.plugin.interface import BuildHookInterface

from pathlib import Path
from subprocess import check_output

def get_commit_hash(root: str):
    return check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode('utf-8').strip()

class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "GIT_HASH_EXTRACTOR"

    PACKAGE_NAME = "depot_server"
    BUILD_FOLDER = Path("build/") 
    FILENAME = BUILD_FOLDER / "version.py"

    def initialize(self, version: str, build_data: dict[str, any]) -> None:
        self.BUILD_FOLDER.mkdir(exist_ok=True, parents=True)
        
        hash = get_commit_hash(self.root)
        
        print(f"Building commit hash: {hash}") 
        template = [
            "# Do not edit by hand, gets overwritten by `uv build`",
            "from importlib.metadata import version",
            "version = version(\"depot_server\")",
            f"commit_hash = \"{hash[:8]}\""
        ]

        with open(self.FILENAME, "w") as f:
            f.writelines(map(lambda s: f"{s}\n", template))
