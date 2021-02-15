from enum import IntEnum


class Visibility(IntEnum):
    PUBLIC = 1  # anyone can see
    PRIVATE = 2  # only logged-in users can see
    UNLISTED = 3  # only people who know the url / logged-in users can see


VISIBILITY_CHOICES = [
    (Visibility.PUBLIC.value, "Public"),
    (Visibility.PRIVATE.value, "Private"),
    (Visibility.UNLISTED.value, "Unlisted"),
]
