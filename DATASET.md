# Dokumentasi Dataset — Pemantauan Titik Api (Hotspot) Indonesia (Topic 10)

Dokumen ini menjelaskan seluruh dataset yang digunakan pada pengerjaan **Topic 10 – Layer Processing: Hive, Pig, dan Spark SQL (Kelompok 6)** sebagaimana dirujuk dalam laporan [`report/Tugas_Topic10_Processing_Kelompok6.pdf`](report/Tugas_Topic10_Processing_Kelompok6.pdf). Dataset ini melanjutkan studi kasus kelompok pada **Topic 9 (Apache HBase)** menggunakan data deteksi satelit **NASA FIRMS VIIRS 375m Collection 2**.

---

## 1. Ringkasan Dataset yang Digunakan pada Topic 10

Sesuai ketentuan tugas Topic 10 (*pengukuran pada data kecil dan data yang diperbesar, serta pengujian query agregasi, join, dan partisi*), dataset dibagi menjadi tiga bagian di dalam folder [`data/`](data/):

| Dataset | Lokasi File | Jumlah Baris | Ukuran CSV | Peran pada Pengujian |
|---|---|---|---|---|
| **Data Kecil (`1x`)** | [`data/hotspot_1x/hotspot_1x.csv`](data/hotspot_1x/hotspot_1x.csv) | **54.516 baris** | ±4,71 MB | Seluruh titik api wilayah Indonesia selama 7 hari (19–25 Sep 2026), selaras persis dengan statistik Bab 1 Topic 9. |
| **Data Diperbesar (`10x`)** | [`data/hotspot_10x/hotspot_10x.csv`](data/hotspot_10x/hotspot_10x.csv) | **545.160 baris** | ±47,71 MB | Replikasi terukur 10× lipat dari data `1x` (ID unik `1..954516` dan variasi FRP) untuk menguji skalabilitas mesin query di luar waktu *start-up*. |
| **Tabel Referensi Wilayah** | [`data/ref_grid/ref_grid_provinsi.csv`](data/ref_grid/ref_grid_provinsi.csv) | **300 baris** | ±10 KB | Tabel dimensi spasial yang memetakan 300 kode sel grid 1°×1° (`grid_id`) ke nama **Provinsi**, **Pulau**, **Tingkat Rawan**, dan **Luas Gambut (Ha)** untuk pengujian `JOIN`. |

---

## 2. Skema Kolom Tabel Fakta Titik Api (`hotspot_1x` & `hotspot_10x`)

Setiap baris pada `hotspot_1x.csv` dan `hotspot_10x.csv` memiliki **14 kolom** (tanpa baris header agar langsung terbaca bersih oleh `EXTERNAL TABLE` Hive maupun pembaca CSV Spark SQL):

| No | Nama Kolom | Tipe Data (Hive / Spark) | Penjelasan |
|---|---|---|---|
| 1 | `hotspot_id` | `INT` | Nomor urut unik titik api (`1..54516` pada data `1x`). |
| 2 | `grid_id` | `STRING` | Kode sel grid 1°×1° (`g` + `floor(lat)+90` 3 digit + `floor(lon)` 3 digit, contoh `g087112`). Menjadi kunci penghubung (`JOIN key`) ke tabel `ref_grid_provinsi` dan selaras dengan awalan *row key* HBase pada Topic 9. |
| 3 | `latitude` | `DOUBLE` | Garis lintang titik api (derajat desimal, kotak Indonesia `-11..6`). |
| 4 | `longitude` | `DOUBLE` | Garis bujur titik api (derajat desimal, kotak Indonesia `95..141`). |
| 5 | `bright_ti4` | `DOUBLE` | Suhu kecerahan (*brightness temperature*) kanal I4 dalam Kelvin. |
| 6 | `scan` | `DOUBLE` | Ukuran piksel arah *along-scan* (km). |
| 7 | `track` | `DOUBLE` | Ukuran piksel arah *along-track* (km). |
| 8 | `acq_date` | `STRING` | Tanggal deteksi (`YYYY-MM-DD`, rentang `2026-09-19` s/d `2026-09-25`). Digunakan sebagai **kolom partisi (`PARTITIONED BY (acq_date STRING)`)** pada tabel berpartisi. |
| 9 | `acq_time` | `STRING` | Waktu deteksi UTC (`HHMM`, contoh `0533`). |
| 10 | `satellite` | `STRING` | Kode satelit pengamat (`N` = Suomi-NPP VIIRS). |
| 11 | `confidence` | `STRING` | Tingkat keyakinan deteksi (`low`, `nominal`, `high`). |
| 12 | `bright_ti5` | `DOUBLE` | Suhu kecerahan kanal I5 dalam Kelvin. |
| 13 | `frp` | `DOUBLE` | *Fire Radiative Power* / daya radiasi panas api dalam Megawatt (MW). |
| 14 | `daynight` | `STRING` | Indikator pengamatan siang (`D`) atau malam (`N`). |

