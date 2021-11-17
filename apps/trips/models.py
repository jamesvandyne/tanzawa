import uuid
from typing import Optional

from core.constants import VISIBILITY_CHOICES, Visibility
from core.models import TimestampModel
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.urls import reverse


class TTripManager(models.Manager):
    def visible_for_user(self, user_id: Optional[int]):
        qs = self.get_queryset()
        anon_ok_entries = models.Q(visibility__in=[Visibility.PUBLIC, Visibility.UNLISTED])
        if user_id:
            private_entries = models.Q(visibility=Visibility.PRIVATE, p_author_id=user_id)
            return qs.filter(anon_ok_entries | private_entries)
        return qs.filter(anon_ok_entries)


class TTrip(TimestampModel):

    name = models.CharField(max_length=128)
    uuid = models.UUIDField(default=uuid.uuid4)
    p_author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    p_summary = models.TextField(blank=True)
    d_start = models.DateField(verbose_name="Start Date", blank=True, null=True)
    d_end = models.DateField(verbose_name="End Date", blank=True, null=True)
    visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICES, default=Visibility.PUBLIC)

    posts = models.ManyToManyField("post.TPost", through="TTripPost")

    objects = TTripManager()

    class Meta:
        db_table = "t_trip"
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("public:trip_detail", args=[self.uuid])


class TTripLocation(TimestampModel):
    t_trip = models.ForeignKey(TTrip, on_delete=models.CASCADE, related_name="t_trip_location")
    street_address = models.CharField(max_length=128, blank=True, default="")
    locality = models.CharField(max_length=128, blank=True, default="")
    region = models.CharField(max_length=64, blank=True, default="")
    country_name = models.CharField(max_length=64, blank=True, default="")
    postal_code = models.CharField(max_length=16, blank=True, default="")
    point = geo_models.PointField(geography=True, srid=3857)

    class Meta:
        db_table = "t_trip_location"
        verbose_name = "Trip Location"
        verbose_name_plural = "Locations"

    @property
    def summary(self):
        return (
            ", ".join(filter(None, [self.locality, self.region, self.country_name])) or f"{self.point.y},{self.point.x}"
        )

    def __str__(self):
        return self.summary


class TTripPost(TimestampModel):

    t_trip = models.ForeignKey(TTrip, on_delete=models.CASCADE)
    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_trip_entry"
        verbose_name = "Trip-Post"
        verbose_name_plural = "Trip-Posts"

    def __str__(self):
        return f"{self.t_trip_id}-{self.t_post_id}"
