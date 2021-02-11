from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from post.models import TPost


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
        handler.addQuickElement(u"content:encoded", item["content_encoded"])


class AllEntriesFeed(Feed):
    title = "Tanzawa"
    feed_type = ExtendedRSSFeed
    item_guid_is_permalink = False

    def link(self):
        return reverse("feeds:feed")

    def items(self):
        return (
            TPost.objects.published()
            .prefetch_related("ref_t_entry")
            .all()
            .order_by("-dt_published")[:10]
        )

    def item_title(self, item: TPost):
        t_entry = item.ref_t_entry.all()[0]
        return t_entry.p_name or t_entry.p_summary[:128]

    def item_description(self, item: TPost):
        return item.ref_t_entry.all()[0].p_summary

    def item_extra_kwargs(self, item: TPost):
        content_encoded = item.ref_t_entry.all()[0].e_content
        no_div_wrapper_content = f"<p>{content_encoded[5:-6]}</p>"
        return {"content_encoded": no_div_wrapper_content}

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
