from typing import Union, Dict, List
from django.views.generic import ListView
from django.db.models import Count, Q, F
from django.shortcuts import get_object_or_404, render
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from entry.models import TEntry, TLocation
from core.constants import Visibility
from indieweb.constants import MPostStatuses, MPostKinds
from post.models import TPost
from streams.models import MStream
from trips.models import TTrip


from .forms import SearchForm


class HomeView(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            TEntry.objects.visible_for_user(self.request.user.id)
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
            .exclude(t_post__visibility=Visibility.UNLISTED)
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "selected": ["home"],
                "streams": MStream.objects.visible(self.request.user),
            }
        )
        return context


def status_detail(request, uuid):
    t_post: TPost = get_object_or_404(
        TPost.objects.visible_for_user(request.user.id)
        .filter(m_post_status__key=MPostStatuses.published)
        .select_related(
            "m_post_kind",
            "ref_t_entry",
            "ref_t_entry__t_reply",
            "ref_t_entry__t_bookmark",
            "ref_t_entry__t_checkin",
            "ref_t_entry__t_location",
        )
        .prefetch_related("streams", "ref_t_entry__t_syndication"),
        uuid=uuid,
    )
    t_entry = t_post.ref_t_entry
    webmentions = t_post.ref_t_webmention.filter(approval_status=True).select_related("t_post", "t_webmention_response")
    detail_template = f"public/entry/{t_post.m_post_kind.key}_item.html"

    context = {
        "t_post": t_post,
        "detail_template": detail_template,
        "webmentions": webmentions,
        "webmentions_count": webmentions.count(),
        "t_entry": t_entry,
        "now": now(),
        "selected": [stream.slug for stream in t_post.streams.all()],
        "title": t_entry.p_name if t_entry.p_name else t_entry.p_summary[:140],
        "streams": MStream.objects.visible(request.user),
        "public": True,
        "open_interactions": request.GET.get("o"),
    }
    return render(request, "public/post/post_detail.html", context=context)


class AuthorDetail(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
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
            .filter(
                t_post__m_post_status__key=MPostStatuses.published,
                t_post__p_author__username__exact=self.kwargs["username"],
            )
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )


class StreamView(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    @cached_property
    def stream(self):
        return get_object_or_404(MStream.objects.visible(self.request.user), slug=self.kwargs["stream_slug"])

    def get_queryset(self):

        return (
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
            .filter(t_post__in=self.stream.posts.published())
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "stream": self.stream,
                "selected": [self.stream.slug],
                "streams": MStream.objects.visible(self.request.user),
            }
        )
        return context


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


def trip_detail(request, uuid):
    t_trip: TTrip = get_object_or_404(
        (
            TTrip.objects.visible_for_user(request.user.id).prefetch_related(
                "posts",
                "posts__m_post_kind",
                "posts__p_author",
                "posts__ref_t_entry",
                "posts__ref_t_entry__t_location",
                "posts__ref_t_entry__t_bookmark",
                "posts__ref_t_entry__t_reply",
                "posts__ref_t_entry__t_checkin",
            )
        ),
        uuid=uuid,
    )
    posts = (
        TPost.objects.visible_for_user(request.user.id)
        .filter(m_post_status__key=MPostStatuses.published, trips=t_trip)
        .select_related(
            "m_post_kind",
            "ref_t_entry",
            "ref_t_entry__t_reply",
            "ref_t_entry__t_bookmark",
            "ref_t_entry__t_checkin",
            "ref_t_entry__t_location",
        )
    )
    if not request.user.is_authenticated:
        posts = posts.exclude(visibility=Visibility.UNLISTED)
    posts = posts.order_by("dt_published")
    context = {"t_trip": t_trip, "t_posts": posts, "selected": ["trips"], "title": t_trip.name}
    return render(request, "public/trips/trip_detail.html", context=context)


class TripListView(ListView):
    template_name = "public/trips/ttrip_list.html"

    def get_queryset(self):
        qs = (
            TTrip.objects.visible_for_user(self.request.user.id)
            .exclude(visibility=Visibility.UNLISTED)
            .prefetch_related("t_trip_location")
        )
        return qs

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, nav="trips", **kwargs)
        locations = (
            TLocation.objects.filter(t_entry__t_post__trips__in=context["object_list"])
            .exclude(t_entry__t_post__visibility=Visibility.UNLISTED)
            .annotate(trip_id=F("t_entry__t_post__trips__pk"))
            .values_list("trip_id", "point")
        )
        t_location_points: Dict[int, List[Point]] = {}
        for trip_id, point in locations:
            points = t_location_points.get(trip_id, [])
            points.append(point)
            t_location_points[trip_id] = points
        context.update(
            {
                "selected": ["trips"],
                "streams": MStream.objects.visible(self.request.user),
                "t_location_points": t_location_points,
                "title": "Trips",
            }
        )
        return context


def cluster_map(request):

    posts = TPost.objects.visible_for_user(request.user.id).filter(
        m_post_status__key=MPostStatuses.published, m_post_kind__key=MPostKinds.checkin
    )
    if not request.user.is_authenticated:
        posts = posts.exclude(visibility=Visibility.UNLISTED)
    posts = posts.values("uuid", "ref_t_entry__t_checkin__name", "ref_t_entry__t_location__point")
    context = {"t_posts": posts, "selected": ["maps"], "title": "Checkin Cluster Map"}
    return render(request, "public/maps/cluster.html", context=context)
