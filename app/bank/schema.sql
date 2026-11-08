CREATE TABLE IF NOT EXISTS customers (
  id            INTEGER PRIMARY KEY,
  full_name     TEXT NOT NULL,
  phone         TEXT NOT NULL UNIQUE,
  birth_date    TEXT NOT NULL,                 -- 'YYYY-MM-DD'; LLM'e asla gönderilmez
  district      TEXT NOT NULL,
  address_type  TEXT NOT NULL CHECK (address_type IN ('home','work'))
);

CREATE TABLE IF NOT EXISTS delivery_slots (
  id          INTEGER PRIMARY KEY,
  district    TEXT NOT NULL,
  slot_date   TEXT NOT NULL,
  start_time  TEXT NOT NULL,
  end_time    TEXT NOT NULL,
  capacity    INTEGER NOT NULL CHECK (capacity > 0),
  booked      INTEGER NOT NULL DEFAULT 0,
  CHECK (booked BETWEEN 0 AND capacity),       -- fazla rezervasyon DB seviyesinde imkânsız
  UNIQUE (district, slot_date, start_time)
);

CREATE TABLE IF NOT EXISTS calls (
  id                    TEXT PRIMARY KEY,
  customer_id           INTEGER NOT NULL REFERENCES customers(id),
  started_at            TEXT NOT NULL,
  ended_at              TEXT,
  verification_attempts INTEGER NOT NULL DEFAULT 0,
  verified_at           TEXT,
  outcome               TEXT CHECK (outcome IN
    ('scheduled','waitlisted','escalated','verification_failed','not_reached','declined')),
  summary               TEXT
);

CREATE TABLE IF NOT EXISTS appointments (
  id           INTEGER PRIMARY KEY,
  customer_id  INTEGER NOT NULL REFERENCES customers(id),
  slot_id      INTEGER NOT NULL REFERENCES delivery_slots(id),
  call_id      TEXT REFERENCES calls(id),
  status       TEXT NOT NULL CHECK (status IN ('confirmed','cancelled','delivered')),
  source       TEXT NOT NULL CHECK (source IN ('call','waitlist_promotion')),
  created_at   TEXT NOT NULL,
  cancelled_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_appointment
  ON appointments(customer_id) WHERE status = 'confirmed';

CREATE TABLE IF NOT EXISTS waitlist_entries (
  id                 INTEGER PRIMARY KEY,
  customer_id        INTEGER NOT NULL REFERENCES customers(id),
  call_id            TEXT REFERENCES calls(id),
  accepted_slot_ids  TEXT NOT NULL,            -- JSON dizi; prod'da ayrı join tablosu
  next_week_priority INTEGER NOT NULL DEFAULT 1,
  status             TEXT NOT NULL CHECK (status IN ('waiting','promoted','cancelled')),
  created_at         TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_waitlist
  ON waitlist_entries(customer_id) WHERE status = 'waiting';

CREATE TABLE IF NOT EXISTS escalations (
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  call_id     TEXT REFERENCES calls(id),
  reason      TEXT NOT NULL CHECK (reason IN ('capacity_request','address_change',
                'third_party','verification_failed','customer_request','other')),
  note        TEXT,
  status      TEXT NOT NULL DEFAULT 'open',
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS call_events (
  id       INTEGER PRIMARY KEY,
  call_id  TEXT NOT NULL REFERENCES calls(id),
  ts       TEXT NOT NULL,
  kind     TEXT NOT NULL CHECK (kind IN ('user','assistant','tool','system')),
  payload  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (    -- SMS mock (outbox)
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  body        TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  sent_at     TEXT
);
