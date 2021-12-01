-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS temperature;
DROP TABLE IF EXISTS snoring;
DROP TABLE IF EXISTS hours_slept;
DROP TABLE IF EXISTS wake_up_hour;
DROP TABLE IF EXISTS waking_mode;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE temperature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value REAL NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE snoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value INTEGER NOT NULL, -- True or false
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hours_slept(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE wake_up_hour(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TIME,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE waking_mode(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  value TEXT CHECK( value IN ('L','V','S', 'LVS', 'LV', 'LS', 'VS') )   NOT NULL, -- L = Lights, V = Vibrations, S = Sounds, rest represent the possible combinations
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
