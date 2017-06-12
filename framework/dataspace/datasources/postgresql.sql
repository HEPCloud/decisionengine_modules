DROP TABLE IF EXISTS header;

CREATE TABLE header (
    taskmanager_id TEXT,
    generation_id INTEGER,
    key TEXT,
    create_time BIGINT,
    expiration_time BIGINT,
    scheduled_create_time BIGINT,
    creator TEXT,
    schema_id BIGINT
    );

DROP TABLE IF EXISTS schema;
CREATE TABLE schema (
    schema_id SERIAL,
    schema BYTEA
    );

DROP TABLE IF EXISTS metadata;
CREATE TABLE metadata (
    taskmanager_id TEXT,
    generation_id INTEGER,
    key TEXT,
    state TEXT,
    generation_time BIGINT,
    missed_update_count INTEGER
    );

DROP TABLE IF EXISTS dataproduct;
CREATE TABLE dataproduct (
    taskmanager_id TEXT,
    generation_id INTEGER,
    key TEXT,
    value BYTEA
    );
