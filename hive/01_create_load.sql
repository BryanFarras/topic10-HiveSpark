-- ============================================================================
-- Topic 10 - Pembuatan Database & Pemuatan Tabel Hive (Teks, Parquet, Partisi)
-- Studi Kasus: Pemantauan Titik Api (Hotspot) VIIRS Indonesia (Kelompok 6)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS hotspot_db;
USE hotspot_db;

SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

-- 1. Tabel Referensi Wilayah Spasial (300 Sel Grid 1x1 Derajat -> Provinsi)
DROP TABLE IF EXISTS ref_grid_provinsi;
CREATE EXTERNAL TABLE ref_grid_provinsi (
    grid_id STRING,
    provinsi STRING,
    pulau STRING,
    tingkat_rawan STRING,
    luas_gambut_ha INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/ref_grid';

-- ============================================================================
-- A. DATA KECIL (1x = 54.516 baris, periode 19-25 September 2026)
-- ============================================================================

-- A1. Tabel Format Teks (CSV External)
DROP TABLE IF EXISTS hotspot_1x_text;
CREATE EXTERNAL TABLE hotspot_1x_text (
    hotspot_id INT,
    grid_id STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    bright_ti4 DOUBLE,
    scan DOUBLE,
    track DOUBLE,
    acq_date STRING,
    acq_time STRING,
    satellite STRING,
    confidence STRING,
    bright_ti5 DOUBLE,
    frp DOUBLE,
    daynight STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/hotspot_1x';

-- A2. Tabel Format Parquet (Non-Partisi)
DROP TABLE IF EXISTS hotspot_1x_parquet;
CREATE TABLE hotspot_1x_parquet
STORED AS PARQUET
AS SELECT * FROM hotspot_1x_text;

-- A3. Tabel Format Parquet Berpartisi Tanggal (acq_date)
DROP TABLE IF EXISTS hotspot_1x_part;
CREATE TABLE hotspot_1x_part (
    hotspot_id INT,
    grid_id STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    bright_ti4 DOUBLE,
    scan DOUBLE,
    track DOUBLE,
    acq_time STRING,
    satellite STRING,
    confidence STRING,
    bright_ti5 DOUBLE,
    frp DOUBLE,
    daynight STRING
)
PARTITIONED BY (acq_date STRING)
STORED AS PARQUET;

INSERT OVERWRITE TABLE hotspot_1x_part PARTITION (acq_date)
SELECT hotspot_id, grid_id, latitude, longitude, bright_ti4, scan, track,
       acq_time, satellite, confidence, bright_ti5, frp, daynight, acq_date
FROM hotspot_1x_text;

-- ============================================================================
-- B. DATA DIPERBESAR (10x = 545.160 baris)
-- ============================================================================

-- B1. Tabel Format Teks (CSV External 10x)
DROP TABLE IF EXISTS hotspot_10x_text;
CREATE EXTERNAL TABLE hotspot_10x_text (
    hotspot_id INT,
    grid_id STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    bright_ti4 DOUBLE,
    scan DOUBLE,
    track DOUBLE,
    acq_date STRING,
    acq_time STRING,
    satellite STRING,
    confidence STRING,
    bright_ti5 DOUBLE,
    frp DOUBLE,
    daynight STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/hotspot_10x';

-- B2. Tabel Format Parquet 10x (Non-Partisi)
DROP TABLE IF EXISTS hotspot_10x_parquet;
CREATE TABLE hotspot_10x_parquet
STORED AS PARQUET
AS SELECT * FROM hotspot_10x_text;

-- B3. Tabel Format Parquet Berpartisi Tanggal 10x (acq_date)
DROP TABLE IF EXISTS hotspot_10x_part;
CREATE TABLE hotspot_10x_part (
    hotspot_id INT,
    grid_id STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    bright_ti4 DOUBLE,
    scan DOUBLE,
    track DOUBLE,
    acq_time STRING,
    satellite STRING,
    confidence STRING,
    bright_ti5 DOUBLE,
    frp DOUBLE,
    daynight STRING
)
PARTITIONED BY (acq_date STRING)
STORED AS PARQUET;

INSERT OVERWRITE TABLE hotspot_10x_part PARTITION (acq_date)
SELECT hotspot_id, grid_id, latitude, longitude, bright_ti4, scan, track,
       acq_time, satellite, confidence, bright_ti5, frp, daynight, acq_date
FROM hotspot_10x_text;

