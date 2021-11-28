from plugins import pool

from .plugin import get_plugin

__version__ = 0.1


pool.plugin_pool.register_plugin(get_plugin())
