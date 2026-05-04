"""
Base model for a dataset search result, shared across all sources.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Dataset:
    title: str
    source: str                       # e.g. "kaggle", "huggingface"
    url: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    size: str = "N/A"                 # human-readable
    file_formats: list[str] = field(default_factory=list)
    license: str = "Unknown"
    downloads: Optional[int] = None
    votes: Optional[int] = None
    author: str = ""
    last_updated: str = ""

    def short_desc(self, max_len: int = 120) -> str:
        d = self.description.replace("\n", " ").strip()
        return d[:max_len] + "…" if len(d) > max_len else d

    def format_tags(self) -> str:
        return ", ".join(self.tags[:5]) if self.tags else "-"

    def format_formats(self) -> str:
        return ", ".join(self.file_formats) if self.file_formats else "-"
