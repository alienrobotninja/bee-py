"""Nox sessions."""
# import shlex
# import shutil
# import sys
# from pathlib import Path

# # from textwrap import dedent
import nox

# from nox import Session, session

"""
    Helps for future developer to implement tests using Nox
    - https://medium.com/analytics-vidhya/nox-the-shining-python-test-automation-tool-3e189e343b57
    - https://sethmlarson.dev/nox-pyenv-all-python-versions#:~:text=Usually%20this%20is%20done%20for,other%20things%20like%20dependency%20versions).&text=This%20is%20awesome!,target%20a%20specific%20Python%20version.
"""  # noqa: 501


package = "bee_py"
python_versions = ["3.12", "3.11", "3.10", "3.9"]
nox.needs_version = ">= 2023.4.22"
nox.options.sessions = (
    # "pre-commit",
    # "safety",
    "mypy",
    "tests",
    # "typeguard",
    # "xdoctest",
    # "docs-build",
)


# @session(name="pre-commit", python=python_versions[0])
# def precommit(session: Session) -> None:
#     """Lint using pre-commit."""
#     args = session.posargs or [
#         "run",
#         "--all-files",
#         "--hook-stage=manual",
#         "--show-diff-on-failure",
#     ]
#     session.install(
#         "bandit",
#         "black",
#         "darglint",
#         "flake8",
#         "flake8-bugbear",
#         "flake8-docstrings",
#         "flake8-rst-docstrings",
#         "isort",
#         "pep8-naming",
#         "pre-commit",
#         "pre-commit-hooks",
#         "pyupgrade",
#     )
#     session.run("pre-commit", *args)
#     if args and args[0] == "install":
#         activate_virtualenv_in_precommit_hooks(session)


# @session(python=python_versions)
# def mypy(session: Session) -> None:
#     """Type-check using mypy."""
#     args = session.posargs or ["src", "tests", "docs/conf.py"]
#     session.install(".[lint]")
#     session.install("mypy", "pytest")
#     session.run("mypy", *args)
#     if not session.posargs:
#         session.run("mypy", f"--python-executable={sys.executable}", "noxfile.py")


# @session(python=python_versions)
# def tests(session: Session) -> None:
#     """Run the test suite."""
#     session.install(".[test]")
#     session.install("coverage[toml]", "pytest", "pygments")
#     try:
#         session.run("coverage", "run", "--parallel", "-m", "pytest", *session.posargs)
#     finally:
#         if session.interactive:
#             session.notify("coverage", posargs=[])


# @session(python=python_versions[0])
# def coverage(session: Session) -> None:
#     """Produce the coverage report."""
#     args = session.posargs or ["report"]

#     session.install("coverage[toml]")

#     if not session.posargs and any(Path().glob(".coverage.*")):
#         session.run("coverage", "combine")

#     session.run("coverage", *args)


# @session(python=python_versions[0])
# def typeguard(session: Session) -> None:
#     """Runtime type checking using Typeguard."""
#     session.install(".[dev]")
#     session.install("pytest", "typeguard", "pygments")
#     session.run("pytest", f"--typeguard-packages={package}", *session.posargs)


# @session(name="docs-build", python=python_versions[0])
# def docs_build(session: Session) -> None:
#     """Build the documentation."""
#     args = session.posargs or ["docs", "docs/_build"]
#     if not session.posargs and "FORCE_COLOR" in os.environ:
#         args.insert(0, "--color")

#     session.install(".")
#     session.install("sphinx", "sphinx-click", "furo", "myst-parser")

#     build_dir = Path("docs", "_build")
#     if build_dir.exists():
#         shutil.rmtree(build_dir)

#     session.run("sphinx-build", *args)


# @session(python=python_versions[0])
# def docs(session: Session) -> None:
#     """Build and serve the documentation with live reloading on file changes."""
#     args = session.posargs or ["--open-browser", "docs", "docs/_build"]
#     session.install(".")
#     session.install("sphinx", "sphinx-autobuild", "sphinx-click", "furo", "myst-parser")

#     build_dir = Path("docs", "_build")
#     if build_dir.exists():
#         shutil.rmtree(build_dir)

#     session.run("sphinx-autobuild", *args)
