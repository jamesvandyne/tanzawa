from typing import Optional

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotFound,
    HttpResponsePermanentRedirect,
)
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from wordpress.models import TCategory, TWordpressPost


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
        t_category = TCategory.objects.filter(m_stream__isnull=False, nice_name=parts[2]).first()
        if t_category:
            if request.path.endswith("feed"):
                # Redirect stream feeds
                return HttpResponsePermanentRedirect(reverse("public:stream_feed", args=[t_category.m_stream.slug]))
            else:
                # Redirect to stream page
                return HttpResponsePermanentRedirect(reverse("public:stream", args=[t_category.m_stream.slug]))
    return HttpResponseNotFound()


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:

    return HttpResponse(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + '<text y=".9em" font-size="90">'
            + request.settings.icon
            + "</text>"
            + "</svg>"
        ),
        content_type="image/svg+xml",
    )
