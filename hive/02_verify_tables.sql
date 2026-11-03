USE hotspot_db;
SHOW TABLES;
SHOW PARTITIONS hotspot_1x_part;
SELECT '1x_text' AS tabel, COUNT(*) AS jumlah_baris FROM hotspot_1x_text
UNION ALL
SELECT '1x_parquet' AS tabel, COUNT(*) AS jumlah_baris FROM hotspot_1x_parquet
UNION ALL
SELECT '1x_part' AS tabel, COUNT(*) AS jumlah_baris FROM hotspot_1x_part
UNION ALL
SELECT '10x_part' AS tabel, COUNT(*) AS jumlah_baris FROM hotspot_10x_part;

