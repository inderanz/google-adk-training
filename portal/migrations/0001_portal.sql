PRAGMA foreign_keys = ON;
CREATE TABLE approvals (
  email TEXT PRIMARY KEY,
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
  google_sub TEXT UNIQUE,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE TABLE identities (
  sub TEXT PRIMARY KEY,
  email TEXT NOT NULL,
  name TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);
CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  sub TEXT NOT NULL REFERENCES identities(sub),
  email TEXT NOT NULL,
  csrf TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX sessions_sub ON sessions(sub);
CREATE INDEX sessions_expiry ON sessions(expires_at);
CREATE TABLE oauth_attempts (
  state_hash TEXT PRIMARY KEY,
  verifier TEXT NOT NULL,
  nonce TEXT NOT NULL,
  return_to TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX oauth_expiry ON oauth_attempts(expires_at);
CREATE TABLE releases (
  module_id TEXT PRIMARY KEY,
  lessons INTEGER NOT NULL DEFAULT 0 CHECK (lessons IN (0,1)),
  solutions INTEGER NOT NULL DEFAULT 0 CHECK (solutions IN (0,1)),
  updated_at INTEGER NOT NULL,
  CHECK (solutions = 0 OR lessons = 1)
);
CREATE TABLE visits (
  id TEXT PRIMARY KEY,
  sub TEXT NOT NULL REFERENCES identities(sub),
  page TEXT NOT NULL,
  started_at INTEGER NOT NULL,
  last_at INTEGER NOT NULL,
  active_ms INTEGER NOT NULL DEFAULT 0,
  sequence INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX visits_user_time ON visits(sub, started_at);
CREATE INDEX visits_time ON visits(started_at);
CREATE TABLE audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX audit_time ON audit(created_at);
