# Platform bot linking API

from prisma.models import PlatformLink, PlatformUserLink


def redact_id(value: str | None) -> str:
    """Redact a platform / user identifier for logs.

    Keeps the last 4 chars for correlation without exposing the full
    third-party ID as PII.
    """
    if not value:
        return "<none>"
    return f"...{value[-4:]}" if len(value) > 4 else "***"


async def find_server_link(
    platform: str,
    platform_server_id: str,
) -> PlatformLink | None:
    """Look up the PlatformLink for a server (group chat / guild).

    Server and user (DM) links are independent — a user who owns a linked
    server still has to link their DMs separately via a USER-type token.
    """
    return await PlatformLink.prisma().find_first(
        where={"platform": platform, "platformServerId": platform_server_id}
    )


async def find_user_link(
    platform: str,
    platform_user_id: str,
) -> PlatformUserLink | None:
    """Look up the PlatformUserLink for an individual user's DMs with the bot."""
    return await PlatformUserLink.prisma().find_unique(
        where={
            "platform_platformUserId": {
                "platform": platform,
                "platformUserId": platform_user_id,
            }
        }
    )
