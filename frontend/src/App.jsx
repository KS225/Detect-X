import { useEffect, useRef, useState } from "react";

import "./App.css";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";

import {
  getCurrentUser,
  getToken,
  getWebsites,
  createWebsite,
  startScan,
  getScan,
  stopScan,
  getScanHistory,
} from "./services/api";

function App() {

  // ============================================================
  // AUTHENTICATION
  // ============================================================

  const [authenticated, setAuthenticated] = useState(
    Boolean(getToken())
  );

  const [showRegister, setShowRegister] =
    useState(false);

  const [showProfile, setShowProfile] =
    useState(false);

  // ============================================================
  // DASHBOARD DATA
  // ============================================================
  const [websites, setWebsites] = useState([]);

  const [scanHistory, setScanHistory] = useState([]);

  // ============================================================
  // ADD WEBSITE
  // ============================================================

  const [showAddWebsite, setShowAddWebsite] =
    useState(false);

  const [websiteName, setWebsiteName] =
    useState("");

  const [websiteUrl, setWebsiteUrl] =
    useState("");

  const [websiteDescription, setWebsiteDescription] =
    useState("");

  const [creatingWebsite, setCreatingWebsite] =
    useState(false);

  const [websiteError, setWebsiteError] =
    useState("");

  const [loading, setLoading] = useState(
    Boolean(getToken())
  );

  const [error, setError] = useState("");

  // ============================================================
  // ACTIVE SCANS
  //
  // Structure:
  //
  // {
  //   websiteId: {
  //      scanId: 10,
  //      progress: 45,
  //      stage: "Spider",
  //      status: "Running",
  //      data: {...}
  //   }
  // }
  // ============================================================

  const [activeScans, setActiveScans] = useState({});

  // ============================================================
  // COMPLETED SCAN DETAILS
  // ============================================================

  const [selectedScan, setSelectedScan] = useState(null);

  // ============================================================
  // POLLING TIMERS
  // ============================================================

  const pollingRefs = useRef({});


  // ============================================================
  // LOAD DASHBOARD
  // ============================================================

  useEffect(() => {

    if (!authenticated) {

      setLoading(false);

      return;
    }


    async function loadDashboard() {

      try {

        setLoading(true);

        setError("");


        // ----------------------------------------
        // Verify logged-in user
        // ----------------------------------------

        await getCurrentUser();


        // ----------------------------------------
        // Get websites
        // ----------------------------------------

        const websiteData = await getWebsites();

        setWebsites(websiteData);


        // ----------------------------------------
        // Get scan history
        // ----------------------------------------

        const historyData = await getScanHistory();

        setScanHistory(historyData);

      } catch (err) {

        console.error(err);

        localStorage.removeItem("access_token");

        setAuthenticated(false);

        setError(
          err.message || "Failed to load dashboard."
        );

      } finally {

        setLoading(false);

      }

    }


    loadDashboard();

  }, [authenticated]);


  // ============================================================
  // STOP POLLING
  // ============================================================

  function stopPolling(scanId) {

    if (pollingRefs.current[scanId]) {

      clearInterval(
        pollingRefs.current[scanId]
      );

      delete pollingRefs.current[scanId];

    }

  }


  // ============================================================
  // POLL SCAN
  // ============================================================

  function pollScan(
    websiteId,
    scanId
  ) {

    // Prevent duplicate polling
    stopPolling(scanId);


    async function checkScan() {

      try {

        const data = await getScan(scanId);


        // ----------------------------------------
        // Update active scan
        // ----------------------------------------

        setActiveScans((previous) => ({

          ...previous,

          [websiteId]: {

            scanId: scanId,

            progress:
              data.progress ?? 0,

            stage:
              data.scan_stage ||
              "Scanning",

            status:
              data.status,

            data: data,

          },

        }));


        // ----------------------------------------
        // Scan completed
        // ----------------------------------------

        if (data.status === "Completed") {

          stopPolling(scanId);


          // Keep final result visible
          setSelectedScan(data);


          // Remove from active scans
          setActiveScans((previous) => {

            const updated = {
              ...previous,
            };

            delete updated[websiteId];

            return updated;

          });


          // Refresh scan history
          try {

            const historyData =
              await getScanHistory();

            setScanHistory(
              historyData
            );

          } catch (historyError) {

            console.error(
              "Failed to refresh history:",
              historyError
            );

          }

          return;

        }


        // ----------------------------------------
        // Scan stopped
        // ----------------------------------------

        if (data.status === "Stopped") {

          stopPolling(scanId);


          setActiveScans((previous) => {

            const updated = {
              ...previous,
            };

            delete updated[websiteId];

            return updated;

          });


          setSelectedScan(data);


          try {

            const historyData =
              await getScanHistory();

            setScanHistory(
              historyData
            );

          } catch (historyError) {

            console.error(
              "Failed to refresh history:",
              historyError
            );

          }

          return;

        }


        // ----------------------------------------
        // Scan failed
        // ----------------------------------------

        if (data.status === "Failed") {

          stopPolling(scanId);


          setActiveScans((previous) => {

            const updated = {
              ...previous,
            };

            delete updated[websiteId];

            return updated;

          });


          setError(
            `Scan ${scanId} failed.`
          );

          return;

        }

      } catch (err) {

        console.error(
          "Error checking scan:",
          err
        );

      }

    }


    // Check immediately
    checkScan();


    // Then check every 2 seconds
    const interval = setInterval(
      checkScan,
      2000
    );


    pollingRefs.current[scanId] =
      interval;

  }

  // ============================================================
  // CREATE WEBSITE
  // ============================================================

  async function handleCreateWebsite(event) {

    event.preventDefault();

    setWebsiteError("");


    // ----------------------------------------------------------
    // Validate website name
    // ----------------------------------------------------------

    if (!websiteName.trim()) {

      setWebsiteError(
        "Please enter a website name."
      );

      return;
    }


    // ----------------------------------------------------------
    // Validate website URL
    // ----------------------------------------------------------

    if (!websiteUrl.trim()) {

      setWebsiteError(
        "Please enter a website URL."
      );

      return;
    }


    try {

      setCreatingWebsite(true);


      // --------------------------------------------------------
      // Send website to backend
      // --------------------------------------------------------

      const newWebsite =
        await createWebsite(
          websiteName.trim(),
          websiteUrl.trim(),
          websiteDescription.trim()
        );


      console.log(
        "Website created successfully:",
        newWebsite
      );


      // --------------------------------------------------------
      // Add website to current UI
      // --------------------------------------------------------

      setWebsites((previous) => [
        ...previous,
        newWebsite,
      ]);


      // --------------------------------------------------------
      // Clear form
      // --------------------------------------------------------

      setWebsiteName("");
      setWebsiteUrl("");
      setWebsiteDescription("");


      // --------------------------------------------------------
      // Close modal
      // --------------------------------------------------------

      setShowAddWebsite(false);

      setWebsiteError("");


    } catch (err) {

      console.error(
        "Failed to create website:",
        err
      );

      setWebsiteError(
        err.message ||
        "Failed to create website."
      );

    } finally {

      setCreatingWebsite(false);

    }

  }

  // ============================================================
  // START SCAN
  // ============================================================

  async function handleStartScan(
    website
  ) {

    const websiteId =
      website.id;


    // ----------------------------------------
    // Prevent duplicate scan
    // ----------------------------------------

    if (
      activeScans[websiteId]
    ) {

      return;

    }


    try {

      setError("");


      // ----------------------------------------
      // Start backend scan
      // ----------------------------------------

      const data =
        await startScan(
          websiteId
        );


      console.log(
        "Scan started:",
        data
      );


      const scanId =
        data.scan_id;


      // ----------------------------------------
      // Initial UI state
      // ----------------------------------------

      setActiveScans(
        (previous) => ({

          ...previous,

          [websiteId]: {

            scanId: scanId,

            progress: 0,

            stage:
              "Initializing",

            status:
              "Running",

            data: data,

          },

        })
      );


      // ----------------------------------------
      // Start polling
      // ----------------------------------------

      pollScan(
        websiteId,
        scanId
      );

    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Failed to start scan."
      );

    }

  }


  // ============================================================
  // STOP SCAN
  // ============================================================

  async function handleStopScan(
    websiteId
  ) {

    const activeScan =
      activeScans[websiteId];


    if (!activeScan) {

      return;

    }


    try {

      setError("");


      const data =
        await stopScan(
          activeScan.scanId
        );


      console.log(
        "Stop requested:",
        data
      );


      // Don't immediately remove it.
      // The polling will receive "Stopped".
      setActiveScans(
        (previous) => ({

          ...previous,

          [websiteId]: {

            ...previous[websiteId],

            status: "Stopping",

            stage:
              "Stopping scan...",

          },

        })
      );


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Failed to stop scan."
      );

    }

  }


  // ============================================================
  // VIEW SCAN
  // ============================================================

  async function handleViewScan(
    scanId
  ) {

    try {

      setError("");

      const data =
        await getScan(
          scanId
        );

      setSelectedScan(
        data
      );

    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Failed to load scan."
      );

    }

  }


  // ============================================================
  // CLEANUP POLLING
  // ============================================================

  useEffect(() => {

    return () => {

      Object.values(
        pollingRefs.current
      ).forEach(
        (interval) => {
          clearInterval(interval);
        }
      );

      pollingRefs.current = {};

    };

  }, []);


  // ============================================================
  // LOGIN
  // ============================================================

  function handleLogin() {

    setAuthenticated(true);

  }

  function handleLogout() {
    setAuthenticated(false);
    setShowProfile(false);
    setShowRegister(false);

    setWebsites([]);
  }


  // ============================================================
  // LOGIN SCREEN
  // ============================================================

  if (!authenticated) {
    return (
      <div className="app">

        {showRegister ? (
          <Register
            onRegister={() =>
              setShowRegister(false)
            }
          />
        ) : (
          <Login
            onLogin={handleLogin}
            onRegister={() =>
              setShowRegister(true)
            }
          />
        )}

      </div>
    );
  }

  if (showProfile) {
    return (
      <div className="app">

        <Profile
          onBack={() =>
            setShowProfile(false)
          }
          onLogout={handleLogout}
        />

      </div>
    );
  }

  // ============================================================
  // CALCULATE DASHBOARD STATISTICS
  // ============================================================

  const totalScans =
    scanHistory.length;


  const totalVulnerabilities =
    scanHistory.reduce(
      (total, scan) =>
        total +
        (scan.total_alerts || 0),
      0
    );


  const completedScans =
    scanHistory.filter(
      (scan) =>
        scan.status === "Completed"
    );


  const averageSecurityScore =
    completedScans.length > 0
      ? Math.round(
        completedScans.reduce(
          (total, scan) =>
            total +
            (scan.security_score || 0),
          0
        ) /
        completedScans.length
      )
      : null;


  // ============================================================
  // DASHBOARD
  // ============================================================

  return (

    <div className="app">

      {/* ======================================================
          NAVBAR
      ====================================================== */}

      <header className="navbar">

        <div className="brand">

          <div className="brand-icon">
            D
          </div>

          <div>

            <h1>
              DetectX
            </h1>

            <span>
              AI Security Assessment
            </span>

          </div>

        </div>


        <button
          className="user-section user-section-button"
          onClick={() =>
            setShowProfile(true)
          }
          type="button"
        >

          <div className="user-avatar">
            U
          </div>

          <div className="user-info">

            <strong>
              User
            </strong>

            <span>
              Security Analyst
            </span>

          </div>

        </button>

      </header>


      {/* ======================================================
          DASHBOARD
      ====================================================== */}

      <main className="dashboard">

        {/* ========================================================
    ADD WEBSITE MODAL
======================================================== */}

        {showAddWebsite && (

          <div className="modal-overlay">

            <div className="modal-card">

              <div className="modal-header">

                <div>

                  <p className="eyebrow">
                    WEBSITE SETUP
                  </p>

                  <h3>
                    Add Website
                  </h3>

                  <p>
                    Add a website to begin a security assessment.
                  </p>

                </div>


                <button
                  type="button"
                  className="modal-close"
                  onClick={() => {
                    setShowAddWebsite(false);
                    setWebsiteError("");
                  }}
                >
                  ×
                </button>

              </div>


              <form onSubmit={handleCreateWebsite}>

                {/* WEBSITE NAME */}

                <div className="form-group">

                  <label htmlFor="website-name">
                    Website Name
                  </label>

                  <input
                    id="website-name"
                    type="text"
                    placeholder="My Website"
                    value={websiteName}
                    onChange={(event) =>
                      setWebsiteName(
                        event.target.value
                      )
                    }
                    disabled={creatingWebsite}
                  />

                </div>


                {/* WEBSITE URL */}

                <div className="form-group">

                  <label htmlFor="website-url">
                    Website URL
                  </label>

                  <input
                    id="website-url"
                    type="url"
                    placeholder="https://example.com"
                    value={websiteUrl}
                    onChange={(event) =>
                      setWebsiteUrl(
                        event.target.value
                      )
                    }
                    disabled={creatingWebsite}
                  />

                </div>


                {/* DESCRIPTION */}

                <div className="form-group">

                  <label htmlFor="website-description">
                    Description
                  </label>

                  <textarea
                    id="website-description"
                    placeholder="Optional description"
                    value={websiteDescription}
                    onChange={(event) =>
                      setWebsiteDescription(
                        event.target.value
                      )
                    }
                    disabled={creatingWebsite}
                    rows="3"
                  />

                </div>


                {/* ERROR */}

                {websiteError && (

                  <div className="website-form-error">

                    {websiteError}

                  </div>

                )}


                {/* ACTIONS */}

                <div className="modal-actions">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => {
                      setShowAddWebsite(false);
                      setWebsiteError("");
                    }}
                    disabled={creatingWebsite}
                  >
                    Cancel
                  </button>


                  <button
                    type="submit"
                    className="primary-button"
                    disabled={creatingWebsite}
                  >

                    {creatingWebsite
                      ? "Adding..."
                      : "Add Website"}

                  </button>

                </div>

              </form>

            </div>

          </div>

        )}
        {/* ====================================================
            WELCOME
        ==================================================== */}

        <section className="welcome-section">

          <div>

            <p className="eyebrow">
              SECURITY OVERVIEW
            </p>

            <h2>
              Welcome to DetectX
            </h2>

            <p className="subtitle">
              AI-powered web application security
              assessment and vulnerability analysis.
            </p>

          </div>


          <button
            className="primary-button"
            onClick={() => {
              setWebsiteError("");
              setShowAddWebsite(true);
            }}
          >
            + Add Website
          </button>

        </section>


        {/* ====================================================
            ERROR
        ==================================================== */}

        {error && (

          <div className="dashboard-error">

            {error}

          </div>

        )}


        {/* ====================================================
            STATISTICS
        ==================================================== */}

        <section className="stats-grid">


          <div className="stat-card">

            <span className="stat-label">
              Websites
            </span>

            <strong className="stat-value">

              {loading
                ? "..."
                : websites.length}

            </strong>

            <span className="stat-description">
              Websites under monitoring
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Total Scans
            </span>

            <strong className="stat-value">

              {loading
                ? "..."
                : totalScans}

            </strong>

            <span className="stat-description">
              Security assessments
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Vulnerabilities
            </span>

            <strong className="stat-value">

              {loading
                ? "..."
                : totalVulnerabilities}

            </strong>

            <span className="stat-description">
              Issues detected
            </span>

          </div>


          <div className="stat-card">

            <span className="stat-label">
              Security Score
            </span>

            <strong className="stat-value score">

              {averageSecurityScore !== null
                ? averageSecurityScore
                : "--"}

            </strong>

            <span className="stat-description">
              Average security posture
            </span>

          </div>


        </section>


        {/* ====================================================
            MAIN CONTENT
        ==================================================== */}

        <section className="content-grid">


          {/* ==================================================
              WEBSITES
          ================================================== */}

          <div className="panel">


            <div className="panel-header">

              <div>

                <h3>
                  Your Websites
                </h3>

                <p>
                  Manage websites and run
                  security scans.
                </p>

              </div>

            </div>


            {error && websites.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  !
                </div>

                <h4>
                  Unable to load websites
                </h4>

                <p>
                  {error}
                </p>

              </div>

            ) : websites.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  +
                </div>

                <h4>
                  No websites added yet
                </h4>

                <p>
                  Add your first website to begin
                  a security assessment.
                </p>

                <button className="primary-button">
                  Add Website
                </button>

              </div>

            ) : (

              <div className="website-list">


                {websites.map(
                  (website) => {

                    const activeScan =
                      activeScans[
                      website.id
                      ];


                    return (

                      <div
                        className="website-item"
                        key={website.id}
                      >


                        {/* ==============================
                            WEBSITE INFORMATION
                        ============================== */}

                        <div className="website-info">

                          <strong>
                            {website.name ||
                              website.url}
                          </strong>

                          <span>
                            {website.url}
                          </span>

                        </div>


                        {/* ==============================
                            NORMAL SCAN BUTTON
                        ============================== */}

                        {!activeScan && (

                          <button
                            className="primary-button"
                            onClick={() =>
                              handleStartScan(
                                website
                              )
                            }
                          >
                            Scan
                          </button>

                        )}


                        {/* ==============================
                            ACTIVE SCAN
                        ============================== */}

                        {activeScan && (

                          <div className="scan-progress-container">


                            <div className="scan-progress-header">

                              <span>

                                {activeScan.stage}

                              </span>

                              <strong>

                                {activeScan.progress}%

                              </strong>

                            </div>


                            {/* Progress bar */}

                            <div className="progress-bar">

                              <div
                                className="progress-bar-fill"
                                style={{
                                  width: `${activeScan.progress}%`,
                                }}
                              />

                            </div>


                            <div className="scan-progress-footer">

                              <span>

                                {activeScan.status ===
                                  "Stopping"
                                  ? "Stopping scan..."
                                  : "Security scan in progress..."}

                              </span>


                              {activeScan.status ===
                                "Running" && (

                                  <button
                                    className="stop-button"
                                    onClick={() =>
                                      handleStopScan(
                                        website.id
                                      )
                                    }
                                  >
                                    Stop Scan
                                  </button>

                                )}

                            </div>


                          </div>

                        )}


                      </div>

                    );

                  }
                )}


              </div>

            )}

          </div>


          {/* ==================================================
              RECENT SCANS
          ================================================== */}

          <div className="panel">


            <div className="panel-header">

              <div>

                <h3>
                  Recent Scans
                </h3>

                <p>
                  Your latest security
                  assessments.
                </p>

              </div>

            </div>


            {scanHistory.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">
                  ✓
                </div>

                <h4>
                  No scans yet
                </h4>

                <p>
                  Your scan history will appear
                  here after you run your first
                  assessment.
                </p>

              </div>

            ) : (

              <div className="scan-history-list">

                {scanHistory
                  .slice(0, 5)
                  .map((scan) => (

                    <div
                      className="history-item"
                      key={scan.id}
                    >

                      <div>

                        <strong>
                          {scan.website}
                        </strong>

                        <span>
                          {scan.status}
                        </span>

                      </div>


                      <div className="history-right">

                        <strong>
                          {scan.security_score}
                        </strong>

                        <span>
                          {scan.total_alerts}
                          {" "}
                          vulnerabilities
                        </span>

                        <button
                          className="secondary-button"
                          onClick={() =>
                            handleViewScan(
                              scan.id
                            )
                          }
                        >
                          View
                        </button>

                      </div>

                    </div>

                  ))}

              </div>

            )}

          </div>


        </section>


        {/* ====================================================
            SELECTED SCAN DETAILS
        ==================================================== */}

        {selectedScan && (

          <section className="scan-details-panel">


            <div className="scan-details-header">

              <div>

                <p className="eyebrow">
                  SCAN RESULTS
                </p>

                <h3>
                  {selectedScan.website}
                </h3>

                <span>
                  Scan #{selectedScan.id}
                </span>

              </div>


              <button
                className="secondary-button"
                onClick={() =>
                  setSelectedScan(null)
                }
              >
                Close
              </button>

            </div>


            {/* ================================
                SUMMARY
            ================================= */}

            <div className="scan-summary-grid">


              <div className="scan-summary-card">

                <span>
                  Status
                </span>

                <strong>
                  {selectedScan.status}
                </strong>

              </div>


              <div className="scan-summary-card">

                <span>
                  Security Score
                </span>

                <strong>
                  {selectedScan.security_score}
                </strong>

              </div>


              <div className="scan-summary-card">

                <span>
                  Vulnerabilities
                </span>

                <strong>
                  {selectedScan.total_alerts}
                </strong>

              </div>


              <div className="scan-summary-card">

                <span>
                  High
                </span>

                <strong>
                  {selectedScan.high}
                </strong>

              </div>


              <div className="scan-summary-card">

                <span>
                  Medium
                </span>

                <strong>
                  {selectedScan.medium}
                </strong>

              </div>


              <div className="scan-summary-card">

                <span>
                  Low
                </span>

                <strong>
                  {selectedScan.low}
                </strong>

              </div>


            </div>


            {/* ================================
                VULNERABILITIES
            ================================= */}

            <div className="results-section">

              <h4>
                Detected Vulnerabilities
              </h4>


              {selectedScan.results?.length === 0 ? (

                <div className="empty-state">

                  <h4>
                    No vulnerabilities detected
                  </h4>

                </div>

              ) : (

                <div className="results-list">

                  {selectedScan.results?.map(
                    (result) => (

                      <div
                        className="result-card"
                        key={result.id}
                      >

                        <div className="result-header">

                          <div>

                            <span
                              className={`risk-badge risk-${(
                                result.risk || ""
                              ).toLowerCase()}`}
                            >
                              {result.risk}
                            </span>

                            <h4>
                              {result.name}
                            </h4>

                          </div>

                          <span>
                            {result.priority}
                          </span>

                        </div>


                        <div className="result-content">


                          <div>

                            <h5>
                              AI Explanation
                            </h5>

                            <p>
                              {result.ai_explanation ||
                                "No AI explanation available."}
                            </p>

                          </div>


                          <div>

                            <h5>
                              Business Impact
                            </h5>

                            <p>
                              {result.business_impact ||
                                "No business impact information available."}
                            </p>

                          </div>


                          <div>

                            <h5>
                              Technical Impact
                            </h5>

                            <p>
                              {result.technical_impact ||
                                "No technical impact information available."}
                            </p>

                          </div>


                          <div>

                            <h5>
                              Remediation
                            </h5>

                            <p>
                              {result.remediation_steps ||
                                result.solution ||
                                "No remediation information available."}
                            </p>

                          </div>


                          <div>

                            <h5>
                              Secure Coding Tip
                            </h5>

                            <p>
                              {result.secure_coding_tip ||
                                "No secure coding tip available."}
                            </p>

                          </div>


                          <div>

                            <h5>
                              Estimated Fix Time
                            </h5>

                            <p>
                              {result.estimated_fix_time ||
                                "Not available"}
                            </p>

                          </div>


                        </div>

                      </div>

                    )
                  )}

                </div>

              )}

            </div>


          </section>

        )}


      </main>

    </div>

  );

}


export default App;