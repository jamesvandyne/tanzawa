from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from post.models import TPost
from streams.models import MStream
from core.constants import Visibility
from entry.models import TLocation
from indieweb.constants import MPostKinds, MPostStatuses
from settings.models import MSiteSettings


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement("content:encoded", item["content_encoded"])


class AllEntriesFeed(Feed):
    feed_type = ExtendedRSSFeed
    item_guid_is_permalink = False

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def title(self):
        title = MSiteSettings.objects.values_list("title", flat=True).first()
        return title or "Tanzawa"

    def link(self):
        return reverse("feeds:feed")

    def items(self):
        return (
            TPost.objects.visible_for_user(self.request.user.id)
            .filter(m_post_status__key=MPostStatuses.published)
            .exclude(visibility=Visibility.UNLISTED)
            .select_related("m_post_kind")
            .prefetch_related(
                "ref_t_entry",
                "ref_t_entry__t_reply",
                "ref_t_entry__t_location",
                "ref_t_entry__t_checkin",
            )
            .all()
            .order_by("-dt_published")[:10]
        )

    def item_title(self, item: TPost):
        return item.post_title

    def item_description(self, item: TPost):
        return item.ref_t_entry.p_summary

    def item_extra_kwargs(self, item: TPost):
        t_entry = item.ref_t_entry
        e_content = t_entry.e_content
        if item.m_post_kind.key == MPostKinds.reply:
            e_content = f"<blockquote>{t_entry.t_reply.quote}</blockquote>{e_content}"
        elif item.m_post_kind.key == MPostKinds.bookmark:
            t_bookmark = t_entry.t_bookmark
            e_content = (
                f"Bookmark: "
                f'<a href="{t_bookmark.u_bookmark_of}"'
                f">{t_bookmark.title or t_bookmark.u_bookmark_of}</a>"
                f"<blockquote>{t_bookmark.quote}</blockquote>{e_content}"
            )
        try:
            e_content = f"{e_content}<br/>Location: {t_entry.t_location.summary}"
        except TLocation.DoesNotExist:
            pass
        return {"content_encoded": e_content}

    def item_guid(self, obj: TPost) -> str:
        return obj.uuid

    def item_author_name(self, item: TPost):
        return item.p_author.get_full_name()

    def item_author_link(self, item: TPost):
        return reverse("public:author", args=[item.p_author.username])

    def item_pubdate(self, item: TPost):
        return item.dt_published

    def item_updateddate(self, item: TPost):
        return item.dt_updated


class StreamFeed(AllEntriesFeed):
    def get_object(self, request, stream_slug: str):
        return get_object_or_404(MStream.objects.visible(request.user), slug=stream_slug)

    def items(self, obj):
        return (
            TPost.objects.visible_for_user(self.request.user.id)
            .filter(streams=obj, m_post_status__key=MPostStatuses.published)
            .exclude(visibility=Visibility.UNLISTED)
            .select_related("ref_t_entry")
            .all()
            .order_by("-dt_published")[:10]
        )
