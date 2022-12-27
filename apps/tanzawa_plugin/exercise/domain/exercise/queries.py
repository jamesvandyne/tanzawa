from tanzawa_plugin.exercise.data.exercise import models


def get_activity_by_vendor_id(vendor_id: str) -> models.Activity | None:
    try:
        return models.Activity.objects.get(vendor_id=vendor_id)
    except models.Activity.DoesNotExist:
        return None
