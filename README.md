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

## Langkah-Langkah Menjalankan Semua Tools (Lengkap dari Awal sampai Akhir)

Seluruh *tools* lapisan *processing* dipasang dan dijalankan di dalam **WSL2 (`Ubuntu-22.04`)**, sedangkan pembangkitan laporan PDF/DOCX dijalankan di **Windows PowerShell**.

### Tahap 0: Masuk ke Terminal WSL2 (`Ubuntu-22.04`)

Buka **Windows PowerShell** atau **Command Prompt**, lalu masuk ke distribusi Linux WSL2:

```powershell
wsl -d Ubuntu-22.04 -u root
```

Setelah masuk ke prompt Linux (`root@...:~#`), pindah ke direktori proyek:

```bash
cd /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig
```

---

### Tahap 1: Menyiapkan Dataset (`1x`, `10x`, dan `ref_grid_provinsi`)

1. **Bangkitkan berkas CSV dataset** (jika belum ada atau ingin membuat ulang):
   ```bash
   python3 data/generate_dataset.py
   ```
   Perintah ini menghasilkan:
   - `data/hotspot_1x/hotspot_1x.csv` (`54.516` baris, ±4,71 MB)
   - `data/hotspot_10x/hotspot_10x.csv` (`545.160` baris, ±47,71 MB)
   - `data/ref_grid/ref_grid_provinsi.csv` (`300` baris referensi sel grid provinsi)

2. **Salin dataset ke filesystem native Linux (`/root/topic10-data`)** agar dapat diakses bersama (*shared mount*) oleh kontainer Docker Hive dan PySpark dengan kecepatan I/O maksimal:
   ```bash
   mkdir -p /root/topic10-data/hotspot_1x /root/topic10-data/hotspot_10x /root/topic10-data/ref_grid
   cp -f data/hotspot_1x/hotspot_1x.csv /root/topic10-data/hotspot_1x/
   cp -f data/hotspot_10x/hotspot_10x.csv /root/topic10-data/hotspot_10x/
   cp -f data/ref_grid/ref_grid_provinsi.csv /root/topic10-data/ref_grid/
   chmod -R 777 /root/topic10-data
   ```

---

### Tahap 2: Menjalankan Docker Engine (`29.1.3`)

1. **Pastikan layanan `docker` dan `containerd` aktif**:
   ```bash
   systemctl start containerd docker
   systemctl status docker --no-pager
   ```
2. **Cek versi Docker dan daftar kontainer yang berjalan**:
   ```bash
   docker --version
   docker ps -a
   ```

---

### Tahap 3: Menjalankan Apache Hive (`4.2.1` + Engine Apache Tez via Docker)

#### A. Menyalakan Kontainer `hive4`
- **Jika kontainer `hive4` sudah pernah dibuat** (cukup nyalakan kembali):
  ```bash
  docker start hive4
  docker ps --filter name=hive4
  ```
- **Jika kontainer `hive4` belum ada** (buat kontainer baru dengan port `10000` untuk Beeline JDBC, port `10002` untuk Web UI, dan *mount* `/root/topic10-data` ke `/data`):
  ```bash
  docker run -d --name hive4 \
    -p 10000:10000 -p 10002:10002 \
    -e SERVICE_NAME=hiveserver2 \
    -v /root/topic10-data:/data \
    apache/hive:4.2.1
  ```
  *(Tunggu ±25–30 detik hingga HiveServer2 selesai menginisialisasi Metastore)*:
  ```bash
  docker logs --tail 25 hive4
  ```

#### B. Membuka Web UI HiveServer2
Buka browser di Windows dan kunjungi:
- **URL Web UI HiveServer2**: `http://localhost:10002`

#### C. Masuk ke Shell Interaktif Beeline (Ketik SQL Manual)
Untuk masuk ke antarmuka SQL interaktif **Beeline**:
```bash
docker exec -it hive4 beeline -u jdbc:hive2://localhost:10000
```
Di dalam prompt `0: jdbc:hive2://localhost:10000>`, Anda dapat menjalankan perintah SQL seperti:
```sql
SHOW DATABASES;
USE hotspot_db;
SHOW TABLES;
SHOW PARTITIONS hotspot_1x_part;
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp), 2) AS total_frp_mw
FROM hotspot_1x_part
GROUP BY confidence, daynight
ORDER BY total_frp_mw DESC;
!quit
```

#### D. Menjalankan Seluruh Skrip SQL & Benchmark Hive (Otomatis)
Untuk membuat seluruh 7 tabel (`ref_grid_provinsi`, `hotspot_1x_text`, `hotspot_1x_parquet`, `hotspot_1x_part`, `hotspot_10x_text`, `hotspot_10x_parquet`, `hotspot_10x_part`), memverifikasi isi tabel, menjalankan 3 query (`Q1_Agregasi`, `Q2_Join`, `Q3_Partisi`), dan mengukur waktu **median 3 kali percobaan**:

