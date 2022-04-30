from core.constants import Visibility
from data.indieweb.constants import MPostStatuses
from data.post.models import TPost
from data.streams.models import MStream
from data.trips.models import TTrip
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from domain.trips import queries


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
        return queries.get_public_trips_for_user(user_id=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, nav="trips", **kwargs)
        t_location_points = queries.get_points_for_trips(trips=context["object_list"])
        context.update(
            {
                "selected": ["trips"],
                "streams": MStream.objects.visible(self.request.user),
                "t_location_points": t_location_points,
                "title": "Trips",
            }
        )
        return context
