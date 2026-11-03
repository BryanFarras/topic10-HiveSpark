# Panduan Instalasi, Konfigurasi, dan Penggunaan Apache Pig 0.18.0 (Opsional)

Dokumen ini menjelaskan langkah-langkah instalasi dan penggunaan **Apache Pig 0.18.0** di **WSL2 (Ubuntu 22.04 LTS)**. Sesuai materi **Topic 10 (Slide 10, 11, 18–20)**, Apache Pig berperan sebagai alat *dataflow* (`Pig Latin`) **opsional** di samping dua mesin SQL inti (**Apache Hive** dan **Spark SQL**).

---

## 1. Spesifikasi Lingkungan Apache Pig

| Komponen | Versi / Lokasi |
|---|---|
| **Sistem Operasi** | Windows 11 + WSL2 (`Ubuntu-22.04`) |
| **Java Runtime (JDK)** | OpenJDK `17.0.20.1` (`/usr/lib/jvm/java-17-openjdk-amd64`) |
| **Apache Pig** | Pig `0.18.0` (`/root/pig-0.18.0`) |
| **Mode Eksekusi** | Local Mode (`pig -x local`) untuk transformasi ETL bertahap |

---

## 2. Langkah Instalasi Apache Pig 0.18.0 di WSL2

### A. Mengunduh dan Mengekstrak Apache Pig 0.18.0
```bash
cd /root
wget https://downloads.apache.org/pig/pig-0.18.0/pig-0.18.0.tar.gz
tar -xzf pig-0.18.0.tar.gz
rm -f pig-0.18.0.tar.gz
```

### B. Menambahkan `PIG_HOME` ke `~/.bashrc`
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PIG_HOME=/root/pig-0.18.0
export PIG_CLASSPATH="/root/hbase-2.6.7-hadoop3/lib/*"
export PATH=$PATH:$PIG_HOME/bin
```
Muat ulang konfigurasi:
```bash
source ~/.bashrc
```

### C. Verifikasi Versi Pig
```bash
pig -version
```
Keluaran:
```text
Apache Pig version 0.18.0
```

---

## 3. Contoh Skrip Dataflow Pig Latin pada Dataset Hotspot (`pig/hotspot_etl.pig`)

Berbeda dengan SQL di Hive dan Spark SQL yang bersifat **deklaratif** (menulis hasil akhir yang diinginkan), Pig Latin meminta pengguna menulis **alur transformasi langkah demi langkah** (*LOAD → FILTER → GROUP → FOREACH GENERATE → STORE*):

```pig
-- Memuat data CSV titik api Indonesia (1x = 54.516 baris)
hotspot = LOAD '/root/topic10-data/hotspot_1x/hotspot_1x.csv' USING PigStorage(',')
    AS (hotspot_id:int, grid_id:chararray, latitude:double, longitude:double,
        bright_ti4:double, scan:double, track:double, acq_date:chararray,
        acq_time:chararray, satellite:chararray, confidence:chararray,
        bright_ti5:double, frp:double, daynight:chararray);

-- Langkah 1: Filter titik api pada tanggal puncak 2026-09-19 dengan FRP >= 10 MW
panas = FILTER hotspot BY (acq_date == '2026-09-19') AND (frp >= 10.0);

-- Langkah 2: Kelompokkan berdasarkan sel grid
per_grid = GROUP panas BY grid_id;

-- Langkah 3: Hitung jumlah titik api dan total FRP per grid
ringkasan = FOREACH per_grid GENERATE
    group AS grid_id,
    COUNT(panas) AS jumlah_hotspot,
    SUM(panas.frp) AS total_frp_mw;

-- Langkah 4: Urutkan dari total FRP tertinggi dan ambil 5 teratas
urut = ORDER ringkasan BY total_frp_mw DESC;
top5 = LIMIT urut 5;

DUMP top5;
```

Cara menjalankan skrip Pig dalam mode lokal:
```bash
PIG_CLASSPATH="/root/hbase-2.6.7-hadoop3/lib/*" JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
  /root/pig-0.18.0/bin/pig -x local /mnt/c/Users/asus/Documents/BigData/Topic10-HivePig/pig/hotspot_etl.pig
```

Keluaran hasil eksekusi (`pig/output/hotspot_etl.out`):
```text
(g087112,255,11306.029999999995)
(g086113,195,8737.439999999995)
(g086111,209,7323.420000000004)
(g087113,106,7308.179999999999)
(g087114,156,6520.979999999999)
2026-11-02 18:06:30,769 INFO [main] org.apache.pig.Main - Pig script completed in 5 seconds and 481 milliseconds (5481 ms)
```

