import os
import platform
import sys
from pathlib import Path

Path("logs").mkdir(exist_ok=True)
# Tasks to run during `doit` (with no args)
DOIT_CONFIG = {
    'default_tasks': ['setup'],
    'dep_file': 'logs/doit-db.json',
}


# Use mamba by default
USE_MAMBA = True

# Automatically agree to conda actions
os.environ["CONDA_ALWAYS_YES"] = "true"

# Path to environment
ENV_PATH = ".envs/"
Path(ENV_PATH).mkdir(exist_ok=True)

PLATFORM = platform.system()
PYTHON = sys.executable

class CONDA:
    specs = []
    @classmethod
    def prepare(cls, spec):
        yield {
            "name": f"prepare ({spec})",
            "actions": [f"mamba env update -p .envs/{spec} -f deploy/specs/{spec}.yml"],
            "file_dep": [f"deploy/specs/{spec}.yml"],
        }

    @classmethod
    def run_in(cls, spec, tasks):
        yield cls.prepare(spec)
        for task in tasks:
            yield dict(
                actions=[f"conda run --no-capture-output --live-stream -p .envs/{spec} {action}" for action in task.pop('actions')],
                **task
            )


def task_setup():
    return CONDA.run_in(
        spec="dev",
        tasks=[
            dict(
                name="install src",
                actions=['python -m pip install -e . --no-deps'],
                verbosity=2,
            ),
            dict(
                name="pip check",
                actions=['python -m pip check'],
                verbosity=2,
            ),
        ]
    )

def task_test():
    return CONDA.run_in(
        spec="dev",
        tasks=[
            dict(
                name="run pytests",
                actions=['pytest'],
                verbosity=2,
            ),
        ]
    )

def task_launch():
    return CONDA.run_in(
        spec="dev",
        tasks=[
            dict(
                name="launch",
                actions=['jupyter lab']
            ),
        ]
    )

def task_lint():
    return CONDA.run_in(
        spec="qa",
        tasks=[
            dict(
                name="launch",
                actions=[
                    "isort ipypdf/ tests/", 
                    "black ipypdf/ tests/ -l 79"
                ]
            ),
        ]
    )

def task_lab():
    return CONDA.run_in(
        spec="dev",
        tasks=[
            dict(
                name="jupyterlab",
                actions=["jupyter lab"]
            ),
        ]
    )