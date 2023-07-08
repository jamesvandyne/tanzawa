import datetime

from django.contrib.gis import geos
from django.contrib.gis.db import models as geo_models
from django.db import models
from data.entry import models as entry_models
from . import constants


class Activity(models.Model):
    name = models.CharField(max_length=255)
    vendor_id = models.CharField(max_length=255, unique=True)
    upload_id = models.CharField(max_length=255, null=True, unique=True)

    distance = models.FloatField(help_text="Distance in meters", null=True)
    moving_time = models.PositiveIntegerField(help_text="Moving time in seconds")
    elapsed_time = models.PositiveIntegerField(help_text="Moving time in seconds")
    total_elevation_gain = models.FloatField()
    elevation_high = models.FloatField()
    elevation_low = models.FloatField()
    activity_type = models.CharField(max_length=64, choices=constants.ActivityTypeChoices.choices)
    started_at = models.DateTimeField()
    start_point = geo_models.PointField(geography=True, srid=3857)
    end_point = geo_models.PointField(geography=True, srid=3857)
    average_speed = models.FloatField(help_text="Average speed in meters per second")
    max_speed = models.FloatField()
    average_heartrate = models.FloatField(null=True)
    max_heartrate = models.FloatField(null=True)

    entry = models.ForeignKey("entry.TEntry", on_delete=models.CASCADE, null=True, related_name="activities")

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def distance_km(self) -> float:
        return self.distance / 1000

    @property
    def elapsed_time_minutes(self) -> float:
        return self.elapsed_time / 60

    @classmethod
    def new(
        cls,
        name: str,
        vendor_id: str,
        upload_id: str | None,
        distance: float | None,
        moving_time: int,
        elapsed_time: int,
        total_elevation_gain: float,
        elevation_high: float,
        elevation_low: float,
        activity_type: constants.ActivityTypeChoices,
        started_at: datetime.datetime,
        start_point: geos.Point,
        end_point: geos.Point,
        average_speed: float,
        max_speed: float,
        average_heartrate: float | None,
        max_heartrate: float | None,
    ) -> "Activity":
        return cls.objects.create(
            name=name,
            vendor_id=vendor_id,
            upload_id=upload_id,
            distance=distance,
            moving_time=moving_time,
            elapsed_time=elapsed_time,
            total_elevation_gain=total_elevation_gain,
            elevation_high=elevation_high,
            elevation_low=elevation_low,
            activity_type=activity_type,
            started_at=started_at,
            start_point=start_point,
            end_point=end_point,
            average_speed=average_speed,
            max_speed=max_speed,
            average_heartrate=average_heartrate,
            max_heartrate=max_heartrate,
        )

    def update(
        self,
        name: str,
        vendor_id: str,
        upload_id: str | None,
        distance: float | None,
        moving_time: int,
        elapsed_time: int,
        total_elevation_gain: float,
        elevation_high: float,
        elevation_low: float,
        activity_type: constants.ActivityTypeChoices,
        started_at: datetime.datetime,
        start_point: geos.Point,
        end_point: geos.Point,
        average_speed: float,
        max_speed: float,
        average_heartrate: float | None,
        max_heartrate: float | None,
    ) -> None:
        self.name = name
        self.vendor_id = vendor_id
        self.upload_id = upload_id
        self.distance = distance
        self.moving_time = moving_time
        self.elapsed_time = elapsed_time
        self.total_elevation_gain = total_elevation_gain
        self.elevation_high = elevation_high
        self.elevation_low = elevation_low
        self.activity_type = activity_type
        self.started_at = started_at
        self.start_point = start_point
        self.end_point = end_point
        self.average_speed = average_speed
        self.max_speed = max_speed
        self.average_heartrate = average_heartrate
        self.max_heartrate = max_heartrate
        self.save()


class Map(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE)
    vendor_id = models.CharField(max_length=255, default="", unique=True)
    summary_polyline = models.TextField()

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update(self, vendor_id: str, summary_polyline: str) -> None:
        self.vendor_id = vendor_id
        self.summary_polyline = summary_polyline
        self.save()


class GPXRoute(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
