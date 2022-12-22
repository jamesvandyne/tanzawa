from typing import TYPE_CHECKING, Type

from django.template import loader

from data.plugins import plugin, pool

if TYPE_CHECKING:
    from data.post import models as post_models

__identifier__ = "blog.tanzawa.plugins.comment-by-email"


class CommentByEmail(plugin.Plugin):
    """
    Add links inviting readers to comment to your post by email.
    """

    name = "Reply by email"
    identifier = __identifier__

    @property
    def description(self):
        return """Invite users to comment to your posts privately by email."""

    @property
    def has_feed_hooks(self):
        return True

    @property
    def urls(self) -> str | None:
        return None

    @property
    def admin_urls(self) -> str | None:
        return None

    def feed_after_content(self, post: None | Type["post_models.TPost"] = None) -> str:
        template = loader.get_template("comment_by_email/feed.html")
        return template.render(context={"post": post})


def get_plugin() -> plugin.Plugin:
    return CommentByEmail()


pool.plugin_pool.register_plugin(get_plugin())
