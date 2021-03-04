from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from post.models import TPost
from streams.models import MStream
from indieweb.constants import MPostKinds


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """

    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement("content:encoded", item["content_encoded"])


class AllEntriesFeed(Feed):
    title = "Tanzawa"
    feed_type = ExtendedRSSFeed
    item_guid_is_permalink = False

    def link(self):
        return reverse("feeds:feed")

    def items(self):
        return (
            TPost.objects.published()
            .select_related("m_post_kind")
            .prefetch_related("ref_t_entry", "ref_t_entry__t_reply")
            .all()
            .order_by("-dt_published")[:10]
        )

    def item_title(self, item: TPost):
        t_entry = item.ref_t_entry.all()[0]
        title = t_entry.p_name or t_entry.p_summary[:128]
        if item.m_post_kind.key == MPostKinds.reply:
            title = f"Response to {t_entry.t_reply.title}"
        elif item.m_post_kind.key == MPostKinds.bookmark:
            t_bookmark = t_entry.t_bookmark
            title = f"Bookmark of {t_bookmark.title or t_bookmark.u_bookmark_of}"
        return title

    def item_description(self, item: TPost):
        return item.ref_t_entry.all()[0].p_summary

    def item_extra_kwargs(self, item: TPost):
        t_entry = item.ref_t_entry.all()[0]
        e_content = t_entry.e_content
        if item.m_post_kind.key == MPostKinds.reply:
            e_content = f"<blockquote>{t_entry.t_reply.quote}</blockquote>{e_content}"
        elif item.m_post_kind.key == MPostKinds.bookmark:
            t_bookmark = t_entry.t_bookmark
            e_content = f'Bookmark: <a href="{t_bookmark.u_bookmark_of}">{t_bookmark.title or t_bookmark.u_bookmark_of}</a><blockquote>{t_bookmark.quote}</blockquote>{e_content}'
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
        return get_object_or_404(
            MStream.objects.visible(request.user), slug=stream_slug
        )

    def items(self, obj):
        return (
            TPost.objects.published()
            .filter(streams=obj)
            .prefetch_related("ref_t_entry")
            .all()
            .order_by("-dt_published")[:10]
        )
