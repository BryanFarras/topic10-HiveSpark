# Topic 10 – Layer Processing: Apache Hive, Pig, dan Spark SQL (Kelompok 6)

Tugas kelompok mata kuliah **Teknologi Big Data**: merancang, menguji, dan memilih mesin query lapisan *processing* (**Apache Hive 4.2.1** di atas Tez vs **Apache Spark SQL 4.2.0** di memori) untuk studi kasus **pemantauan titik api (*hotspot*) kebakaran hutan dan lahan di Indonesia** menggunakan dataset satelit **NASA FIRMS VIIRS** (19–25 Sep 2026).

---

## Ringkasan

| Aspek | Keterangan |
|---|---|
| **Kasus** | Pemantauan titik api VIIRS Indonesia – melanjutkan arsitektur storage HBase Topic 9 ke lapisan *processing* |
| **Dataset** | Data Kecil `1x` (**54.516 baris**, ±4,71 MB CSV), Data Diperbesar `10x` (**545.160 baris**, ±47,71 MB CSV), dan Tabel Referensi `ref_grid_provinsi` (**300 sel grid** 1°×1°) |
| **Format Tabel** | 1. Teks (`CSV` External), 2. Kolumnar (`Parquet`), 3. Kolumnar Berpartisi (`PARTITIONED BY (acq_date STRING) STORED AS PARQUET`) |
| **Tiga Query Inti** | `Q1_Agregasi` (GROUP BY confidence & daynight), `Q2_Join` (JOIN tabel titik api dengan 300 sel grid provinsi), `Q3_Partisi` (WHERE `acq_date = '2026-09-19'` & `frp >= 10`) |
| **Lingkungan** | Windows 11 + WSL2 (`Ubuntu-22.04`), Docker `29.1.3` (`apache/hive:4.2.1` + Tez + Beeline), PySpark `4.2.0` + OpenJDK `17.0.20.1`, Apache Pig `0.18.0` |
| **Keputusan Desain** | **Catatan Keputusan Desain (1 halaman penuh)** + **Diagram Arsitektur v0.2** |

---

## Dokumentasi Instalasi & Dataset Terpisah

Sesuai instruksi pengerjaan, panduan instalasi setiap *tools* dan dokumentasi dataset dipisahkan ke dalam berkas Markdown masing-masing:

1. **[`INSTALASI_DOCKER.md`](INSTALASI_DOCKER.md)** — Panduan instalasi, konfigurasi, dan verifikasi **Docker Engine (`29.1.3`)** di WSL2.
2. **[`INSTALASI_HIVE.md`](INSTALASI_HIVE.md)** — Panduan instalasi, konfigurasi kontainer **Apache Hive `4.2.1` (`apache/hive:4.2.1`)**, pembuatan tabel Teks/Parquet/Partisi, serta eksekusi query via Beeline.
3. **[`INSTALASI_SPARK_SQL.md`](INSTALASI_SPARK_SQL.md)** — Panduan instalasi, konfigurasi **Apache Spark SQL (`pyspark 4.2.0` + `pyarrow` + OpenJDK 17)**, serta eksekusi benchmark di memori.
4. **[`INSTALASI_PIG.md`](INSTALASI_PIG.md)** — Panduan instalasi dan penggunaan **Apache Pig `0.18.0`** (opsional pada perkuliahan).
5. **[`DATASET.md`](DATASET.md)** — Dokumentasi lengkap dataset titik api `1x` (54.516 baris), `10x` (545.160 baris), dan tabel referensi wilayah `ref_grid_provinsi` (300 sel grid).

---

## Struktur Repositori

```text
report/                                      Laporan final
  Tugas_Topic10_Processing_Kelompok6.pdf     <- Berkas utama yang dikumpulkan
  Tugas_Topic10_Processing_Kelompok6.docx    Versi Microsoft Word (gambar tertanam)
  Tugas_Topic10_Processing_Kelompok6.md      Versi Markdown laporan
  build.py                                   Skrip pembangun PDF & DOCX otomatis
  shots/                                     Screenshot asli terminal, Web UI, & diagram v0.2
data/                                        Generator & berkas dataset CSV
  generate_dataset.py                        Pembangkit data 1x (54.516), 10x (545.160), dan ref_grid (300)
  hotspot_1x/hotspot_1x.csv                  Dataset titik api Indonesia 1x (54.516 baris)
  hotspot_10x/hotspot_10x.csv                Dataset titik api Indonesia 10x (545.160 baris)
  ref_grid/ref_grid_provinsi.csv             Tabel referensi 300 sel grid -> provinsi & pulau
hive/                                        Skrip SQL & benchmark Apache Hive 4.2.1
  01_create_load.sql                         DDL & pemuatan tabel Teks, Parquet, dan Partisi (1x & 10x)
  02_verify_tables.sql                       Verifikasi daftar tabel, partisi, dan jumlah baris
  03_queries_demo.sql                        Eksekusi 3 query (Agregasi, Join, Partisi)
  benchmark_hive.py                          Pengukuran waktu 3 percobaan & perhitungan median di Hive
  output/                                    Log keluaran mentah & JSON hasil benchmark Hive
spark/                                       Skrip PySpark & benchmark Spark SQL 4.2.0
  benchmark_spark.py                         Pembuatan tabel Parquet/Partisi, eksekusi 3 query, & median 3x
  output/                                    Log keluaran & JSON hasil benchmark Spark SQL
pig/                                         Skrip Pig Latin (opsional)
  hotspot_etl.pig                            Contoh alur ETL bertahap pada data titik api
tools/
  cap.ps1                                    Utilitas tangkapan layar jendela terminal asli (Windows/WSL)
```

---

## Anggota Kelompok 6

| Nama | NPM | Pembagian Tugas |
|---|---|---|
| **Muhammad Bryan Farras** | 2306230975 | Bab 1 (Konteks kasus, peran layer processing, & desain 3 query) dan Bab 4 (Analisis perbandingan waktu, format, partisi, & proyeksi 100x) |
| **Mirza Adi Raffiansyah** | 2306210323 | Bab 2 (Desain tabel Hive/Spark: Teks, Parquet, Partisi tanggal, & tabel referensi provinsi) |
| **Calvin Wirathama Katoroy** | 2306242395 | Bab 3 (Instalasi Docker, Hive 4.2.1, PySpark 4.2.0, hands-on, screenshot, & pengukuran median 3x) |
| **Salim** | 2306204604 | Bab 5 (Satu halaman Catatan Keputusan Desain), Bab 6 (Diagram Arsitektur v0.2), & penyusunan PDF |

