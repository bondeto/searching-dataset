"""
Kaggle Dataset Searcher.
Uses the official Kaggle REST API (requires KAGGLE_USERNAME + KAGGLE_KEY).
Falls back gracefully if credentials are missing.
"""
from __future__ import annotations
import httpx
from models import Dataset
from config import KAGGLE_USERNAME, KAGGLE_KEY, HTTP_TIMEOUT, HTTP_HEADERS


def _humanize_bytes(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} PB"


async def search(query: str, max_results: int = 10) -> list[Dataset]:
    if not KAGGLE_USERNAME or not KAGGLE_KEY:
        return []

    url = "https://www.kaggle.com/api/v1/datasets/list"
    params = {"search": query, "page": 1, "pageSize": max_results}
    auth = (KAGGLE_USERNAME, KAGGLE_KEY)

    try:
        async with httpx.AsyncClient(
            headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT, follow_redirects=True
        ) as client:
            resp = await client.get(url, params=params, auth=auth)
            resp.raise_for_status()
            items = resp.json()
    except Exception:
        return []

    results: list[Dataset] = []
    for item in items:
        ref = item.get("ref", "")
        results.append(
            Dataset(
                title=item.get("title", ref),
                source="kaggle",
                url=f"https://www.kaggle.com/datasets/{ref}",
                description=item.get("subtitle", ""),
                tags=[t.get("name", "") for t in item.get("tags", [])],
                size=_humanize_bytes(item.get("totalBytes", 0)),
                license=item.get("licenseName", "Unknown"),
                downloads=item.get("downloadCount", 0),
                votes=item.get("voteCount", 0),
                author=item.get("ownerName", ""),
                last_updated=item.get("lastUpdated", "")[:10],
            )
        )
    return results
