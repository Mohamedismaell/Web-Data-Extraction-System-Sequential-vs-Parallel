import time
import asyncio
import aiohttp
import logging
from core.parser import parse_html, compile_results
from core.domain import SystemResult
import json

class ParallelEngine:
    @staticmethod
    def run(urls, check_cancel=None, progress_cb=None) -> SystemResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        return loop.run_until_complete(ParallelEngine._async_run(urls, check_cancel, progress_cb))

    @staticmethod
    async def _async_run(urls, check_cancel=None, progress_cb=None):
        start = time.perf_counter()
        results = []
        failed = 0
        total = len(urls)
        
        # Rate Limiting via asyncio.Semaphore
        sem = asyncio.Semaphore(10) # Lowered to 10 to drastically reduce connection dropping / timeouts
        completed = [0]
        
        async def fetch(url, session):
            if check_cancel and check_cancel(): return None
            
            async with sem:
                attempts = 4 # Incremented retry attempts
                for attempt in range(attempts):
                    if check_cancel and check_cancel(): return None
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        # Increased connection timeout securely
                        async with session.get(url, headers=headers, timeout=12) as response:
                            response.raise_for_status()
                            html = await response.text()
                            
                            data = parse_html(url, html)
                            
                            completed[0] += 1
                            if progress_cb: progress_cb(completed[0], total, url)
                            return data
                    except Exception as e:
                        if attempt == attempts - 1:
                            logging.error(f"[Parallel] Failed {url}: {e}")
                            completed[0] += 1
                            if progress_cb: progress_cb(completed[0], total, f"FAILED: {url}")
                            return "FAIL"
                        # Exponential backoff for parallel traffic jams
                        await asyncio.sleep(1.5 * (attempt + 1)) 
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(url, session) for url in urls]
            outputs = await asyncio.gather(*tasks)
            
        for out in outputs:
            if out == "FAIL":
                failed += 1
            elif out is not None:
                results.append(out)
                
        t = time.perf_counter() - start
        
        with open("parallel_output.json", "w", encoding="utf-8") as f:
            json.dump([r.__dict__ for r in results], f, indent=2)
            
        return compile_results(results, t, failed)
