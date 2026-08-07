import time
from datetime import datetime

from sqlalchemy.orm import Session
from zapv2 import ZAPv2

from app.models.scan import Scan
from app.models.scan_result import ScanResult
from app.models.website import Website


class FullScanService:

    @staticmethod
    def execute(
        website: Website,
        db: Session,
    ):

        # -----------------------------
        # Clean URL
        # -----------------------------
        url = website.url.strip().rstrip("/")

        # -----------------------------
        # Create Scan Record
        # -----------------------------
        scan = Scan(
            user_id=website.user_id,
            website_id=website.id,
            status="Running",
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        print(f"\nCreated Scan ID: {scan.id}")

        try:

            # -----------------------------
            # Connect to ZAP
            # -----------------------------
            zap = ZAPv2(
                proxies={
                    "http": "http://127.0.0.1:8080",
                    "https": "http://127.0.0.1:8080",
                }
            )

            # -----------------------------
            # Fresh Session
            # -----------------------------
            print("\nCreating Fresh ZAP Session...")

            zap.core.new_session(
                name=f"scan_{scan.id}",
                overwrite=True,
            )

            print("Fresh Session Created")

            # -----------------------------
            # Open Website
            # -----------------------------
            print(f"\nOpening {url}")

            zap.urlopen(url)

            # Force the URL into the Sites tree
            zap.core.access_url(url)

            # Give ZAP more time to build the site tree
            time.sleep(5)

            # -----------------------------
            # Spider
            # -----------------------------
            print("\nStarting Spider...")

            spider_id = zap.spider.scan(url)

            while int(zap.spider.status(spider_id)) < 100:

                print(
                    f"Spider Progress: {zap.spider.status(spider_id)}%"
                )

                time.sleep(2)

            # Give passive scanner time to index discovered pages
            time.sleep(5)

            print("\n========== URLs DISCOVERED ==========")

            urls = zap.core.urls()

            print(f"Total URLs: {len(urls)}")

            for discovered in urls:
                print(discovered)

            print("Spider Completed")

            print("\nSites after Spider:")
            print("\nURLs discovered:")

            urls = zap.core.urls()

            print(len(urls))

            for u in urls:
                print(u)

            # -----------------------------
            # Passive Scan
            # -----------------------------
            print("\nWaiting for Passive Scan...")

            while int(zap.pscan.records_to_scan) > 0:

                print(
                    f"Remaining Records: {zap.pscan.records_to_scan}"
                )

                time.sleep(1)

            print("Passive Scan Completed")

            # -----------------------------
            # Active Scan
            # -----------------------------
            print("\nStarting Active Scan...")

            print("\nStarting Active Scan...")

            active_scan_id = zap.ascan.scan(
                url=url,
                recurse=True,
                inscopeonly=False,
            )

            while int(zap.ascan.status(active_scan_id)) < 100:

                print(
                    f"Active Scan: {zap.ascan.status(active_scan_id)}%"
                )

                time.sleep(3)

            print("Active Scan Completed")
            
            while int(zap.ascan.status(active_scan_id)) < 100:

                print(
                    f"Active Scan: {zap.ascan.status(active_scan_id)}%"
                )

                time.sleep(2)

            print("Active Scan Completed")

            print("\nSites after Active Scan:")
            print(zap.core.sites)

            # -----------------------------
            # Fetch Alerts
            # -----------------------------
            print("\nFetching Alerts...")

            print("\nSites Found:")
            print(zap.core.sites)

            # IMPORTANT:
            # Fetch ALL alerts while debugging
            alerts = zap.core.alerts(
            start=0,
            count=9999,
            )

            print("\n========== ALERTS ==========")
            print(f"Total Alerts: {len(alerts)}")

            for alert in alerts:
                print(
                    f"[{alert.get('risk')}] "
                    f"{alert.get('alert')} "
                    f"{alert.get('url')}"
                )

            print("\n" + "=" * 60)
            print(f"TOTAL ALERTS FOUND: {len(alerts)}")
            print("=" * 60)

            for alert in alerts:
                print(
                    f"[{alert.get('risk')}] "
                    f"{alert.get('alert')} "
                    f"-> {alert.get('url')}"
                )

            high = 0
            medium = 0
            low = 0
            info = 0

            # -----------------------------
            # Save Scan Results
            # -----------------------------
            for alert in alerts:

                risk = alert.get("risk", "Informational")

                if risk == "High":
                    high += 1

                elif risk == "Medium":
                    medium += 1

                elif risk == "Low":
                    low += 1

                else:
                    info += 1

                result = ScanResult(
                    scan_id=scan.id,

                    name=alert.get("alert", ""),
                    risk=risk,
                    confidence=alert.get("confidence", ""),

                    description=alert.get("description", ""),
                    solution=alert.get("solution", ""),
                    reference=alert.get("reference", ""),

                    url=alert.get("url", ""),
                    param=alert.get("param", ""),
                    attack=alert.get("attack", ""),
                    evidence=alert.get("evidence", ""),

                    cwe_id=(
                        int(alert["cweid"])
                        if alert.get("cweid") not in ("", None)
                        else None
                    ),

                    wasc_id=(
                        int(alert["wascid"])
                        if alert.get("wascid") not in ("", None)
                        else None
                    ),
                )

                db.add(result)

            # -----------------------------
            # Calculate Security Score
            # -----------------------------
            score = 100

            score -= high * 15
            score -= medium * 7
            score -= low * 2

            if score < 0:
                score = 0

            # -----------------------------
            # Update Scan
            # -----------------------------
            scan.status = "Completed"

            scan.security_score = score
            scan.total_alerts = len(alerts)

            scan.high_count = high
            scan.medium_count = medium
            scan.low_count = low
            scan.info_count = info

            scan.completed_at = datetime.utcnow()

            db.commit()
            db.refresh(scan)

            print("\nScan Saved Successfully!")

            return {
                "scan_id": scan.id,
                "website": website.url,
                "status": scan.status,
                "security_score": scan.security_score,
                "total_alerts": scan.total_alerts,
                "high": scan.high_count,
                "medium": scan.medium_count,
                "low": scan.low_count,
                "info": scan.info_count,
            }

        except Exception as e:

            db.rollback()

            scan.status = "Failed"
            scan.completed_at = datetime.utcnow()

            db.add(scan)
            db.commit()

            raise