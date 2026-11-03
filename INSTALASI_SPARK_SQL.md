# Panduan Instalasi, Konfigurasi, dan Penggunaan Apache Spark SQL (PySpark 4.2.0)

Dokumen ini menjelaskan langkah-langkah instalasi, konfigurasi, dan penggunaan **Apache Spark SQL (`pyspark 4.2.0`)** di **WSL2 (Ubuntu 22.04 LTS)** untuk mengerjakan **Topic 10 – Layer Processing (Kelompok 6)** sebagaimana tertulis dalam laporan [`report/Tugas_Topic10_Processing_Kelompok6.pdf`](report/Tugas_Topic10_Processing_Kelompok6.pdf).

---

## 1. Spesifikasi Lingkungan Spark SQL

| Komponen | Versi / Konfigurasi |
|---|---|
| **Sistem Operasi** | Windows 11 + WSL2 (`Ubuntu-22.04`) |
| **Java Runtime (JDK)** | OpenJDK `17.0.20.1` (`/usr/lib/jvm/java-17-openjdk-amd64`) |
| **Python** | Python `3.10.12` (`/usr/bin/python3`) |
| **PySpark / Spark SQL** | Apache Spark `4.2.0` (`pip install pyspark==4.2.0`) |
| **Pendukung Kolumnar** | `pyarrow` & `pandas` & `numpy` |
| **Mode Eksekusi** | `local[*]` (menggunakan seluruh core CPU di memori, Catalyst Optimizer + Tungsten) |
| **Direktori Tabel Spark** | `/root/topic10-data/spark_tables/` (Parquet non-partisi & Parquet berpartisi `acq_date`) |

---

## 2. Langkah Instalasi PySpark dari Awal di WSL2

### A. Pastikan OpenJDK 17 dan Python 3 Pip Terpasang
```bash
sudo apt-get update -y
sudo apt-get install -y openjdk-17-jdk python3 python3-pip python3-venv
java -version
python3 --version
```

### B. Konfigurasi `JAVA_HOME`
Pastikan variabel `JAVA_HOME` sudah mengarah ke OpenJDK 17 di `~/.bashrc`:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
```
Muat ulang konfigurasi:
```bash
source ~/.bashrc
```

### C. Instalasi `pyspark==4.2.0` dan `pyarrow` via `pip`
Sesuai materi perkuliahan **Topic 10 (Slide 11)**:
```bash
pip3 install --upgrade pip
pip3 install pyspark==4.2.0 pyarrow pandas
```

---

## 3. Verifikasi Instalasi PySpark & Spark SQL

Jalankan perintah satu baris berikut di terminal WSL2 untuk memverifikasi bahwa `SparkSession` dan mesin **Spark SQL** berjalan dengan baik:
```bash
python3 -c "import pyspark; from pyspark.sql import SparkSession; s = SparkSession.builder.master('local[*]').appName('cek').getOrCreate(); print('PySpark Version:', s.version); s.sql('SELECT 1 AS uji_spark_sql').show(); s.stop()"
```

Atau jalankan antarmuka interaktif PySpark:
```bash
pyspark --version
```

---

## 4. Memuat Dataset & Menjalankan 3 Query di Spark SQL

Pada [`spark/benchmark_spark.py`](spark/benchmark_spark.py), dataset kasus proyek (`hotspot_1x.csv` = 54.516 baris dan `hotspot_10x.csv` = 545.160 baris) beserta tabel referensi `ref_grid_provinsi.csv` (300 sel grid) dimuat ke dalam tiga format tampilan tabel (*temporary view*) di Spark SQL yang setara dengan tabel di Hive:
1. **Format Teks (CSV)**: `hotspot_1x_text` dan `hotspot_10x_text` (`spark.read.schema(...).csv(...)`)
2. **Format Parquet Non-Partisi**: `hotspot_1x_parquet` dan `hotspot_10x_parquet` (`spark.read.parquet(...)`)
3. **Format Parquet Berpartisi (`acq_date`)**: `hotspot_1x_part` dan `hotspot_10x_part` (`df.write.partitionBy("acq_date").parquet(...)`)

### Contoh Kode Spark SQL (Setara dengan Query Hive)
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HotspotSparkSQL").master("local[*]").getOrCreate()

# Membaca tabel Parquet berpartisi tanggal
df_part = spark.read.parquet("/root/topic10-data/spark_tables/hotspot_1x_part")
df_part.createOrReplaceTempView("hotspot_1x_part")

# Menjalankan Query 3 (Partisi + Agregasi pada tanggal puncak 2026-09-19)
spark.sql("""
    SELECT grid_id,
           confidence,
           COUNT(*) AS jumlah_hotspot,
           ROUND(SUM(frp), 2) AS total_frp_mw,
           ROUND(MAX(frp), 2) AS max_frp_mw
    FROM hotspot_1x_part
    WHERE acq_date = '2026-09-19' AND frp >= 10.0
    GROUP BY grid_id, confidence
    ORDER BY total_frp_mw DESC
    LIMIT 10
""").show()
```

---

## 5. Menjalankan Benchmark Waktu Spark SQL (3 Percobaan & Median)

Untuk menjalankan pembuatan tabel Parquet/Partisi, mengeksekusi ketiga query (`Q1_Agregasi`, `Q2_Join`, `Q3_Partisi`), dan mencatat waktu median dari 3 kali percobaan pada data **1x** dan **10x**:
```bash
cd /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig
python3 spark/benchmark_spark.py
```

Hasil keluaran dan tabel ringkasan waktu tersimpan otomatis di:
* [`spark/output/spark_queries_demo.txt`](spark/output/spark_queries_demo.txt) — hasil tabel keluaran ketiga query di Spark SQL (identik dengan hasil di Hive).
* [`spark/output/benchmark_spark_summary.txt`](spark/output/benchmark_spark_summary.txt) — tabel waktu Run 1, Run 2, Run 3, dan Median (detik).
* [`spark/output/benchmark_spark.json`](spark/output/benchmark_spark.json) — data JSON hasil pengukuran.

