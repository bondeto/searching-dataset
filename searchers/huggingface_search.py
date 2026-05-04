"""
HuggingFace Dataset Searcher.
Uses the official HuggingFace Hub API.
"""
from __future__ import annotations
import httpx
from models import Dataset
from config import HF_TOKEN, HTTP_TIMEOUT, HTTP_HEADERS

async def search(query: str, max_results: int = 10) -> list[Dataset]:
    url = "https://huggingface.co/api/datasets"
    params = {"search": query, "limit": max_results, "full": "true"}
    headers = {**HTTP_HEADERS}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    try:
        async with httpx.AsyncClient(headers=headers, timeout=HTTP_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            items = resp.json()
    except Exception:
        return []

    results: list[Dataset] = []
    for item in items:
        # Extract metadata
        card_data = item.get("cardData", {})
        tags = item.get("tags", [])
        
        results.append(
            Dataset(
                title=item.get("id", ""),
                source="huggingface",
                url=f"https://huggingface.co/datasets/{item.get('id')}",
                description=card_data.get("description", "HuggingFace Dataset"),
                tags=tags[:10],
                downloads=item.get("downloads", 0),
                votes=item.get("likes", 0),
                author=item.get("author", "Unknown"),
                last_updated=item.get("lastModified", "")[:10]
            )
        )
    return results
