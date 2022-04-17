from typing import Dict, List

from core.constants import Visibility
from data.entry.models import TLocation
from data.indieweb.constants import MPostStatuses
from data.post.models import TPost
from data.streams.models import MStream
from data.trips.models import TTrip
from django.contrib.gis.geos import Point
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView


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
