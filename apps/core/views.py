from typing import Optional

from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound
from django.urls import reverse


from wordpress.models import TWordpressPost, TCategory


def handle404(request, exception):
    # Redirect from our Wordpress post url to new permanent uuid url
    wp_post: Optional[TWordpressPost] = TWordpressPost.objects.filter(
        path__endswith=request.path, t_post__isnull=False
    ).first()
    if wp_post:
        return HttpResponsePermanentRedirect(wp_post.t_post.get_absolute_url())

    # Redirect to our mapped stream
    if request.path.startswith("/category/"):
        parts = request.path.split("/")
        t_category = TCategory.objects.filter(
            m_stream__isnull=False, nice_name=parts[2]
        ).first()
        if t_category:
            if request.path.endswith("feed"):
                # Redirect stream feeds
                return HttpResponsePermanentRedirect(
                    reverse("feeds:stream_feed", args=[t_category.m_stream.slug])
                )
            else:
                # Redirect to stream page
                return HttpResponsePermanentRedirect(
                    reverse("public:stream", args=[t_category.m_stream.slug])
                )
    return HttpResponseNotFound()
