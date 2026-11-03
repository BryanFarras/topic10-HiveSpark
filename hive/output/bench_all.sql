USE hotspot_db;
-- Warm-up
SELECT COUNT(*) FROM hotspot_1x_part;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Teks (CSV)|hotspot_1x_text|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet|hotspot_1x_parquet|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_1x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|1x|Parquet Partisi|hotspot_1x_part|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_1x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_text h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Teks (CSV)|hotspot_10x_text|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_text WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_parquet h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet|hotspot_10x_parquet|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_parquet WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q1_Agregasi|run1
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q1_Agregasi|run2
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q1_Agregasi|run3
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,        ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q2_Join|run1
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q2_Join|run2
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q2_Join|run3
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,        ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw FROM hotspot_10x_part h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal', 'high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q3_Partisi|run1
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q3_Partisi|run2
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
-- MARKER|10x|Parquet Partisi|hotspot_10x_part|Q3_Partisi|run3
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,        ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw FROM hotspot_10x_part WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;
