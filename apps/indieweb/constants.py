class MPostStatuses:
    """
    Post Statuses from Micropub-extentions
    https://indieweb.org/Micropub-extensions#Post_Status
    """

    published = "published"
    draft = "draft"


class MPostKinds:
    """
    Supported post-kind / microformats
    """

    article = "article"
    note = "note"
    bookmark = "bookmark"
    checkin = "checkin"
    reply = "reply"
    like = "like"


class Microformats:
    ENTRY = "entry"
    CHECKIN = "checkin"
    CARD = "card"
    EVENT = "event"
    GEO = "geo"
    REVIEW = "review"
    RESUME = "resume"

    def __contains__(self, item):
        return item in [
            self.CARD,
            self.CHECKIN,
            self.ENTRY,
            self.EVENT,
            self.GEO,
            self.REVIEW,
            self.REVIEW,
        ]


supported_microformats = Microformats()
