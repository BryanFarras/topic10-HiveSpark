# Panduan Instalasi, Konfigurasi, dan Penggunaan Apache Hive 4.2.1 (Docker)

Dokumen ini menjelaskan langkah-langkah instalasi dan penggunaan **Apache Hive 4.2.1** menggunakan Docker image resmi `apache/hive:4.2.1` pada **WSL2 (Ubuntu 22.04 LTS)** untuk mengerjakan **Topic 10 – Layer Processing (Kelompok 6)** sebagaimana tertulis dalam laporan [`report/Tugas_Topic10_Processing_Kelompok6.pdf`](report/Tugas_Topic10_Processing_Kelompok6.pdf).

---

## 1. Spesifikasi Lingkungan Apache Hive

| Komponen | Versi / Konfigurasi |
|---|---|
| **Image Docker** | `apache/hive:4.2.1` (Rilis resmi Apache Hive, 24 Agustus 2026) |
| **Nama Kontainer** | `hive4` |
| **Execution Engine** | **Apache Tez** (default pada Hive 4.x, menggantikan MapReduce) |
| **Metastore** | Embedded Derby Metastore (`schema-on-read`) |
| **Port JDBC HiveServer2** | `10000` (`jdbc:hive2://localhost:10000`) |
| **Port Web UI HiveServer2** | `10002` (http://localhost:10002) |
| **Volume Mount Data** | `/root/topic10-data:/data` (direktori ext4 WSL2 berisi dataset CSV 1x, 10x, dan referensi) |
| **Klien SQL** | **Beeline** (`docker exec -it hive4 beeline -u jdbc:hive2://localhost:10000`) |

---

## 2. Langkah Instalasi & Menjalankan Kontainer Hive 4.2.1

Pastikan Docker Engine sudah terpasang dan berjalan di WSL2 (lihat [`INSTALASI_DOCKER.md`](INSTALASI_DOCKER.md)).

### A. Mengunduh Image `apache/hive:4.2.1`
```bash
docker pull apache/hive:4.2.1
```

### B. Menyiapkan Direktori Data di WSL2 (`/root/topic10-data`)
Agar pembacaan file oleh user `hive` di dalam kontainer berjalan cepat di atas filesystem native Linux (`ext4`) dan bebas kendala izin akses (*permission*), salin dataset dari repositori ke `/root/topic10-data`:
```bash
mkdir -p /root/topic10-data
cp -r /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/data/hotspot_1x /root/topic10-data/
cp -r /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/data/hotspot_10x /root/topic10-data/
cp -r /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/data/ref_grid /root/topic10-data/
chmod -R 777 /root/topic10-data
```

### C. Menjalankan Kontainer `hive4` (HiveServer2)
```bash
docker rm -f hive4 2>/dev/null || true

docker run -d \
  --name hive4 \
  -p 10000:10000 \
  -p 10002:10002 \
  -e SERVICE_NAME=hiveserver2 \
  -v /root/topic10-data:/data \
  apache/hive:4.2.1
```

### D. Verifikasi Kontainer & Koneksi Beeline
Tunggu ±25–40 detik hingga HiveServer2 selesai menginisialisasi Metastore dan membuka port `10000`. Periksa statusnya dengan:
```bash
# 1. Cek status kontainer dan port yang terbuka
docker ps --filter name=hive4

# 2. Uji koneksi ke HiveServer2 menggunakan Beeline
docker exec hive4 beeline -u jdbc:hive2://localhost:10000 -e "SELECT version();"
```
Antarmuka Web UI HiveServer2 juga dapat diakses melalui browser di:
* **http://localhost:10002**

---

## 3. Memuat Dataset ke Tabel Hive (Teks, Parquet, dan Berpartisi)

Seluruh skrip DDL dan pemuatan data tersedia di [`hive/01_create_load.sql`](hive/01_create_load.sql). Untuk menjalankannya:
```bash
docker cp /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/hive/01_create_load.sql hive4:/tmp/01_create_load.sql
docker exec hive4 beeline -u jdbc:hive2://localhost:10000 -f /tmp/01_create_load.sql
```

Skrip tersebut membuat database `hotspot_db` dan 7 tabel berikut:
1. **`ref_grid_provinsi`** (`EXTERNAL TABLE`, `TEXTFILE`) — 300 baris pemetaan `grid_id` ke provinsi dan pulau di Indonesia.
2. **`hotspot_1x_text`** (`EXTERNAL TABLE`, `TEXTFILE`) — 54.516 baris data titik api Indonesia (1x) berformat CSV.
3. **`hotspot_1x_parquet`** (`MANAGED TABLE`, `PARQUET`) — 54.516 baris data titik api (1x) berformat kolumnar Parquet non-partisi.
4. **`hotspot_1x_part`** (`MANAGED TABLE`, `PARTITIONED BY (acq_date STRING) STORED AS PARQUET`) — 54.516 baris data titik api (1x) berformat Parquet yang dipartisi per tanggal (`2026-09-19` s/d `2026-09-25`, 7 partisi).
5. **`hotspot_10x_text`** (`EXTERNAL TABLE`, `TEXTFILE`) — 545.160 baris data titik api yang diperbesar (10x) berformat CSV.
6. **`hotspot_10x_parquet`** (`MANAGED TABLE`, `PARQUET`) — 545.160 baris data titik api (10x) berformat Parquet non-partisi.
7. **`hotspot_10x_part`** (`MANAGED TABLE`, `PARTITIONED BY (acq_date STRING) STORED AS PARQUET`) — 545.160 baris data titik api (10x) berformat Parquet berpartisi tanggal.

---

## 4. Verifikasi Tabel & Partisi di Hive

Jalankan skrip [`hive/02_verify_tables.sql`](hive/02_verify_tables.sql):
```bash
docker cp /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/hive/02_verify_tables.sql hive4:/tmp/02_verify_tables.sql
docker exec hive4 beeline -u jdbc:hive2://localhost:10000 -f /tmp/02_verify_tables.sql
```

Atau masuk ke Beeline interaktif:
```bash
docker exec -it hive4 beeline -u jdbc:hive2://localhost:10000/hotspot_db
```
Lalu jalankan:
```sql
SHOW TABLES;
SHOW PARTITIONS hotspot_1x_part;
DESCRIBE FORMATTED hotspot_1x_part;
```

---

## 5. Menjalankan 3 Query (Agregasi, Join, Partisi) & Benchmark Median 3 Kali

### A. Menjalankan Demo 3 Query di Hive
```bash
docker cp /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/hive/03_queries_demo.sql hive4:/tmp/03_queries_demo.sql
docker exec hive4 beeline -u jdbc:hive2://localhost:10000 -f /tmp/03_queries_demo.sql
```

### B. Menjalankan Pengukuran Waktu Otomatis (3 Percobaan & Median)
Skrip [`hive/benchmark_hive.py`](hive/benchmark_hive.py) menjalankan ketiga query (`Q1_Agregasi`, `Q2_Join`, `Q3_Partisi`) masing-masing **3 kali** pada tabel **Teks**, **Parquet**, dan **Parquet Partisi** untuk ukuran data **1x (54.516 baris)** dan **10x (545.160 baris)**:
```bash
cd /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig
python3 hive/benchmark_hive.py
```
Hasil pengukuran tersimpan otomatis di:
* [`hive/output/benchmark_hive_summary.txt`](hive/output/benchmark_hive_summary.txt)
* [`hive/output/benchmark_hive.json`](hive/output/benchmark_hive.json)