### Statistik Data `1x` (54.516 Baris — Konsisten dengan Topic 9)
* **Distribusi per Tanggal (`acq_date` — 7 Partisi)**:
  * `2026-09-19`: **10.974 baris** *(puncak kemarau — diuji pada Query 3 Partisi)*
  * `2026-09-20`: **10.312 baris**
  * `2026-09-21`: **6.920 baris**
  * `2026-09-22`: **7.548 baris**
  * `2026-09-23`: **6.686 baris**
  * `2026-09-24`: **6.390 baris**
  * `2026-09-25`: **5.686 baris** *(titik terendah dalam 7 hari)*
* **Distribusi Tingkat Keyakinan (`confidence`)**:
  * `nominal`: **50.095 baris** (91,89%)
  * `low`: **2.331 baris** (4,28%)
  * `high`: **2.090 baris** (3,83%)
* **Sel Grid Terpadat**:
  * `g087112` (Kalimantan Tengah, `lat -3..-2`, `lon 112..113`): **5.107 baris** (9,37% dari seluruh titik api Indonesia).

---

## 3. Skema Tabel Referensi Wilayah (`ref_grid_provinsi.csv`)

Tabel ini memetakan seluruh **300 sel grid** (`grid_id`) yang muncul pada data titik api ke informasi administratif provinsi di Indonesia untuk menjawab **Pertanyaan Data 5** (*jumlah titik api dan total FRP per provinsi*):

| No | Nama Kolom | Tipe Data | Contoh Nilai | Penjelasan |
|---|---|---|---|---|
| 1 | `grid_id` | `STRING` | `g087112` | Kode unik sel grid 1°×1° (Primary Key). |
| 2 | `provinsi` | `STRING` | `Kalimantan Tengah` | Nama provinsi tempat sel grid berada. |
| 3 | `pulau` | `STRING` | `Kalimantan` | Gugus pulau utama (`Kalimantan`, `Sumatera`, `Papua`, `Sulawesi`, `Jawa`, `Nusa Tenggara`, `Maluku`). |
| 4 | `tingkat_rawan` | `STRING` | `Sangat Tinggi` | Kategori kerawanan karhutla (`Sangat Tinggi`, `Tinggi`, `Sedang`, `Rendah`). |
| 5 | `luas_gambut_ha` | `INT` | `54200` | Estimasi luas lahan gambut pada sel grid tersebut (hektare). |

---

## 4. Tiga Varian Format Tabel yang Dibandingkan

Baik pada ukuran **1x (54.516 baris)** maupun **10x (545.160 baris)**, data dimuat ke dalam tiga varian tabel di **Apache Hive** dan **Apache Spark SQL**:

1. **Tabel Teks (`hotspot_1x_text` & `hotspot_10x_text`)**:
   * Disimpan sebagai berkas teks CSV (`STORED AS TEXTFILE`).
   * Setiap query harus membaca seluruh baris dan seluruh 14 kolom dari awal hingga akhir, lalu mengurai (*parse*) teks menjadi angka `DOUBLE`/`INT` saat query berjalan.
2. **Tabel Parquet Non-Partisi (`hotspot_1x_parquet` & `hotspot_10x_parquet`)**:
   * Disimpan dalam format kolumnar biner **Apache Parquet** (`STORED AS PARQUET`).
   * Menyimpan skema tipe data dan statistik (`min`/`max`/`count`) per *row group*, serta menerapkan kompresi kolumnar. Query hanya membaca kolom yang disebut dalam `SELECT`/`WHERE`/`GROUP BY` (*column projection*).
3. **Tabel Parquet Berpartisi Tanggal (`hotspot_1x_part` & `hotspot_10x_part`)**:
   * Disimpan dalam format **Parquet** dan dipecah ke dalam sub-folder per nilai `acq_date` (`PARTITIONED BY (acq_date STRING) STORED AS PARQUET`), menghasilkan 7 direktori partisi (`acq_date=2026-09-19` s/d `acq_date=2026-09-25`).
   * Saat menjalankan query dengan filter `WHERE acq_date = '2026-09-19'`, mesin query melakukan **Partition Pruning** (hanya membaca 1 folder partisi yang relevan dan melewati 6 folder lainnya).

---

## 5. Cara Membangkitkan Ulang Dataset

Jika ingin membangkitkan ulang berkas CSV `1x`, `10x`, dan `ref_grid_provinsi.csv` dari data sumber `load10k.rb` Topic 9:
```bash
python data/generate_dataset.py
```