```bash
# 1. Jalankan pembuatan tabel, verifikasi partisi, dan demo 3 query Hive
bash hive/run_all_hive.sh

# 2. Jalankan benchmark waktu eksekusi Hive (1x warm-up + 3x percobaan per tabel & query)
python3 hive/benchmark_hive.py

# 3. Lihat ringkasan tabel hasil benchmark Hive
cat hive/output/benchmark_hive_summary.txt
```

---

### Tahap 4: Menjalankan Apache Spark SQL (`PySpark 4.2.0`)

#### A. Cek Versi Java & PySpark
```bash
java -version
pyspark --version
```

#### B. Menjalankan Shell Interaktif `pyspark` (Mode Eksplorasi)
Jika ingin mencoba query Spark SQL secara interaktif:
```bash
pyspark --master "local[*]"
```
Contoh perintah di dalam shell Python PySpark:
```python
df = spark.read.parquet("/root/topic10-data/spark_warehouse/hotspot_1x_part")
df.createOrReplaceTempView("hotspot_1x_part")
spark.sql("""
    SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp), 2) AS total_frp_mw
    FROM hotspot_1x_part
    WHERE acq_date = '2026-09-19' AND frp >= 10.0
    GROUP BY grid_id, confidence
    ORDER BY total_frp_mw DESC
    LIMIT 10
""").show(truncate=False)
exit()
```

#### C. Menjalankan Skrip Demo 3 Query & Benchmark Spark SQL (Otomatis)
Skrip `spark/benchmark_spark.py` secara otomatis menulis tabel Parquet & Parquet Berpartisi (`acq_date`), mendaftarkan *temporary view* untuk format Teks (CSV), Parquet, dan Parquet Partisi pada skala `1x` & `10x`, serta menghitung median dari 3 kali percobaan:

```bash
# 1. Tampilkan hasil keluaran 3 query (Q1_Agregasi, Q2_Join, Q3_Partisi) di Spark SQL
python3 spark/benchmark_spark.py --demo

# 2. Jalankan benchmark lengkap Spark SQL (3 percobaan x 3 query x 3 format x 2 skala data)
python3 spark/benchmark_spark.py

# 3. Lihat tabel ringkasan waktu eksekusi Spark SQL
cat spark/output/benchmark_spark_summary.txt
```

---

### Tahap 5: Menjalankan Apache Pig (`0.18.0` — Pelengkap Materi Kuliah)

1. **Cek versi Apache Pig**:
   ```bash
   /root/pig-0.18.0/bin/pig -version
   ```
2. **Masuk ke shell interaktif Grunt (`pig -x local`)**:
   ```bash
   JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
   PIG_CLASSPATH="/root/hbase-2.6.7-hadoop3/lib/*" \
   /root/pig-0.18.0/bin/pig -x local
   ```
   *(Ketik `quit;` untuk keluar dari prompt `grunt>`)*.
3. **Menjalankan skrip ETL Pig Latin (`pig/hotspot_etl.pig`) pada dataset titik api**:
   ```bash
   JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
   PIG_CLASSPATH="/root/hbase-2.6.7-hadoop3/lib/*" \
   /root/pig-0.18.0/bin/pig -x local -f pig/hotspot_etl.pig
   ```

---

### Tahap 6: Membangun Ulang Screenshot & Laporan PDF/DOCX (di Windows PowerShell)

Jika Anda mengubah hasil benchmark atau kode laporan dan ingin membangun ulang *screenshot* terminal beserta laporan `.pdf` dan `.docx`, jalankan perintah berikut di **Windows PowerShell** pada folder proyek:

```powershell
cd C:\Users\asus\Documents\BigData\Topic10-HivePig

# 1. Format log output dan render screenshot terminal (report/shots/01..07.png)
python tools/format_outputs.py
python tools/render_shots.py

# 2. Bangun laporan PDF, laporan DOCX, dan Diagram Arsitektur v0.2 (08_diagram_v02.png)
python report/build.py
```

---

## Anggota Kelompok 6

| Nama | NPM | Pembagian Tugas |
|---|---|---|
| **Muhammad Bryan Farras** | 2306230975 | Bab 1 (Konteks kasus, peran layer processing, & desain 3 query) dan Bab 4 (Analisis perbandingan waktu, format, partisi, & proyeksi 100x) |
| **Mirza Adi Raffiansyah** | 2306210323 | Bab 2 (Desain tabel Hive/Spark: Teks, Parquet, Partisi tanggal, & tabel referensi provinsi) |
| **Calvin Wirathama Katoroy** | 2306242395 | Bab 3 (Instalasi Docker, Hive 4.2.1, PySpark 4.2.0, hands-on, screenshot, & pengukuran median 3x) |
| **Salim** | 2306204604 | Bab 5 (Satu halaman Catatan Keputusan Desain), Bab 6 (Diagram Arsitektur v0.2), & penyusunan PDF |

