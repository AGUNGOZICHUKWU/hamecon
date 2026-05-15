-- Hameçon v1.0 — SQLite schema
-- All timestamps stored in UTC.
-- Foreign keys are enforced by the init script (PRAGMA foreign_keys = ON).

-- 1. roles — the two access levels
CREATE TABLE IF NOT EXISTS roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

-- 2. users — the operators of the platform (admins, viewers)
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT NOT NULL UNIQUE,
    email               TEXT NOT NULL UNIQUE,
    password_hash       TEXT NOT NULL,
    role_id             INTEGER NOT NULL,
    is_active           INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    failed_login_count  INTEGER NOT NULL DEFAULT 0,
    last_login_at       TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

-- 3. recipients — the people who can receive simulated phishing
CREATE TABLE IF NOT EXISTS recipients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    language      TEXT NOT NULL CHECK(language IN ('fr','en')),
    organisation  TEXT,
    notes         TEXT,
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. consent_records — proof that a recipient consented to participate
CREATE TABLE IF NOT EXISTS consent_records (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id     INTEGER NOT NULL,
    granted_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_user  INTEGER NOT NULL,
    scope            TEXT NOT NULL,
    expires_at       TIMESTAMP,
    revoked_at       TIMESTAMP,
    evidence_note    TEXT,
    FOREIGN KEY (recipient_id)    REFERENCES recipients(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by_user) REFERENCES users(id)      ON DELETE RESTRICT
);

-- 5. campaigns — one row per simulated phishing campaign
CREATE TABLE IF NOT EXISTS campaigns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    brief           TEXT NOT NULL,
    language        TEXT NOT NULL CHECK(language IN ('fr','en','both')),
    difficulty      TEXT NOT NULL CHECK(difficulty IN ('easy','medium','hard')),
    scenario        TEXT NOT NULL CHECK(scenario IN ('mobile_money','banking','university')),
    status          TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved','sending','completed','cancelled')),
    created_by      INTEGER NOT NULL,
    approved_by     INTEGER,
    approved_at     TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    FOREIGN KEY (created_by)  REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE RESTRICT
);

-- 6. sent_emails — each individual email sent to one recipient
CREATE TABLE IF NOT EXISTS sent_emails (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id     INTEGER NOT NULL,
    recipient_id    INTEGER NOT NULL,
    subject         TEXT NOT NULL,
    body_html       TEXT NOT NULL,
    body_plain      TEXT NOT NULL,
    tracking_token  TEXT NOT NULL UNIQUE,
    mailgun_id      TEXT,
    sent_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id)  REFERENCES campaigns(id)  ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE CASCADE
);

-- 7. click_events — every link click on a tracking URL
CREATE TABLE IF NOT EXISTS click_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_email_id  INTEGER NOT NULL,
    clicked_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address     TEXT,
    user_agent     TEXT,
    country_code   TEXT,
    FOREIGN KEY (sent_email_id) REFERENCES sent_emails(id) ON DELETE CASCADE
);

-- 8. submit_events — submission attempts on the fake landing form.
--    CRITICAL: input contents are NEVER stored. Only that a submit happened.
CREATE TABLE IF NOT EXISTS submit_events (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_email_id  INTEGER NOT NULL,
    submitted_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    input_length   INTEGER NOT NULL,
    ip_address     TEXT,
    user_agent     TEXT,
    FOREIGN KEY (sent_email_id) REFERENCES sent_emails(id) ON DELETE CASCADE
);

-- 9. training_sessions — teachable-moment views and completions
CREATE TABLE IF NOT EXISTS training_sessions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_email_id     INTEGER NOT NULL,
    lesson_text       TEXT NOT NULL,
    started_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP,
    quiz_score        INTEGER,
    seconds_on_page   INTEGER,
    FOREIGN KEY (sent_email_id) REFERENCES sent_emails(id) ON DELETE CASCADE
);

-- 10. audit_log — every meaningful admin action
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    action      TEXT NOT NULL,
    target      TEXT,
    details     TEXT,
    ip_address  TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for the queries we will actually run
CREATE INDEX IF NOT EXISTS idx_users_email             ON users(email);
CREATE INDEX IF NOT EXISTS idx_recipients_email        ON recipients(email);
CREATE INDEX IF NOT EXISTS idx_consent_recipient       ON consent_records(recipient_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status        ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_sent_emails_campaign    ON sent_emails(campaign_id);
CREATE INDEX IF NOT EXISTS idx_sent_emails_recipient   ON sent_emails(recipient_id);
CREATE INDEX IF NOT EXISTS idx_sent_emails_token       ON sent_emails(tracking_token);
CREATE INDEX IF NOT EXISTS idx_click_events_sent       ON click_events(sent_email_id);
CREATE INDEX IF NOT EXISTS idx_submit_events_sent      ON submit_events(sent_email_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_sent  ON training_sessions(sent_email_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user          ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created       ON audit_log(created_at);

-- Seed the two roles (idempotent — re-running never duplicates)
INSERT OR IGNORE INTO roles (name, description) VALUES
    ('admin',  'Full administrative access — can create, approve, and send campaigns'),
    ('viewer', 'Read-only access to reports and audit logs');
