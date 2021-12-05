from enum import IntEnum


class Visibility(IntEnum):
    PUBLIC = 1  # anyone can see
    PRIVATE = 2  # only logged-in users can see
    UNLISTED = 3  # only people who know the url / logged-in users can see

    @classmethod
    def from_micropub_property(cls, visibility: str) -> "Visibility":
        """
        Map micropub visibility into Tanzawa native visibility.
        Default to public

        refs: https://indieweb.org/Micropub-extensions#Visibility
        """
        vis_map = {
            "public": Visibility.PUBLIC,
            "private": Visibility.PRIVATE,
            "unlisted": Visibility.UNLISTED,
        }
        return vis_map.get(visibility, Visibility.PUBLIC)

    def to_micropub_property(self) -> str:
        """
        Tanzawa native visibility to micropub visibility
        Default to public

        refs: https://indieweb.org/Micropub-extensions#Visibility
        """
        vals = ["public", "private", "unlisted"]
        return vals[self.value - 1]


VISIBILITY_CHOICES = [
    (Visibility.PUBLIC.value, "Everyone"),
    (Visibility.PRIVATE.value, "Only me"),
    (Visibility.UNLISTED.value, "People who know the url"),
]
