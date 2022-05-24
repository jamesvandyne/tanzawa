from application.feeds import content as feed_content
from data.post.models import TPost
from data.streams.models import MStream
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed, rfc2822_date
from domain.posts import queries as post_queries


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
        return self.request.settings.title or "Tanzawa"

    def link(self):
        return reverse("public:home")

    def items(self):
        return post_queries.get_public_posts_for_user(user=self.request.user)[:10]

    def item_title(self, item: TPost):
        if item.ref_t_entry.is_note or item.ref_t_entry.is_checkin:
            return None
        return item.post_title

    def item_description(self, item: TPost):
        return item.ref_t_entry.p_summary

    def item_extra_kwargs(self, item: TPost):
        content_encoded = feed_content.get_encoded_content(post=item)
        return {"content_encoded": content_encoded}

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
        return post_queries.get_public_posts_for_user(self.request.user, stream=obj)[:10]
