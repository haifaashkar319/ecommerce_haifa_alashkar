import os
import sys
sys.path.insert(0, os.path.abspath('../..'))



# -- Project information -----------------------------------------------------
project = '435L Final Project'
author = 'Your Name'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google and NumPy style docstrings
    'sphinx.ext.viewcode',  # Adds links to source code
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']
