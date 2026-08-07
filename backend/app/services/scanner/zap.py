import time
from zapv2 import ZAPv2


class ZapScanner:

    def __init__(self):
        self.zap = ZAPv2(
            proxies={
                "http": "http://127.0.0.1:8080",
                "https": "http://127.0.0.1:8080",
            }
        )

    def version(self):
        return {
            "version": self.zap.core.version
        }

    def full_scan(self, url: str):

        print("Opening URL...")
        self.zap.urlopen(url)

        time.sleep(2)

        print("Starting Spider...")
        spider_id = self.zap.spider.scan(url)

        while int(self.zap.spider.status(spider_id)) < 100:
            print("Spider:", self.zap.spider.status(spider_id))
            time.sleep(2)

        print("Spider Finished")

        print("Passive Scan...")

        while int(self.zap.pscan.records_to_scan) > 0:
            print("Remaining:", self.zap.pscan.records_to_scan)
            time.sleep(2)

        print("Passive Scan Finished")

        print("Starting Active Scan...")

        scan_id = self.zap.ascan.scan(url)

        while int(self.zap.ascan.status(scan_id)) < 100:
            print("Active:", self.zap.ascan.status(scan_id))
            time.sleep(5)

        print("Active Scan Finished")

        alerts = self.zap.core.alerts(baseurl=url)

        return {
            "url": url,
            "total_alerts": len(alerts),
            "alerts": alerts,
        }