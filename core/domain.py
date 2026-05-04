from dataclasses import dataclass
from typing import List

@dataclass
class ExtractedData:
    url: str
    title: str
    word_count: int
    top_words: List[str]
    links: List[str]

@dataclass
class SystemResult:
    time_taken: float
    successful_urls: int
    failed_urls: int
    total_words: int
    top_global_words: List[str]
