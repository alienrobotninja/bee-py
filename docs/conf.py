"""Sphinx configuration."""
project = "Bee Py"
author = "Saikat Karmakar"
# copyright = "2023, Saikat Karmakar"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
