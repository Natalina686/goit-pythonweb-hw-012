import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

from unittest.mock import MagicMock

MOCK_MODULES = [
    'crud', 'models', 'schemas', 'routes.auth', 'routes.contacts', 'routes.users',
    'settings', 'deps', 'dependencies.auth', 'dependencies.roles'
]

for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

autodoc_mock_imports = MOCK_MODULES

project = 'MyContactsApp'
copyright = '2025, natalina686'
author = 'natalina686'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']
