import asyncio
from playwright.async_api import async_playwright
import json
import time
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    url: str
    timestamp: float
    fcp: float
    lcp: float
    cls: float
    tbt: float
    tti: float
    fully_loaded_time: float


class WebPerformanceMonitor:
    def __init__(self, urls: list):
        self.urls = urls

    async def collect_performance_metrics(self, page):
        # Execute browser performance measurement
        performance_data = await page.evaluate("""() => {
            const metrics = {
                fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                lcp: performance.getEntriesByName('largest-contentful-paint')[0]?.startTime || 0,
                cls: performance.getEntriesByType('layout-shift').reduce((sum, entry) => sum + entry.value, 0),
                tbt: performance.getEntriesByType('long-task').reduce((sum, entry) => sum + entry.duration, 0),
                tti: performance.getEntriesByName('interactive')[0]?.startTime || 0,
                fully_loaded_time: performance.timing.loadEventEnd - performance.timing.navigationStart
            };
            return metrics;
        }""")
        print("performance_data  :  ", performance_data)
        return performance_data

    async def monitor_url(self, url):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            start_time = time.time()
            await page.goto(url, wait_until='networkidle')

            performance_metrics = await self.collect_performance_metrics(page)

            await browser.close()

            return PerformanceMetrics(
                url=url,
                timestamp=start_time,
                fcp=performance_metrics['fcp'],
                lcp=performance_metrics['lcp'],
                cls=performance_metrics['cls'],
                tbt=performance_metrics['tbt'],
                tti=performance_metrics['tti'],
                fully_loaded_time=performance_metrics['fully_loaded_time']
            )

    async def run_monitoring(self):
        tasks = [self.monitor_url(url) for url in self.urls]
        results = await asyncio.gather(*tasks)
        return results


async def main():
    urls_to_monitor = [
        'http://localhost:8018/',
        # 'https://www.facebook.com',
    ]

    monitor = WebPerformanceMonitor(urls_to_monitor)
    performance_results = await monitor.run_monitoring()

    for result in performance_results:
        print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
