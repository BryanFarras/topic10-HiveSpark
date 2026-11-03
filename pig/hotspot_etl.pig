-- ============================================================================
-- Skrip Pig Latin (Opsional Topic 10) - ETL Dataflow Titik Api Indonesia
-- ============================================================================

hotspot = LOAD '/root/topic10-data/hotspot_1x/hotspot_1x.csv' USING PigStorage(',')
    AS (hotspot_id:int, grid_id:chararray, latitude:double, longitude:double,
        bright_ti4:double, scan:double, track:double, acq_date:chararray,
        acq_time:chararray, satellite:chararray, confidence:chararray,
        bright_ti5:double, frp:double, daynight:chararray);

panas = FILTER hotspot BY (acq_date == '2026-09-19') AND (frp >= 10.0);

per_grid = GROUP panas BY grid_id;

ringkasan = FOREACH per_grid GENERATE
    group AS grid_id,
    COUNT(panas) AS jumlah_hotspot,
    SUM(panas.frp) AS total_frp_mw;

urut = ORDER ringkasan BY total_frp_mw DESC;
top5 = LIMIT urut 5;

DUMP top5;

