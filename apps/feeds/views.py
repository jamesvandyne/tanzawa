from core.constants import Visibility
from data.entry import models as entry_models
from data.settings.models import MSiteSettings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed, rfc2822_date
from indieweb.constants import MPostKinds, MPostStatuses
from post.models import TPost
from streams.models import MStream


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs["xmlns:content"] = "http://purl.org/rss/1.0/modules/content/"
        return attrs

    def add_item_elements(self, handler, item):  # noqa: C901
        """
        Overrides the base class because there's no hook around the title tag.
        Excluding the title tag if no title is set to allow checkins and notes to display inline
        on micro.blog
        """
        if item["title"]:
            handler.addQuickElement("title", item["title"])
        # Django super start
        handler.addQuickElement("link", item["link"])
        if item["description"] is not None:
            handler.addQuickElement("description", item["description"])

        # Author information.
        if item["author_name"] and item["author_email"]:
            handler.addQuickElement("author", "%s (%s)" % (item["author_email"], item["author_name"]))
        elif item["author_email"]:
            handler.addQuickElement("author", item["author_email"])
        elif item["author_name"]:
            handler.addQuickElement("dc:creator", item["author_name"], {"xmlns:dc": "http://purl.org/dc/elements/1.1/"})

        if item["pubdate"] is not None:
            handler.addQuickElement("pubDate", rfc2822_date(item["pubdate"]))
        if item["comments"] is not None:
            handler.addQuickElement("comments", item["comments"])
        if item["unique_id"] is not None:
            guid_attrs = {}
            if isinstance(item.get("unique_id_is_permalink"), bool):
                guid_attrs["isPermaLink"] = str(item["unique_id_is_permalink"]).lower()
            handler.addQuickElement("guid", item["unique_id"], guid_attrs)
        if item["ttl"] is not None:
            handler.addQuickElement("ttl", item["ttl"])

        # Enclosure.
        if item["enclosures"]:
            enclosures = list(item["enclosures"])
            if len(enclosures) > 1:
                raise ValueError(
                    "RSS feed items may only have one enclosure, see "
                    "http://www.rssboard.org/rss-profile#element-channel-item-enclosure"
                )
            enclosure = enclosures[0]
            handler.addQuickElement(
                "enclosure",
                "",
                {
                    "url": enclosure.url,
                    "length": enclosure.length,
                    "type": enclosure.mime_type,
                },
            )

        # Categories.
        for cat in item["categories"]:
            handler.addQuickElement("category", cat)
        # Django Superclass End
        # Add our html content to the feed
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
        if item.m_post_kind.key in (MPostKinds.checkin, MPostKinds.note):
            return None
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
        elif item.m_post_kind.key == MPostKinds.checkin:
            e_content = f"{item.post_title}<br/>{e_content}"
        try:
            e_content = f"{e_content}<br/>Location: {t_entry.t_location.summary}"
        except entry_models.TLocation.DoesNotExist:
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
