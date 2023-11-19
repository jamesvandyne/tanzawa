from django import http

from data.plugins.pool import plugin_pool
from data.post import models as post_models
from domain.feeds import queries


def get_encoded_content(*, post: post_models.TPost, request: http.HttpRequest) -> str:
    """
    Get the html encoded for a given post wrapped with plugin content before/after the post.
    """
    before_content: list[str] = []
    after_content: list[str] = []
    br_tag = "<br/>"
    content = queries.get_encoded_content(post, request)
    for feed_plugin in plugin_pool.feed_plugins():
        if plugin_before_content := feed_plugin.feed_before_content(request, post=post):
            before_content.append(plugin_before_content)
        if plugin_after_content := feed_plugin.feed_after_content(request, post=post):
            after_content.append(plugin_after_content)

    if before_content:
        content = f"{br_tag.join(before_content)}{br_tag}{content}"
    if after_content:
        content = f"{content}{br_tag}{br_tag.join(after_content)}"

    return content
