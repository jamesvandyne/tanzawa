from plugins.core import plugin_pool
from ._plugin import get_plugin


plugin_pool.register_plugin(get_plugin())
