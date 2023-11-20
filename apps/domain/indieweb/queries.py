from data.indieweb import constants


def emoji_for_kind(kind: str) -> str | None:
    """
    Get the common emoji for a given post kind.
    """
    lookup = {
        constants.MPostKinds.note: "💬",
        constants.MPostKinds.article: "✏️",
        constants.MPostKinds.bookmark: "🔗",
        constants.MPostKinds.reply: "↩️",
        constants.MPostKinds.like: "👍",
        constants.MPostKinds.checkin: "📍",
    }
    try:
        return lookup[kind]
    except (ValueError, KeyError):
        return None
