import time
from datetime import datetime
from threading import Event, Lock

from sqlalchemy.orm import Session
from zapv2 import ZAPv2

from app.models.scan import Scan
from app.models.scan_result import ScanResult
from app.models.website import Website
from app.services.ai.explain import AIExplainService


# ============================================================
# RUNNING SCAN CONTROL
# ============================================================

_running_scans = {}

_running_scans_lock = Lock()


class ScanStoppedException(Exception):
    pass


class FullScanService:

    # ========================================================
    # CREATE SCAN
    # ========================================================

    @staticmethod
    def create_scan(
        website: Website,
        db: Session,
    ):
        """
        Create the Scan record before the actual ZAP scan starts.
        """

        scan = Scan(
            user_id=website.user_id,
            website_id=website.id,
            status="Running",
            progress=0,
            scan_stage="Initializing",
        )

        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Register scan control
        with _running_scans_lock:

            _running_scans[scan.id] = {
                "stop_event": Event(),
                "zap": None,
                "spider_id": None,
                "active_scan_id": None,
            }

        print(
            f"\nCreated Scan ID: {scan.id}"
        )

        return scan

    # ========================================================
    # GET USER SCAN
    # ========================================================

    @staticmethod
    def get_user_scan(
        db: Session,
        scan_id: int,
        user_id: int,
    ):

        return (
            db.query(Scan)
            .filter(
                Scan.id == scan_id,
                Scan.user_id == user_id,
            )
            .first()
        )

    # ========================================================
    # STOP SCAN
    # ========================================================

    @staticmethod
    def stop_scan(
        scan_id: int,
    ):
        """
        Request the currently running scan to stop.
        """

        with _running_scans_lock:

            control = _running_scans.get(
                scan_id
            )

            if not control:
                return False

            # Set cancellation flag
            control["stop_event"].set()

            zap = control.get(
                "zap"
            )

            spider_id = control.get(
                "spider_id"
            )

            active_scan_id = control.get(
                "active_scan_id"
            )

        # ----------------------------------------------------
        # Stop Active Scan
        # ----------------------------------------------------

        if zap is not None:

            if active_scan_id:

                try:

                    print(
                        f"\nStopping Active Scan "
                        f"for Scan ID {scan_id}..."
                    )

                    zap.ascan.stop(
                        active_scan_id
                    )

                except Exception as e:

                    print(
                        f"Could not stop active scan: {e}"
                    )

            # ------------------------------------------------
            # Stop Spider
            # ------------------------------------------------

            if spider_id:

                try:

                    print(
                        f"\nStopping Spider "
                        f"for Scan ID {scan_id}..."
                    )

                    zap.spider.stop(
                        spider_id
                    )

                except Exception as e:

                    print(
                        f"Could not stop spider: {e}"
                    )

        print(
            f"\nStop requested for Scan ID: {scan_id}"
        )

        return True

    # ========================================================
    # CHECK STOP REQUEST
    # ========================================================

    @staticmethod
    def _check_stop(
        scan_id: int,
    ):

        with _running_scans_lock:

            control = _running_scans.get(
                scan_id
            )

            if not control:
                return

            if control["stop_event"].is_set():

                raise ScanStoppedException()

    # ========================================================
    # UPDATE RUNNING SCAN CONTROL
    # ========================================================

    @staticmethod
    def _update_control(
        scan_id: int,
        **kwargs,
    ):

        with _running_scans_lock:

            control = _running_scans.get(
                scan_id
            )

            if control:

                control.update(
                    kwargs
                )

    # ========================================================
    # UPDATE SCAN PROGRESS
    # ========================================================

    @staticmethod
    def _update_progress(
        db: Session,
        scan: Scan,
        progress: int,
        stage: str,
    ):
        """
        Update scan progress in the database so the frontend
        can retrieve the latest progress through GET /scanner/{id}.
        """

        # Keep progress safely between 0 and 100
        progress = max(
            0,
            min(
                progress,
                100,
            ),
        )

        scan.progress = progress
        scan.scan_stage = stage

        db.commit()

        print(
            f"[SCAN {scan.id}] "
            f"{stage} - {progress}%"
        )

    # ========================================================
    # CLEANUP
    # ========================================================

    @staticmethod
    def _cleanup(
        scan_id: int,
    ):

        with _running_scans_lock:

            _running_scans.pop(
                scan_id,
                None,
            )

    # ========================================================
    # EXECUTE FULL SCAN
    # ========================================================

    @staticmethod
    def execute(
        website: Website,
        scan_id: int,
        engine,
    ):

        # ----------------------------------------------------
        # Create independent DB session
        # ----------------------------------------------------

        db = Session(
            bind=engine
        )

        scan = None

        try:

            # =================================================
            # Get Scan
            # =================================================

            scan = (
                db.query(Scan)
                .filter(
                    Scan.id == scan_id
                )
                .first()
            )

            if not scan:

                raise Exception(
                    "Scan record not found."
                )

            # =================================================
            # Initial Progress
            # =================================================

            FullScanService._update_progress(
                db,
                scan,
                0,
                "Initializing",
            )

            # =================================================
            # Clean URL
            # =================================================

            url = (
                website.url
                .strip()
                .rstrip("/")
            )

            print(
                "\n==================================="
            )

            print(
                f"Starting Scan ID: {scan.id}"
            )

            print(
                f"Target: {url}"
            )

            print(
                "==================================="
            )

            # =================================================
            # Check Stop
            # =================================================

            FullScanService._check_stop(
                scan.id
            )

            # =================================================
            # Connect to ZAP
            # =================================================

            FullScanService._update_progress(
                db,
                scan,
                5,
                "Connecting to ZAP",
            )

            print(
                "\nConnecting to OWASP ZAP..."
            )

            zap = ZAPv2(
                proxies={
                    "http": "http://127.0.0.1:8080",
                    "https": "http://127.0.0.1:8080",
                }
            )

            # Store ZAP instance
            FullScanService._update_control(
                scan.id,
                zap=zap,
            )

            # =================================================
            # Fresh Session
            # =================================================

            FullScanService._update_progress(
                db,
                scan,
                8,
                "Creating ZAP Session",
            )

            print(
                "\nCreating Fresh ZAP Session..."
            )

            zap.core.new_session(
                name=f"scan_{scan.id}",
                overwrite=True,
            )

            print(
                "Fresh Session Created"
            )

            FullScanService._check_stop(
                scan.id
            )

            # =================================================
            # Open Website
            # =================================================

            FullScanService._update_progress(
                db,
                scan,
                10,
                "Opening Website",
            )

            print(
                f"\nOpening {url}"
            )

            zap.urlopen(
                url
            )

            zap.core.access_url(
                url
            )

            time.sleep(5)

            FullScanService._check_stop(
                scan.id
            )

            # =================================================
            # Spider
            # =================================================

            print(
                "\nStarting Spider..."
            )

            FullScanService._update_progress(
                db,
                scan,
                10,
                "Spider",
            )

            spider_id = zap.spider.scan(
                url
            )

            FullScanService._update_control(
                scan.id,
                spider_id=spider_id,
            )

            while int(
                zap.spider.status(
                    spider_id
                )
            ) < 100:

                FullScanService._check_stop(
                    scan.id
                )

                spider_progress = int(
                    zap.spider.status(
                        spider_id
                    )
                )

                # Spider gets 10% -> 40%
                overall_progress = (
                    10
                    + int(
                        spider_progress * 0.30
                    )
                )

                FullScanService._update_progress(
                    db,
                    scan,
                    overall_progress,
                    "Spider",
                )

                time.sleep(2)

            print(
                "Spider Completed"
            )

            FullScanService._update_progress(
                db,
                scan,
                40,
                "Spider Completed",
            )

            # =================================================
            # Passive Scanner
            # =================================================

            FullScanService._check_stop(
                scan.id
            )

            print(
                "\n========== URLs DISCOVERED =========="
            )

            urls = zap.core.urls()

            print(
                f"Total URLs: {len(urls)}"
            )

            for discovered in urls:

                print(
                    discovered
                )

            print(
                "\nSites after Spider:"
            )

            print(
                zap.core.sites
            )

            print(
                "\nWaiting for Passive Scan..."
            )

            FullScanService._update_progress(
                db,
                scan,
                42,
                "Passive Scan",
            )

            while int(
                zap.pscan.records_to_scan
            ) > 0:

                FullScanService._check_stop(
                    scan.id
                )

                remaining = int(
                    zap.pscan.records_to_scan
                )

                print(
                    f"Remaining Records: "
                    f"{remaining}"
                )

                time.sleep(1)

            print(
                "Passive Scan Completed"
            )

            FullScanService._update_progress(
                db,
                scan,
                50,
                "Passive Scan Completed",
            )

            # =================================================
            # Active Scan
            # =================================================

            FullScanService._check_stop(
                scan.id
            )

            print(
                "\nStarting Active Scan..."
            )

            FullScanService._update_progress(
                db,
                scan,
                50,
                "Active Scan",
            )

            active_scan_id = zap.ascan.scan(
                url=url,
                recurse=True,
                inscopeonly=False,
            )

            FullScanService._update_control(
                scan.id,
                active_scan_id=active_scan_id,
            )

            while int(
                zap.ascan.status(
                    active_scan_id
                )
            ) < 100:

                FullScanService._check_stop(
                    scan.id
                )

                active_progress = int(
                    zap.ascan.status(
                        active_scan_id
                    )
                )

                # Active scan gets 50% -> 90%
                overall_progress = (
                    50
                    + int(
                        active_progress * 0.40
                    )
                )

                FullScanService._update_progress(
                    db,
                    scan,
                    overall_progress,
                    "Active Scan",
                )

                time.sleep(3)

            print(
                "Active Scan Completed"
            )

            FullScanService._update_progress(
                db,
                scan,
                90,
                "Active Scan Completed",
            )

            # =================================================
            # Sites
            # =================================================

            print(
                "\nSites after Active Scan:"
            )

            print(
                zap.core.sites
            )

            # =================================================
            # Fetch Alerts
            # =================================================

            FullScanService._check_stop(
                scan.id
            )

            FullScanService._update_progress(
                db,
                scan,
                92,
                "Fetching Alerts",
            )

            print(
                "\nFetching Alerts..."
            )

            alerts = zap.core.alerts(
                start=0,
                count=9999,
            )

            print(
                "\n========== ALERTS =========="
            )

            print(
                f"Total Alerts: {len(alerts)}"
            )

            for alert in alerts:

                print(
                    f"[{alert.get('risk')}] "
                    f"{alert.get('alert')} "
                    f"-> {alert.get('url')}"
                )

            print(
                "\n" + "=" * 60
            )

            print(
                f"TOTAL ALERTS FOUND: "
                f"{len(alerts)}"
            )

            print(
                "=" * 60
            )

            # =================================================
            # Risk Counters
            # =================================================

            high = 0
            medium = 0
            low = 0
            info = 0

            # =================================================
            # Gemini Analysis
            # =================================================

            total_alerts = len(alerts)

            if total_alerts == 0:

                FullScanService._update_progress(
                    db,
                    scan,
                    95,
                    "No Vulnerabilities Found",
                )

            # =================================================
            # Save Scan Results
            # =================================================

            for index, alert in enumerate(alerts):

                FullScanService._check_stop(
                    scan.id
                )

                risk = alert.get(
                    "risk",
                    "Informational",
                )

                if risk == "High":

                    high += 1

                elif risk == "Medium":

                    medium += 1

                elif risk == "Low":

                    low += 1

                else:

                    info += 1

                # =================================================
                # Gemini Explanation
                # =================================================

                print(
                    f"\nGenerating AI explanation for: "
                    f"{alert.get('alert')}"
                )

                # Gemini stage: 92 -> 99
                if total_alerts > 0:

                    ai_progress = (
                        92
                        + int(
                            (
                                (index + 1)
                                / total_alerts
                            )
                            * 7
                        )
                    )

                    FullScanService._update_progress(
                        db,
                        scan,
                        ai_progress,
                        "Gemini Analysis",
                    )

                try:

                    ai = AIExplainService.execute(
                        alert
                    )

                    print(
                        "AI explanation generated successfully."
                    )

                except Exception as ai_error:

                    print(
                        "\nAI explanation failed:"
                    )

                    print(
                        ai_error
                    )

                    ai = {
                        "ai_explanation": "",
                        "business_impact": "",
                        "technical_impact": "",
                        "remediation_steps": "",
                        "secure_coding_tip": "",
                        "priority": "",
                        "estimated_fix_time": "",
                    }

                # =================================================
                # CWE
                # =================================================

                cwe_id = None

                if alert.get(
                    "cweid"
                ) not in (
                    "",
                    None,
                ):

                    try:

                        cwe_id = int(
                            alert.get(
                                "cweid"
                            )
                        )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        cwe_id = None

                # =================================================
                # WASC
                # =================================================

                wasc_id = None

                if alert.get(
                    "wascid"
                ) not in (
                    "",
                    None,
                ):

                    try:

                        wasc_id = int(
                            alert.get(
                                "wascid"
                            )
                        )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        wasc_id = None

                # =================================================
                # Create Scan Result
                # =================================================

                result = ScanResult(

                    scan_id=scan.id,

                    # ------------------------------------------------
                    # ZAP DATA
                    # ------------------------------------------------

                    name=alert.get(
                        "alert",
                        "",
                    ),

                    risk=risk,

                    confidence=alert.get(
                        "confidence",
                        "",
                    ),

                    description=alert.get(
                        "description",
                        "",
                    ),

                    solution=alert.get(
                        "solution",
                        "",
                    ),

                    reference=alert.get(
                        "reference",
                        "",
                    ),

                    url=alert.get(
                        "url",
                        "",
                    ),

                    param=alert.get(
                        "param",
                        "",
                    ),

                    attack=alert.get(
                        "attack",
                        "",
                    ),

                    evidence=alert.get(
                        "evidence",
                        "",
                    ),

                    cwe_id=cwe_id,

                    wasc_id=wasc_id,

                    # ------------------------------------------------
                    # GEMINI DATA
                    # ------------------------------------------------

                    ai_explanation=ai.get(
                        "ai_explanation",
                        "",
                    ),

                    business_impact=ai.get(
                        "business_impact",
                        "",
                    ),

                    technical_impact=ai.get(
                        "technical_impact",
                        "",
                    ),

                    remediation_steps=ai.get(
                        "remediation_steps",
                        "",
                    ),

                    secure_coding_tip=ai.get(
                        "secure_coding_tip",
                        "",
                    ),

                    priority=ai.get(
                        "priority",
                        "",
                    ),

                    estimated_fix_time=ai.get(
                        "estimated_fix_time",
                        "",
                    ),
                )

                db.add(
                    result
                )

                db.commit()

            # =================================================
            # Final Stop Check
            # =================================================

            FullScanService._check_stop(
                scan.id
            )

            # =================================================
            # Security Score
            # =================================================

            FullScanService._update_progress(
                db,
                scan,
                99,
                "Calculating Security Score",
            )

            score = 100

            score -= high * 15
            score -= medium * 7
            score -= low * 2

            if score < 0:

                score = 0

            # =================================================
            # Update Scan
            # =================================================

            scan.status = "Completed"

            scan.progress = 100

            scan.scan_stage = "Completed"

            scan.security_score = score

            scan.total_alerts = len(
                alerts
            )

            scan.high_count = high

            scan.medium_count = medium

            scan.low_count = low

            scan.info_count = info

            scan.completed_at = (
                datetime.utcnow()
            )

            # =================================================
            # Save
            # =================================================

            db.commit()

            db.refresh(
                scan
            )

            print(
                "\n==================================="
            )

            print(
                "Scan Saved Successfully!"
            )

            print(
                "==================================="
            )

            return {
                "scan_id": scan.id,
                "website": website.url,
                "status": scan.status,
                "progress": scan.progress,
                "scan_stage": scan.scan_stage,
                "security_score": scan.security_score,
                "total_alerts": scan.total_alerts,
                "high": scan.high_count,
                "medium": scan.medium_count,
                "low": scan.low_count,
                "info": scan.info_count,
            }

        # =====================================================
        # STOPPED
        # =====================================================

        except ScanStoppedException:

            print(
                f"\nScan {scan_id} "
                f"was stopped by the user."
            )

            db.rollback()

            scan.status = "Stopped"

            scan.scan_stage = "Stopped"

            scan.completed_at = (
                datetime.utcnow()
            )

            db.add(
                scan
            )

            db.commit()

            return {
                "scan_id": scan.id,
                "website": website.url,
                "status": "Stopped",
                "progress": scan.progress,
                "scan_stage": scan.scan_stage,
                "security_score": (
                    scan.security_score or 0
                ),
                "total_alerts": (
                    scan.total_alerts or 0
                ),
                "high": (
                    scan.high_count or 0
                ),
                "medium": (
                    scan.medium_count or 0
                ),
                "low": (
                    scan.low_count or 0
                ),
                "info": (
                    scan.info_count or 0
                ),
            }

        # =====================================================
        # FAILED
        # =====================================================

        except Exception as e:

            print(
                "\nScan failed:"
            )

            print(
                e
            )

            db.rollback()

            if scan:

                scan.status = "Failed"

                scan.scan_stage = "Failed"

                scan.completed_at = (
                    datetime.utcnow()
                )

                db.add(
                    scan
                )

                db.commit()

            raise

        # =====================================================
        # CLEANUP
        # =====================================================

        finally:

            FullScanService._cleanup(
                scan_id
            )

            db.close()

            print(
                f"\nScan control cleaned "
                f"for Scan ID: {scan_id}"
            )