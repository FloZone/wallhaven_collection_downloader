import distutils.cmd
import distutils.log
import os
import re
import subprocess
import sys
from typing import List, Tuple

from setuptools import setup

FILES_BLACKLIST = re.compile(r".*/data/translations.*")


def list_git_modified_files():
    files = []
    output = subprocess.check_output(["git", "status", "--porcelain"])
    decoded_output = output.decode("utf-8")
    for line in decoded_output.split("\n"):
        if line.strip() == "":
            continue
        status, filename = line.strip().split(" ")
        if status not in ["M", "U", "??"]:
            continue
        if check_is_ignored(filename):
            continue
        files.append(filename)
    return files


def check_is_ignored(path):
    return bool(FILES_BLACKLIST.match(path))


def check_is_not_python(path):
    base, path_ext = os.path.splitext(path)
    return path_ext != "" and path_ext != ".py"


class LintCommand(distutils.cmd.Command):
    """Lint with flake8."""

    description = "run flake8 on source files"
    user_options = [("path=", "p", "path"), ("auto", "a", "auto")]

    def initialize_options(self):
        self.path = None
        self.auto = False

    def finalize_options(self):
        if self.path is None:
            self.path = "."

    def apply_command(self, path):
        self.announce(f"linting files on path {path} ...", level=distutils.log.INFO)

        if check_is_ignored(path) or check_is_not_python(path):
            self.announce(f"ignoring path {path} ...", level=distutils.log.INFO)
            return

        try:
            self.announce("> flake8 pass ...", level=distutils.log.INFO)
            subprocess.check_call(["python", "-m", "flake8", path])
        except subprocess.CalledProcessError:
            sys.exit(1)

    def run(self):
        if self.auto:
            files = list_git_modified_files()
            for filename in files:
                self.apply_command(filename)
        else:
            self.apply_command(self.path)


class FormatCommand(distutils.cmd.Command):
    """Format with black."""

    description = "run lf script, isort and black on source files"
    user_options = [("path=", "p", "path"), ("auto", "a", "auto")]

    def initialize_options(self):
        self.path = None
        self.auto = False

    def finalize_options(self):
        if self.path is None:
            self.path = "."

    def apply_command(self, path):
        self.announce(f"formatting files on path {path} ...", level=distutils.log.INFO)

        try:
            self.announce("> lf pass ...", level=distutils.log.INFO)
            subprocess.check_call(["python", "./autolf.py", "-q", path])
        except subprocess.CalledProcessError:
            sys.exit(1)

        if check_is_ignored(path) or check_is_not_python(path):
            self.announce(f"ignoring path {path} ...", level=distutils.log.INFO)
            return

        try:
            self.announce("> isort ...", level=distutils.log.INFO)
            subprocess.check_call(["isort", "-rc", "--atomic", path])
        except subprocess.CalledProcessError:
            sys.exit(1)

        try:
            self.announce("> black ...", level=distutils.log.INFO)
            subprocess.check_call(
                ["python", "-m", "black", "--target-version", "py36", "-l", "120", path,]
            )
        except subprocess.CalledProcessError:
            sys.exit(1)

    def run(self):
        if self.auto:
            files = list_git_modified_files()
            for filename in files:
                self.apply_command(filename)
        else:
            self.apply_command(self.path)


class FormatCheckCommand(distutils.cmd.Command):
    """Format check with black."""

    description = "run black check on source files"
    user_options = [("path=", "p", "path"), ("auto", "a", "auto")]

    def initialize_options(self):
        self.path = None
        self.auto = False

    def finalize_options(self):
        if self.path is None:
            self.path = "."

    def apply_command(self, path):
        self.announce(f"checking if files are formatted on path {path} ...", level=distutils.log.INFO)

        try:
            self.announce("> lf pass ...", level=distutils.log.INFO)
            subprocess.check_call(["python", "./autolf.py", "-cq", path])
        except subprocess.CalledProcessError:
            sys.exit(1)

        if check_is_ignored(path) or check_is_not_python(path):
            self.announce(f"ignoring path {path} ...", level=distutils.log.INFO)
            return

        try:
            self.announce("> black pass ...", level=distutils.log.INFO)
            subprocess.check_call(
                ["python", "-m", "black", "--target-version", "py36", "-l", "120", "--check", path,]
            )
        except subprocess.CalledProcessError:
            sys.exit(1)

    def run(self):
        if self.auto:
            files = list_git_modified_files()
            for filename in files:
                self.apply_command(filename)
        else:
            self.apply_command(self.path)


class TypeCheckCommand(distutils.cmd.Command):
    """Typecheck with mypy."""

    description = "run mypy on source files"
    user_options = [("path=", "p", "path"), ("auto", "a", "auto")]

    def initialize_options(self):
        self.path = None
        self.auto = False

    def finalize_options(self):
        if self.path is None:
            self.path = "."

    def apply_command(self, path):
        self.announce(f"type checking in path {path} ...", level=distutils.log.INFO)

        if check_is_ignored(path) or check_is_not_python(path):
            self.announce(f"ignoring path {path} ...", level=distutils.log.INFO)
            return

        try:
            subprocess.check_call(["python", "-m", "mypy", path])
        except subprocess.CalledProcessError:
            sys.exit(1)

    def run(self):
        if self.auto:
            files = list_git_modified_files()
            for filename in files:
                self.apply_command(filename)
        else:
            self.apply_command(self.path)


class CICommand(distutils.cmd.Command):
    """Run CI."""

    description = "run ci"
    user_options: List[Tuple] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce(f"running CI ...", level=distutils.log.INFO)
        executable = sys.executable

        try:
            subprocess.check_call([executable, "setup.py", "fmtcheck", "-p", "."])
        except subprocess.CalledProcessError:
            sys.exit(1)

        try:
            subprocess.check_call([executable, "setup.py", "lint", "-p", "."])
        except subprocess.CalledProcessError:
            sys.exit(1)


setup(
    cmdclass={
        "lint": LintCommand,
        "fmt": FormatCommand,
        "fmtcheck": FormatCheckCommand,
        "typecheck": TypeCheckCommand,
        "ci": CICommand,
    },
)
