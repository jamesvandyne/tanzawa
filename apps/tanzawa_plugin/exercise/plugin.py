from django import http, template
from django.template import loader

from data.plugins import plugin, pool
from data.plugins.plugin import RequestContentType
from data.post import models as post_models

from .data import exercise_models
from .interfaces.public import serializers

__identifier__ = "blog.tanzawa.plugins.exercise"


class ExercisePlugin(plugin.Plugin):
    """Track your runs and rides."""

    name = "Exercise"
    identifier = __identifier__

    @property
    def description(self) -> str:
        return "Track your runs and rides on your site."

    @property
    def has_public_top_nav(self):
        return True

    @property
    def has_admin_left_nav(self) -> bool:
        return True

    @property
    def has_feed_hooks(self):
        return True

    @property
    def has_content_hooks(self):
        return True

    def render_navigation(
        self,
        *,
        context: template.Context,
        render_location: str,
    ) -> str:
        """
        Render the admin navigation menu item.
        """
        t = context.template.engine.get_template("exercise/navigation.html")
        return t.render(context=context)

    def feed_after_content(self, request: http.HttpRequest, post: None | post_models.TPost = None) -> str:
        from .interfaces.public.feeds import serializers

        if post is None:
            return ""

        template = loader.get_template("exercise/public/feeds/activity_detail.html")
        try:
            activity = exercise_models.Activity.objects.get(entry_id=post.ref_t_entry.id)
        except Exception:
            return ""
        else:
            activity_detail = serializers.Activity(activity).data
            return template.render(context={"activity": activity_detail}, request=request)

    def render_after_content(
        self,
        request: http.HttpRequest,
        request_content_type: RequestContentType = RequestContentType.HTML,
        post: post_models.TPost | None = None,
    ) -> str:
        if post is None:
            return ""

        template = loader.get_template("exercise/public/fragments/activity_detail.html")
        try:
            activity = exercise_models.Activity.objects.get(entry_id=post.ref_t_entry.id)
        except Exception:
            return ""
        else:
            activity_detail = serializers.Activity(activity).data
            return template.render(context={"activity": activity_detail}, request=request)


def get_plugin() -> plugin.Plugin:
    return ExercisePlugin()


pool.plugin_pool.register_plugin(get_plugin())
