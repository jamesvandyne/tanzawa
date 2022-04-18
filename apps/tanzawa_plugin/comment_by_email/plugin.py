from typing import Optional

from data.plugins import plugin, pool
from data.post import models as post_models
from django.template import loader

__identifier__ = "blog.tanzawa.plugins.comment-by-email"


class CommentByEmail(plugin.Plugin):
    """
    Add links inviting readers to comment to your post by email.
    """

    name = "Reply by email"
    identifier = __identifier__

    @property
    def description(self):
        return """Invite users to reply to your posts by email."""

    @property
    def has_feed_hooks(self):
        return True

    @property
    def urls(self) -> Optional[str]:
        return None

    @property
    def admin_urls(self) -> Optional[str]:
        return None

    def feed_after_content(self, post: Optional[post_models.TPost] = None) -> str:
        template = loader.get_template("comment_by_email/feed.html")
        return template.render(context={"post": post})


def get_plugin() -> plugin.Plugin:
    return CommentByEmail()


pool.plugin_pool.register_plugin(get_plugin())
