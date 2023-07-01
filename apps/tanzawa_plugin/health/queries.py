import datetime

import arrow
from django.db.models import Q
from django.utils import timezone

from . import constants


def get_date_filter(duration: constants.GraphDuration | None = None) -> Q | None:
    """
    Return the Q object for a given duration.
    """
    match duration:
        case constants.GraphDuration.SIX_WEEKS:
            return Q(measured_at__date__gte=_get_six_weeks_ago())
        case constants.GraphDuration.MONTH_TO_DATE:
            return Q(measured_at__date__gte=_get_first_of_month())
        case constants.GraphDuration.LAST_MONTH:
            last_month = _get_last_month()
            return Q(measured_at__range=[d.datetime for d in last_month])
        case [constants.GraphDuration.ALL, _]:
            return None
    return None


def _get_six_weeks_ago() -> datetime.date:
    six_weeks_ago = arrow.get(timezone.now()).shift(weeks=-6)
    return six_weeks_ago.date()


def _get_first_of_month() -> datetime.date:
    now = timezone.now()
    return datetime.date(year=now.year, month=now.month, day=1)


def _get_last_month() -> tuple[arrow.Arrow, arrow.Arrow]:
    last_month = arrow.get(timezone.now()).shift(months=-1)
    return last_month.span("month")
