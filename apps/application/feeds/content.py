from data.plugins.pool import plugin_pool
from data.post import models as post_models
from domain.feeds import queries


def get_encoded_content(*, post: post_models.TPost) -> str:
    """
    Get the html encoded for a given post wrapped with plugin content before/after the post.
    """
    before_content = ""
    after_content = ""
    content = queries.get_encoded_content(post)
    for feed_plugin in plugin_pool.feed_plugins():
        before_content += feed_plugin.feed_before_content(post=post)
        after_content += feed_plugin.feed_after_content(post=post)
    return f"{before_content}{content}{after_content}"
