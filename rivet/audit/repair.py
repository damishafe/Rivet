import re

from rivet.domain.models import AuditCheck, ShotCopy


def _strip_forbidden(text: str, forbidden: list[str]) -> str:
    result = text
    for claim in forbidden:
        result = re.sub(r"\b" + re.escape(claim) + r"\b", "", result, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", result).strip()


def repair_copy(copy: ShotCopy, forbidden: list[str], required: list[str]) -> ShotCopy:
    headline = _strip_forbidden(copy.headline, forbidden)
    support = _strip_forbidden(copy.support, forbidden)
    cta = _strip_forbidden(copy.cta, forbidden)
    joined = f"{headline} {support} {cta}".lower()
    for phrase in required:
        if phrase.lower() not in joined:
            support = phrase
            break
    return ShotCopy(
        headline=headline or copy.headline,
        support=support,
        cta=cta or copy.cta,
    )


def claims_failed(checks: list[AuditCheck]) -> bool:
    return any(check.check_id == "A07" and not check.passed for check in checks)
