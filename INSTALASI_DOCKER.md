# Panduan Instalasi, Konfigurasi, dan Penggunaan Docker Engine di WSL2

Dokumen ini merangkum langkah-langkah instalasi **Docker Engine (`docker.io` 29.1.3)** di **WSL2 (Ubuntu 22.04 LTS)** untuk menjalankan kontainer **Apache Hive 4.2.1 (`apache/hive:4.2.1`)** pada pengerjaan **Topic 10 – Layer Processing (Kelompok 6)** sebagaimana didokumentasikan dalam laporan [`report/Tugas_Topic10_Processing_Kelompok6.pdf`](report/Tugas_Topic10_Processing_Kelompok6.pdf).

---

## 1. Spesifikasi Lingkungan Docker

| Komponen | Versi / Konfigurasi |
|---|---|
| **Sistem Operasi Host** | Windows 11 + WSL2 (`Ubuntu-22.04`, kernel `5.15.167.4-microsoft-standard-WSL2`) |
| **Init System WSL2** | `systemd` aktif (`/etc/wsl.conf` → `systemd=true`) |
| **Docker Engine** | Docker `29.1.3` (`29.1.3-0ubuntu3~22.04.2`) |
| **Container Runtime** | `containerd` `2.2.1` & `runc` `1.3.4` |
| **Service Systemd** | `docker.service` & `containerd.service` (`enabled` & `active (running)`) |
| **Image Utama Topic 10** | `apache/hive:4.2.1` (membawa JDK 21, Hive 4.2.1, Tez, dan Beeline) |

---

## 2. Mengapa Menggunakan Docker untuk Apache Hive 4.2.1?

Sesuai materi perkuliahan **Topic 10 (Slide 11 & 31)**:
1. **Kebutuhan Versi Java Berbeda**: Apache Hive `4.2.x` mensyaratkan **JDK 21** sebagai versi minimum, sedangkan ekosistem HBase (`2.6.7`) dan Spark (`4.2.0`) di lingkungan host WSL2 menggunakan **OpenJDK 17**.
2. **Isolasi Komponen Server**: Image resmi `apache/hive:4.2.1` sudah membungkus **HiveServer2**, **Embedded Metastore (Derby)**, **Execution Engine Apache Tez**, **Hadoop HDFS client**, dan **OpenJDK 21** di dalam satu kontainer siap pakai tanpa mengganggu konfigurasi Java di host.

---

## 3. Langkah Instalasi Docker dari Awal di WSL2

### A. Pastikan `systemd` Aktif di WSL2
Periksa apakah proses PID 1 di WSL2 adalah `systemd`:
```bash
ps -p 1 -o comm=
```
Jika belum mengembalikan `systemd`, pastikan `/etc/wsl.conf` berisi:
```ini
[boot]
systemd=true
```

### B. Instalasi Paket `docker.io` dan `containerd`
Jalankan perintah berikut di terminal WSL2:
```bash
sudo apt-get update -y
sudo apt-get install -y docker.io
```

### C. Menyalakan dan Mengaktifkan Layanan Docker
```bash
sudo systemctl enable --now containerd
sudo systemctl enable --now docker
```

### D. Menambahkan Pengguna ke Grup `docker` (Opsional Non-Root)
Agar perintah `docker` dapat dijalankan tanpa `sudo`:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## 4. Verifikasi Instalasi Docker

Jalankan perintah berikut untuk memastikan daemon Docker berjalan normal:
```bash
# 1. Cek versi Docker CLI
docker --version

# 2. Cek status service systemd Docker
systemctl status docker --no-pager

# 3. Cek informasi engine, jumlah CPU, dan memori yang terdeteksi Docker
docker info | grep -E "Server Version|OSType|Architecture|CPUs|Total Memory"
```

Contoh keluaran pada lingkungan kami:
```text
Docker version 29.1.3, build 29.1.3-0ubuntu3~22.04.2
 Server Version: 29.1.3
 OSType: linux
 Architecture: x86_64
 CPUs: 22
 Total Memory: 7.456GiB
```

---

## 5. Perintah Dasar Pengelolaan Kontainer Docker untuk Topic 10

```bash
# Mengunduh image resmi Apache Hive 4.2.1 dari Docker Hub
docker pull apache/hive:4.2.1

# Menampilkan daftar image Docker yang tersimpan di lokal
docker images

# Menampilkan kontainer yang sedang berjalan
docker ps

# Menampilkan seluruh kontainer (termasuk yang berhenti)
docker ps -a

# Melihat log inisialisasi kontainer hive4
docker logs hive4 --tail 50

# Menghentikan dan memulai ulang kontainer hive4
docker stop hive4
docker start hive4

# Menghapus kontainer hive4 (jika ingin membuat ulang dari awal)
docker rm -f hive4
```

