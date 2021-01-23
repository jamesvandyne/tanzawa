from django.db.models import F
from django.contrib.syndication.views import Feed
from post.models import TPost
from django.utils.feedgenerator import Rss201rev2Feed


class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """

    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])


class AllEntriesFeed(Feed):
    title = "Tanzawa"
    link = "/"
    feed_type = ExtendedRSSFeed

    def items(self):
        return TPost.objects.prefetch_related('ref_t_entry').all()

    def item_link(self, item: TPost):
        return item.get_absolute_url()

    def item_title(self, item: TPost):
        try:
            return item.ref_t_entry.all()[0].p_name
        except IndexError:
            return ""

    def item_description(self, item: TPost):
        try:
            return item.ref_t_entry.all()[0].p_summary
        except IndexError:
            return ""

    def item_extra_kwargs(self, item: TPost):
        try:
            content_encoded = item.ref_t_entry.all()[0].e_content
        except IndexError:
            content_encoded = ""
        return {'content_encoded': content_encoded}


