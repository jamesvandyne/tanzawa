from plugins import core

from .plugin import get_plugin

__version__ = 0.1


core.plugin_pool.register_plugin(get_plugin())
