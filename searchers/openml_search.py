"""
OpenML Dataset Searcher.
Uses the OpenML API (publicly accessible).
"""
from __future__ import annotations
import httpx
from models import Dataset
from config import HTTP_TIMEOUT, HTTP_HEADERS

async def search(query: str, max_results: int = 10) -> list[Dataset]:
    # OpenML XML API is a bit old, but they have a JSON version too
    url = f"https://www.openml.org/api/v1/json/data/list/search/{query}"

    try:
        async with httpx.AsyncClient(headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url)
            if resp.status_code == 404: # No results
                return []
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", {}).get("dataset", [])
    except Exception:
        return []

    # Handle case where only one result is returned (OpenML API quirk)
    if isinstance(items, dict):
        items = [items]

    results: list[Dataset] = []
    for item in items[:max_results]:
        ds_id = item.get("did")
        results.append(
            Dataset(
                title=item.get("name", ""),
                source="openml",
                url=f"https://www.openml.org/d/{ds_id}",
                description=f"Status: {item.get('status', 'unknown')}",
                tags=[item.get("format", "")] if item.get("format") else [],
                file_formats=[item.get("format", "")],
                author=item.get("creator", "Unknown"),
                last_updated=item.get("last_output", "")[:10]
            )
        )
    return results
