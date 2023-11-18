import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.timezone import now
from taggit import managers as taggit_managers

from core.constants import VISIBILITY_CHOICES, Visibility
from core.models import TimestampModel
from data.indieweb.constants import MPostKinds, MPostStatuses


class MPostStatus(TimestampModel):
    key = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "m_post_status"
        verbose_name = "Post Status"
        verbose_name_plural = "Post Statuses"

    def __str__(self):
        return self.name


class MPostKind(TimestampModel):
    key = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "m_post_kind"
        verbose_name = "Post Kind"
        verbose_name_plural = "Post Kinds"

    def __str__(self):
        return self.name

    def icon(self):
        lookup = {
            MPostKinds.note: "💬",
            MPostKinds.article: "✏️",
            MPostKinds.bookmark: "🔖",
            MPostKinds.reply: "📤",
            MPostKinds.like: "👍",
            MPostKinds.checkin: "🗺",
        }
        return lookup.get(self.key, "❓")


class TPostManager(models.Manager):
    def published(self):
        return self.get_queryset().filter(m_post_status__key=MPostStatuses.published, dt_published__lte=now())

    def drafts(self):
        return self.get_queryset().filter(
            m_post_status__key=MPostStatuses.draft,
        )

    def visible_for_user(self, user_id: int | None):
        qs = self.get_queryset()
        anon_ok_entries = Q(visibility__in=[Visibility.PUBLIC, Visibility.UNLISTED])
        if user_id:
            private_entries = Q(visibility=Visibility.PRIVATE, p_author_id=user_id)
            return qs.filter(anon_ok_entries | private_entries)
        else:
            # Anonymous users can only see published posts
            qs = qs.filter(m_post_status__key=MPostStatuses.published, dt_published__lte=now())
        return qs.filter(anon_ok_entries)


class TPost(TimestampModel):
    m_post_status = models.ForeignKey(MPostStatus, on_delete=models.CASCADE)
    m_post_kind = models.ForeignKey(MPostKind, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4)

    p_author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt_published = models.DateTimeField(blank=True, null=True)
    dt_updated = models.DateTimeField(blank=True, null=True)
    visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICES, default=Visibility.PUBLIC)

    files = models.ManyToManyField("files.TFile", through="files.TFilePost", through_fields=("t_post", "t_file"))
    streams = models.ManyToManyField(
        "streams.MStream",
        through="streams.TStreamPost",
        through_fields=("t_post", "m_stream"),
    )
    trips = models.ManyToManyField(
        "trips.TTrip",
        through="trips.TTripPost",
    )
    objects = TPostManager()
    tags = taggit_managers.TaggableManager()

    class Meta:
        db_table = "t_post"
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def get_absolute_url(self) -> str:
        return reverse("public:post_detail", args=[self.uuid])

    @property
    def is_draft(self) -> bool:
        return self.m_post_status.key == MPostStatuses.draft

    @cached_property
    def post_title(self) -> str:
        t_entry = self.ref_t_entry
        summary = t_entry.p_summary[:128]
        title = t_entry.p_name or (f"{summary}…" if len(t_entry.p_summary) > 128 else summary)
        if self.m_post_kind.key == MPostKinds.reply:
            title = f"Response to {t_entry.t_reply.title}"
        elif self.m_post_kind.key == MPostKinds.bookmark:
            t_bookmark = t_entry.t_bookmark
            title = f"Bookmark of {t_bookmark.title or t_bookmark.u_bookmark_of}"
        elif self.m_post_kind.key == MPostKinds.checkin:
            title = f"Checkin to {t_entry.t_checkin.name}"
        return title

    def update_publishing_meta(
        self,
        post_status: MPostStatus,
        visibility: Visibility,
        dt_updated: datetime.datetime | None,
        dt_published: datetime.datetime | None,
    ):
        self.m_post_status = post_status
        self.visibility = visibility
        self.dt_updated = dt_updated
        self.dt_published = dt_published
        self.save()
