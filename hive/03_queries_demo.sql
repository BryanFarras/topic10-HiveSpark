USE hotspot_db;

-- Query 1: Agregasi (Jumlah titik api, total FRP, rata-rata FRP, dan maksimum FRP per tingkat confidence & siang/malam)
SELECT confidence,
       daynight,
       COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw,
       ROUND(AVG(frp), 2) AS rata_frp_mw,
       ROUND(MAX(frp), 2) AS max_frp_mw
FROM hotspot_1x_part
GROUP BY confidence, daynight
ORDER BY total_frp_mw DESC;

-- Query 2: Join (Menggabungkan titik api dengan tabel referensi wilayah grid untuk Top 10 Provinsi Terdampak)
SELECT p.provinsi,
       p.pulau,
       COUNT(h.hotspot_id) AS jumlah_hotspot,
       ROUND(SUM(h.frp), 2) AS total_frp_mw,
       ROUND(AVG(h.frp), 2) AS rata_frp_mw
FROM hotspot_1x_part h
JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id
WHERE h.confidence IN ('nominal', 'high')
GROUP BY p.provinsi, p.pulau
ORDER BY jumlah_hotspot DESC
LIMIT 10;

-- Query 3: Partisi (Filter tanggal puncak kemarau acq_date = '2026-09-19' dan FRP >= 10 MW per sel grid)
SELECT grid_id,
       confidence,
       COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw,
       ROUND(MAX(frp), 2) AS max_frp_mw
FROM hotspot_1x_part
WHERE acq_date = '2026-09-19' AND frp >= 10.0
GROUP BY grid_id, confidence
ORDER BY total_frp_mw DESC
LIMIT 10;

