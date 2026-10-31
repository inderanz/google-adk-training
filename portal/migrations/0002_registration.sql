CREATE TABLE registrations (
  sub TEXT PRIMARY KEY REFERENCES identities(sub),
  agreement_version TEXT NOT NULL,
  accepted_at INTEGER NOT NULL
);
CREATE TABLE pending_registrations (
  token_hash TEXT PRIMARY KEY,
  sub TEXT NOT NULL,
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  csrf TEXT NOT NULL,
  return_to TEXT NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX pending_registration_expiry ON pending_registrations(expires_at);
