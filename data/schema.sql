
-- Hamecon v1.0 - SQLite schema (channel-aware: email + SMS)
-- All timestamps stored in UTC. Foreign keys enforced by the init script.

CREATE TABLE IF NOT EXISTS roles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    username           TEXT NOT NULL UNIQUE,
    email              TEXT NOT NULL UNIQUE,
    password_hash      TEXT NOT NULL,
    role_id            INTEGER NOT NULL,
    is_active          INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    last_login_at      TIMESTAMP,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS recipients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name    TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE,
    phone        TEXT,
    language     TEXT NOT NULL CHECK(language IN ('fr','en')),
    organisation TEXT,
    notes        TEXT,
    is_active    INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consent_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id    INTEGER NOT NULL,
    granted_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_user INTEGER NOT NULL,
    scope           TEXT NOT NULL,
    expires_at      TIMESTAMP,
    revoked_at      TIMESTAMP,
    evidence_note   TEXT,
    FOREIGN KEY (recipient_id)    REFERENCES recipients(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by_user) REFERENCES users(id)      ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS campaigns (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    brief         TEXT NOT NULL,
    channel       TEXT NOT NULL DEFAULT 'email' CHECK(channel IN ('email','sms')),
    language      TEXT NOT NULL CHECK(language IN ('fr','en')),
    difficulty    TEXT NOT NULL CHECK(difficulty IN ('easy','medium','hard')),
    scenario      TEXT NOT NULL CHECK(scenario IN ('mobile_money','banking','university')),
    status        TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','approved','sending','completed','cancelled')),
    draft_subject TEXT,
    draft_body    TEXT,
    created_by    INTEGER NOT NULL,
    approved_by   INTEGER,
    approved_at   TIMESTAMP,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at    TIMESTAMP,
    completed_at  TIMESTAMP,
    FOREIGN KEY (created_by)  REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS sent_messages (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id    INTEGER NOT NULL,
    recipient_id   INTEGER NOT NULL,
    channel        TEXT NOT NULL DEFAULT 'email' CHECK(channel IN ('email','sms')),
    subject        TEXT,
    body           TEXT NOT NULL,
    tracking_token TEXT NOT NULL UNIQUE,
    provider_id    TEXT,
    sent_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id)  REFERENCES campaigns(id)  ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS click_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_message_id INTEGER NOT NULL,
    clicked_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address      TEXT,
    user_agent      TEXT,
    country_code    TEXT,
    FOREIGN KEY (sent_message_id) REFERENCES sent_messages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS submit_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_message_id INTEGER NOT NULL,
    submitted_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    input_length    INTEGER NOT NULL,
    ip_address      TEXT,
    user_agent      TEXT,
    FOREIGN KEY (sent_message_id) REFERENCES sent_messages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS training_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_message_id INTEGER NOT NULL,
    lesson_text     TEXT NOT NULL,
    started_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,
    quiz_score      INTEGER,
    seconds_on_page INTEGER,
    FOREIGN KEY (sent_message_id) REFERENCES sent_messages(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    action     TEXT NOT NULL,
    target     TEXT,
    details    TEXT,
    ip_address TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email             ON users(email);
CREATE INDEX IF NOT EXISTS idx_recipients_email        ON recipients(email);
CREATE INDEX IF NOT EXISTS idx_consent_recipient       ON consent_records(recipient_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status        ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_sent_messages_campaign  ON sent_messages(campaign_id);
CREATE INDEX IF NOT EXISTS idx_sent_messages_recipient ON sent_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_sent_messages_token     ON sent_messages(tracking_token);
CREATE INDEX IF NOT EXISTS idx_click_events_msg        ON click_events(sent_message_id);
CREATE INDEX IF NOT EXISTS idx_submit_events_msg       ON submit_events(sent_message_id);
CREATE INDEX IF NOT EXISTS idx_training_sessions_msg   ON training_sessions(sent_message_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user          ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created       ON audit_log(created_at);

INSERT OR IGNORE INTO roles (name, description) VALUES
    ('admin',  'Full administrative access'),
    ('viewer', 'Read-only access to reports and audit logs');
