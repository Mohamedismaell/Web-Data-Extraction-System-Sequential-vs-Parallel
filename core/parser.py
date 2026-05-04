import re
from collections import Counter
from bs4 import BeautifulSoup
from typing import List
from core.domain import ExtractedData, SystemResult
import itertools

STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 
    'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 
    'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 
    'should', 'now', 'said', 'says', 'also', 'could', 'would', 'like', 'many', 'much', 'even',
    'well', 'way', 'may', 'see', 'make', 'get', 'use', 'know', 'take', 'come', 'go', 'think',
    'one', 'two', 'new', 'time', 'first', 'people', 'year', 'made', 'part', 'http', 'https', 'com'
}

def parse_html(url: str, html: str) -> ExtractedData:
    soup = BeautifulSoup(html, 'html.parser')
    
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
    
    paragraphs = soup.find_all('p')
    text = " ".join([p.get_text(separator=" ", strip=True) for p in paragraphs])
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    filtered_words = [w for w in words if w not in STOP_WORDS]
    
    word_count = len(words)
    
    c = Counter(filtered_words)
    top_words = [word for word, freq in c.most_common(5)]
    
    raw_links = [a.get('href') for a in soup.find_all('a', href=True)]
    clean_links = list(set([lnk for lnk in raw_links if isinstance(lnk, str) and lnk.startswith('http')]))
    
    return ExtractedData(
        url=url,
        title=title,
        word_count=word_count,
        top_words=top_words,
        links=clean_links
    )

def compile_results(results: List[ExtractedData], time_taken: float, failed_urls: int) -> SystemResult:
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
