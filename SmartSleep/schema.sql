-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS temperature;
DROP TABLE IF EXISTS hours_slept;
DROP TABLE IF EXISTS wake_up_hour;
DROP TABLE IF EXISTS waking_mode;
DROP TABLE IF EXISTS start_to_sleep;
DROP TABLE IF EXISTS sounds_recorded;
DROP TABLE IF EXISTS pillow_angle;
DROP TABLE IF EXISTS time_slept;
DROP TABLE IF EXISTS heartrate;

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

CREATE TABLE time_slept(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hours INTEGER NOT NULL,
    minutes INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE wake_up_hour(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TIME,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pillow_angle(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value FLOAT CHECK(value < 90 and value >=0),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE waking_mode(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  value TEXT CHECK( value IN ('L','V','S', 'LVS', 'LV', 'LS', 'VS') )   NOT NULL DEFAULT 'LS', -- L = Lights, V = Vibrations, S = Sounds, rest represent the possible combinations
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE start_to_sleep(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value INTEGER NOT NULL CHECK(value IN (0,1)),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE heartrate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    heartrate INTEGER NOT NULL,
    sleep INTEGER,
    time TEXT,
    FOREIGN KEY(sleep) REFERENCES start_to_sleep(id)
);

CREATE TABLE sounds_recorded(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value REAL NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);