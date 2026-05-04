import re
from collections import Counter
from bs4 import BeautifulSoup
from typing import List
from core.domain import ExtractedData, SystemResult
import itertools

def parse_html(url: str, html: str) -> ExtractedData:
    """Parses raw HTML structure intelligently resolving titles, inner paragraphs, word counts, and hyper-links."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Page Title
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
    
    # 2. Paragraph Text aggregation
    paragraphs = soup.find_all('p')
    text = " ".join([p.get_text(separator=" ", strip=True) for p in paragraphs])
    
    # 3. Word Analysis
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stop_words = {"that", "with", "this", "from", "they", "have", "were", "what", "there", "their"}
    filtered_words = [w for w in words if w not in stop_words]
    
    word_count = len(words)
    c = Counter(filtered_words)
    top_words = [word for word, freq in c.most_common(5)]
    
    # 4. Link Extraction (Duplicate Cleaned)
    raw_links = [a.get('href') for a in soup.find_all('a', href=True)]
    clean_links = list(set([lnk for lnk in raw_links if lnk.startswith('http')]))
    
    return ExtractedData(
        url=url,
        title=title,
        word_count=word_count,
        top_words=top_words,
        links=clean_links
    )

def compile_results(results: List[ExtractedData], time_taken: float, failed_urls: int) -> SystemResult:
    """Consolidates single extractions into macro system data properties"""
    total_words = sum(r.word_count for r in results)
    
    all_top = list(itertools.chain.from_iterable(r.top_words for r in results))
    c = Counter(all_top)
    top_global = [w for w, f in c.most_common(5)]
    
    return SystemResult(
        time_taken=round(time_taken, 2),
        successful_urls=len(results),
        failed_urls=failed_urls,
        total_words=total_words,
        top_global_words=top_global
    )
