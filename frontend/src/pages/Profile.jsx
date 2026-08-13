import { useEffect, useState } from "react";

import {
  getCurrentUser,
  logoutUser,
} from "../services/api";

function Profile({ onBack, onLogout }) {
  const [user, setUser] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [currentPassword, setCurrentPassword] =
    useState("");

  const [newPassword, setNewPassword] =
    useState("");

  const [confirmNewPassword, setConfirmNewPassword] =
    useState("");

  const [showCurrentPassword, setShowCurrentPassword] =
    useState(false);

  const [showNewPassword, setShowNewPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [changingPassword, setChangingPassword] =
    useState(false);


  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);

        const data = await getCurrentUser();

        setUser(data);

      } catch (err) {
        console.error(err);

        setError(
          err.message ||
          "Failed to load profile."
        );

      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);


  function handleLogout() {
    logoutUser();

    onLogout();
  }


  async function handleChangePassword(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      !currentPassword ||
      !newPassword ||
      !confirmNewPassword
    ) {
      setError(
        "Please fill in all password fields."
      );
      return;
    }

    if (newPassword.length < 6) {
      setError(
        "New password must be at least 6 characters long."
      );
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setError(
        "New passwords do not match."
      );
      return;
    }

    if (currentPassword === newPassword) {
      setError(
        "New password must be different from your current password."
      );
      return;
    }

    try {
      setChangingPassword(true);

      /*
       * Backend API will be connected here.
       *
       * We will add:
       *
       * changePassword(
       *   currentPassword,
       *   newPassword
       * )
       */

      setSuccess(
        "Password validation successful."
      );

    } catch (err) {
      setError(
        err.message ||
        "Failed to change password."
      );
    } finally {
      setChangingPassword(false);
    }
  }


  if (loading) {
    return (
      <div className="profile-page">

        <div className="profile-card">

          <div className="profile-loading">
            Loading profile...
          </div>

        </div>

      </div>
    );
  }


  if (error && !user) {
    return (
      <div className="profile-page">

        <div className="profile-card">

          <div className="profile-error">
            {error}
          </div>

          <button
            className="secondary-button"
            onClick={onBack}
          >
            Back to Dashboard
          </button>

        </div>

      </div>
    );
  }


  return (
    <div className="profile-page">

      <div className="profile-card">

        {/* PROFILE HEADER */}

        <div className="profile-header">

          <div className="profile-avatar">
            {user?.name
              ? user.name
                  .charAt(0)
                  .toUpperCase()
              : "U"}
          </div>

          <h1>
            {user?.name || "User"}
          </h1>

          <p>
            {user?.email || ""}
          </p>

        </div>


        {/* ERROR */}

        {error && (
          <div className="profile-error">
            {error}
          </div>
        )}


        {/* SUCCESS */}

        {success && (
          <div className="login-success">
            {success}
          </div>
        )}


        {/* ACCOUNT INFORMATION */}

        <div className="profile-section">

          <h2>
            Account Information
          </h2>


          <div className="profile-info">

            <div className="profile-info-item">

              <span className="profile-label">
                Full Name
              </span>

              <strong>
                {user?.name ||
                  "Not available"}
              </strong>

            </div>


            <div className="profile-info-item">

              <span className="profile-label">
                Email
              </span>

              <strong>
                {user?.email ||
                  "Not available"}
              </strong>

            </div>

          </div>

        </div>


        {/* CHANGE PASSWORD */}

        <div className="profile-section">

          <h2>
            Change Password
          </h2>

          <form
            onSubmit={handleChangePassword}
            className="password-form"
          >

            {/* CURRENT PASSWORD */}

            <div className="form-group">

              <label htmlFor="current-password">
                Current Password
              </label>

              <div className="password-wrapper">

                <input
                  id="current-password"
                  type={
                    showCurrentPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter current password"
                  value={currentPassword}
                  onChange={(event) =>
                    setCurrentPassword(
                      event.target.value
                    )
                  }
                  autoComplete="current-password"
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowCurrentPassword(
                      !showCurrentPassword
                    )
                  }
                >
                  {showCurrentPassword
                    ? "🙈"
                    : "👁"}
                </button>

              </div>

            </div>


            {/* NEW PASSWORD */}

            <div className="form-group">

              <label htmlFor="new-password">
                New Password
              </label>

              <div className="password-wrapper">

                <input
                  id="new-password"
                  type={
                    showNewPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(event) =>
                    setNewPassword(
                      event.target.value
                    )
                  }
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowNewPassword(
                      !showNewPassword
                    )
                  }
                >
                  {showNewPassword
                    ? "🙈"
                    : "👁"}
                </button>

              </div>

            </div>


            {/* CONFIRM NEW PASSWORD */}

            <div className="form-group">

              <label htmlFor="confirm-new-password">
                Confirm New Password
              </label>

              <div className="password-wrapper">

                <input
                  id="confirm-new-password"
                  type={
                    showConfirmPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Confirm new password"
                  value={confirmNewPassword}
                  onChange={(event) =>
                    setConfirmNewPassword(
                      event.target.value
                    )
                  }
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowConfirmPassword(
                      !showConfirmPassword
                    )
                  }
                >
                  {showConfirmPassword
                    ? "🙈"
                    : "👁"}
                </button>

              </div>

            </div>


            {/* CHANGE PASSWORD BUTTON */}

            <button
              type="submit"
              className="change-password-button"
              disabled={changingPassword}
            >
              {changingPassword
                ? "Changing Password..."
                : "Change Password"}
            </button>

          </form>

        </div>


        {/* ACTIONS */}

        <div className="profile-actions">

          <button
            className="secondary-button"
            onClick={onBack}
          >
            ← Back to Dashboard
          </button>


          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </div>

    </div>
  );
}

export default Profile;