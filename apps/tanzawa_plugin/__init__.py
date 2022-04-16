import pathlib
from importlib import import_module

# Automatically import all python modules in this directory to allow us to add plugins without
# needing to modify this __init__ file to install new plugins.
for module in pathlib.Path(__file__).parent.glob("*/__init__.py"):
    import_module(f".{module.parent.name}", package="tanzawa_plugin")
