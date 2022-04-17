from typing import Union

from core.constants import Visibility
from data.entry.models import TEntry
from data.indieweb.constants import MPostStatuses
from data.streams.models import MStream
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Count, Q
from django.views.generic import ListView
from interfaces.public.search.forms import SearchForm


class SearchView(ListView):
    template_name = "public/search/index.html"
    paginate_by = 10
    form_class = SearchForm

    def convert_km_to_degrees(self, km: Union[float, int]):
        """
        Convert kms to degrees.
        """
        meters = D(km=km).m
        degrees = meters / 40000000 * 360
        return degrees

    def get_queryset(self):
        qs = (
            TEntry.objects.visible_for_user(self.request.user.id)
            .exclude(t_post__visibility=Visibility.UNLISTED)
            .select_related(
                "t_post",
                "t_post__m_post_kind",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
                "t_reply",
                "t_checkin",
            )
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )
        form = SearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get("q")
            lat = form.cleaned_data.get("lat")
            lon = form.cleaned_data.get("lon")
            if q:
                qs = qs.filter(Q(p_name__icontains=q) | Q(p_summary__icontains=q))
            if lat and lon:
                point = Point(y=lat, x=lon, srid=3857)
                qs = qs.filter(t_location__point__dwithin=(point, self.convert_km_to_degrees(2)))
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            object_list=object_list,
            selected=["home"],
            streams=MStream.objects.visible(self.request.user),
            form=SearchForm(self.request.GET),
        )
        context["show_map"] = any([getattr(e, "t_location", False) for e in context["object_list"]])
        return context
