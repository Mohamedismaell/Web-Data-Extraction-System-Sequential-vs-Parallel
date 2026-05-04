import time
import requests
import logging
from core.parser import parse_html, compile_results
from core.domain import SystemResult
import json

class SequentialEngine:
    @staticmethod
    def run(urls, check_cancel=None, progress_cb=None) -> SystemResult:
        start = time.perf_counter()
        results = []
        failed = 0
        total = len(urls)
        
        for i, url in enumerate(urls):
            if check_cancel and check_cancel(): 
                return SystemResult(0.0, len(results), failed, 0, [])
            
            # Integrated Counter tracking
            if progress_cb:
                progress_cb(i + 1, total, url)
            
            try:
                attempts = 3
                for attempt in range(attempts):
                    if check_cancel and check_cancel(): break
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                        resp = requests.get(url, headers=headers, timeout=10)
                        resp.raise_for_status()
                        
                        data = parse_html(url, resp.text)
                        results.append(data)
                        break
                    except Exception as e:
                        if attempt == attempts - 1:
                            failed += 1
                            logging.error(f"[Sequential] Failed {url}: {e}")
                        time.sleep(1)
            except Exception:
                pass
                
        t = time.perf_counter() - start
        
        with open("sequential_output.json", "w", encoding="utf-8") as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
            
        return compile_results(results, t, failed)
