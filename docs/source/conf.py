# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))


# -- Project information -----------------------------------------------------

project = 'WinMagnification'
# noinspection PyShadowingBuiltins
copyright = '2022, MaxBQb'
author = 'MaxBQb'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# noinspection SpellCheckingInspection
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx_design',  # https://sphinx-design.readthedocs.io/en/rtd-theme/badges_buttons.html
    'sphinx.ext.viewcode',
    'sphinx_tabs.tabs',
    'sphinx-prompt',
    'sphinx_toolbox',  # https://sphinx-toolbox.readthedocs.io/en/stable/extensions/
    'sphinx_toolbox.sidebar_links',
    'sphinx_toolbox.github',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
github_username = 'MaxBQb'
github_repository = 'WinMagnification'
add_module_names = False
autodoc_typehints = 'signature'
# noinspection SpellCheckingInspection
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
# noinspection SpellCheckingInspection
intersphinx_disabled_domains = ['std']
# noinspection SpellCheckingInspection
autosummary_generate = True
# noinspection SpellCheckingInspection
autodoc_member_order = 'bysource'


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []  # type: ignore


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

autodoc_type_aliases = {
    'types.ColorMatrix': 'types.ColorMatrix',
    'ColorMatrix': 'types.ColorMatrix',
    'types.TransformationMatrix': 'types.TransformationMatrix',
    'types.RectangleRaw': 'Tuple[int, int, int, int]',
    'T': 'T',
    'WrappedFieldType': 'WrappedFieldType',
}
autodoc_typehints_format = 'short'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []  # type: ignore
