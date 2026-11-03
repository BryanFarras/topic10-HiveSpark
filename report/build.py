from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    KeepTogether, PageBreak, Flowable
)
from PIL import Image as PI, ImageDraw, ImageFont
import os
import math

D = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(D, "shots")
os.makedirs(S, exist_ok=True)

NAVY = colors.HexColor("#12394d")
LIGHT = colors.HexColor("#e9f1f4")

base = ParagraphStyle("b", fontName="Helvetica", fontSize=8.3, leading=10.6, spaceAfter=2.5)
small = ParagraphStyle("s", parent=base, fontSize=7.5, leading=9.4)
cap = ParagraphStyle("c", parent=base, fontSize=7.4, leading=9.3, textColor=colors.HexColor("#333333"), spaceAfter=3)
cell = ParagraphStyle("cell", parent=base, fontSize=7.4, leading=9.1, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
cellh = ParagraphStyle("cellh", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
h1 = ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=11.2, leading=13.8, textColor=NAVY, spaceBefore=3, spaceAfter=2.5)
h2 = ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=9.3, leading=11.5, textColor=NAVY, spaceBefore=3, spaceAfter=2)
title = ParagraphStyle("t", parent=base, fontName="Helvetica-Bold", fontSize=14.0, leading=16.8, textColor=NAVY, spaceAfter=1.5)

P = lambda t, s=base: Paragraph(t, s)


def table(rows, widths, header=True, bold_first=False):
    data = []
    for i, r in enumerate(rows):
        st = cellh if (header and i == 0) else cell
        data.append([
            Paragraph(str(c), cellb if (bold_first and j == 0 and i > 0) else st)
            for j, c in enumerate(r)
        ])
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    sty = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c7ce")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
    ]
    if header:
        sty.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1, len(rows), 2):
        sty.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(sty))
    return t


def shot(name, width_cm, caption, crop=None):
    p = os.path.join(S, name)
    if crop:
        im = PI.open(p).crop(crop)
        p = os.path.join(S, "crop_" + name)
        im.save(p)
    w, h = PI.open(p).size
    img = Image(p, width=width_cm * cm, height=width_cm * cm * h / w)
    img.hAlign = "LEFT"
    return KeepTogether([img, P(caption, cap)])


def shot_pair(name1, cap1, name2, cap2, width_cm=8.8):
    p1 = os.path.join(S, name1)
    p2 = os.path.join(S, name2)
    w1, h1_ = PI.open(p1).size
    w2, h2_ = PI.open(p2).size
    img1 = Image(p1, width=width_cm * cm, height=width_cm * cm * h1_ / w1)
    img2 = Image(p2, width=width_cm * cm, height=width_cm * cm * h2_ / w2)
    t = Table(
        [[img1, img2], [P(cap1, cap), P(cap2, cap)]],
        colWidths=[(width_cm + 0.2) * cm, (width_cm + 0.2) * cm],
    )
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return KeepTogether([t])


class DiagramV02(Flowable):
    W, H = 18.0 * cm, 6.9 * cm

    def wrap(self, *a):
        return self.W, self.H

    def box(self, c, x, y, w, h, text, fill=None, dash=False, bold_first=True):
        c.saveState()
        if dash:
            c.setDash(3, 2)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.1)
        if fill:
            c.setFillColor(fill)
        c.roundRect(x, y, w, h, 4, stroke=1, fill=1 if fill else 0)
        c.setFillColor(colors.black)
        lines = text.split("\n")
        ty = y + h / 2 + (len(lines) - 1) * 4.0 - 2.2
        for i, l in enumerate(lines):
            c.setFont("Helvetica-Bold" if (bold_first and i == 0) else "Helvetica", 6.6 if i > 0 else 7.1)
            c.drawCentredString(x + w / 2, ty - i * 8.0, l)
        c.restoreState()

    def arrow(self, c, x1, y1, x2, y2, label="", dash=False, lx=0, ly=2):
        c.saveState()
        c.setStrokeColor(NAVY)
        c.setFillColor(NAVY)
        if dash:
            c.setDash(3, 2)
        c.line(x1, y1, x2, y2)
        c.setDash()
        ang = math.atan2(y2 - y1, x2 - x1)
        p = c.beginPath()
        p.moveTo(x2, y2)
        for da in (math.pi - 0.45, math.pi + 0.45):
            p.lineTo(x2 + 5.5 * math.cos(ang + da), y2 + 5.5 * math.sin(ang + da))
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        if label:
            c.setFont("Helvetica-Oblique", 6.3)
            c.setFillColor(colors.black)
            lines = label.split("\n")
            for i, l in enumerate(lines):
                c.drawCentredString((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly + (len(lines) - 1 - i) * 6.8, l)
        c.restoreState()

    def draw(self):
        c = self.canv
        cm_ = cm
        # 1. Sumber Data (Solid)
        self.box(
            c, 0.0 * cm_, 2.1 * cm_, 2.9 * cm_, 2.5 * cm_,
            "1. SUMBER DATA\nNASA FIRMS VIIRS\nsea_fires_7d.csv (1x & 10x)\n+ ref_grid_provinsi.csv\n(300 sel grid 1°x1°)",
            fill=colors.HexColor("#fff3d6"),
        )
        # 2. Ingestion (Dashed - Topic 11)
        self.box(
            c, 3.5 * cm_, 2.4 * cm_, 2.1 * cm_, 1.9 * cm_,
            "2. INGESTION\nApache Kafka /\nNiFi (Topic 11)\nbelum ada",
            dash=True, bold_first=True,
        )
        # 3A. Storage Operasional HBase (Solid - Topic 9)
        self.box(
            c, 6.4 * cm_, 3.9 * cm_, 4.1 * cm_, 2.4 * cm_,
            "3A. STORAGE OPERASIONAL\nApache HBase 2.6.7 (Topic 9)\nTabel: hotspot (CF loc, sensor)\nrow key: grid#tgl-terbalik#jam#id\nLookup & scan sel < 1 detik",
            fill=colors.HexColor("#d9ecf2"),
        )
        # 3B. Storage Analitik / Data Lake Parquet Berpartisi (Solid - Topic 10)
        self.box(
            c, 6.4 * cm_, 0.8 * cm_, 4.1 * cm_, 2.4 * cm_,
            "3B. STORAGE ANALITIK (BARU)\nWarehouse / HDFS (/data)\nTabel: hotspot_part (Parquet)\nPARTITIONED BY (acq_date)\n+ ref_grid_provinsi (300 grid)",
            fill=colors.HexColor("#d9ecf2"),
        )
        # 4. Layer Processing (Solid - Topic 10 Highlight, height 4.6cm so top route is clear)
        self.box(
            c, 11.4 * cm_, 0.8 * cm_, 3.7 * cm_, 4.6 * cm_,
            "4. LAYER PROCESSING (BARU)\nUtama: Spark SQL 4.2.0\n(PySpark In-Memory Catalyst)\n• Peringatan dini/jam (Q3)\n• Broadcast Join 300 grid (Q2)\n• Agregasi (0,15-0,26 s)\n\nKatalog & SQL Batch:\nApache Hive 4.2.1 (Docker+Tez)\n• Metastore & JDBC BI",
            fill=colors.HexColor("#fde2c8"),
        )
        # 5A. Serving API Peta (Dashed - Topic 12)
        self.box(
            c, 15.9 * cm_, 3.9 * cm_, 2.1 * cm_, 2.4 * cm_,
            "5A. SERVING\nAPI Peta &\nTabel Hasil\n(Topic 12)\nbelum ada",
            dash=True,
        )
        # 5B. Visualisasi Dashboard (Dashed - Topic 12)
        self.box(
            c, 15.9 * cm_, 0.8 * cm_, 2.1 * cm_, 2.2 * cm_,
            "5B. VISUALISASI\nDashboard Peta\n& Grafik Tren\n(Topic 12)",
            dash=True,
        )

        # Arrows
        self.arrow(c, 2.9 * cm_, 3.35 * cm_, 3.5 * cm_, 3.35 * cm_, "CSV", dash=True, ly=3)
        self.arrow(c, 5.6 * cm_, 3.7 * cm_, 6.4 * cm_, 4.8 * cm_, "put", dash=True, ly=3)
        self.arrow(c, 5.6 * cm_, 2.9 * cm_, 6.4 * cm_, 2.0 * cm_, "muat\nParquet", ly=2)
        self.arrow(c, 8.45 * cm_, 3.9 * cm_, 8.45 * cm_, 3.2 * cm_, "ekspor batch", dash=True, lx=1.0 * cm_, ly=-2)
        self.arrow(c, 10.5 * cm_, 2.0 * cm_, 11.4 * cm_, 2.0 * cm_, "pruning\n& baca", ly=3)

        # Top route from 3A (HBase) over Box 4 directly into 5A (Serving API Peta)
        c.saveState()
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.0)
        c.line(10.5 * cm_, 5.9 * cm_, 15.9 * cm_, 5.9 * cm_)
        c.restoreState()
        self.arrow(c, 15.3 * cm_, 5.9 * cm_, 15.9 * cm_, 5.9 * cm_, "")
        c.saveState()
        c.setFont("Helvetica-Oblique", 6.3)
        c.drawCentredString(13.2 * cm_, 6.02 * cm_, "get / scan sel (< 1 detik)")
        c.restoreState()

        self.arrow(c, 15.1 * cm_, 4.5 * cm_, 15.9 * cm_, 4.5 * cm_, "tabel\nhasil", dash=True, ly=3)
        self.arrow(c, 16.95 * cm_, 3.9 * cm_, 16.95 * cm_, 3.0 * cm_, "", dash=True)

        c.setFont("Helvetica-Oblique", 6.8)
        c.drawString(0, 0.2 * cm_, "Diagram Arsitektur v0.2: Garis penuh = sudah dibangun & diuji (Topic 9 Storage HBase + Topic 10 Processing Spark SQL & Hive). Garis putus-putus = Topic 11-12.")


def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.grey)
    c.drawString(1.4 * cm, 0.75 * cm, "Teknologi Big Data - Topic 10 (Layer Processing: Hive & Spark SQL) - Kelompok 6")
    c.drawRightString(A4[0] - 1.4 * cm, 0.75 * cm, "Halaman %d" % d.page)
    c.restoreState()


pdf_path = os.path.join(D, "Tugas_Topic10_Processing_Kelompok6.pdf")
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    leftMargin=1.4 * cm,
    rightMargin=1.4 * cm,
    topMargin=1.15 * cm,
    bottomMargin=1.25 * cm,
    title="Tugas Topic 10 - Desain Lapisan Processing (Hive dan Spark SQL)",
    author="Kelompok 6",
)

E = []

# ---------------- Halaman 1: Bab 1 & Bab 2 ----------------
E += [
    P("Desain Lapisan Processing (Hive dan Spark SQL): Pemantauan Titik Api Indonesia", title),
    P("Teknologi Big Data - Topic 10 - Tugas Kelompok", small),
    table(
        [
            ["Kelompok 6", "NPM", "Pembagian tugas"],
            ["Muhammad Bryan Farras", "2306230975", "Bab 1 (konteks kasus, peran layer processing, 3 query) & Bab 4 (analisis waktu, format, partisi, 100x)"],
            ["Mirza Adi Raffiansyah", "2306210323", "Bab 2 (desain skema tabel Teks, Parquet, Partisi tanggal, & tabel referensi provinsi)"],
            ["Calvin Wirathama Katoroy", "2306242395", "Bab 3 (instalasi Docker, Hive 4.2.1, PySpark 4.2.0, hands-on, screenshot, uji waktu median 3x)"],
            ["Salim", "2306204604", "Bab 5 (satu halaman Catatan Keputusan Desain), Diagram Arsitektur v0.2, & penyusunan PDF"],
        ],
        [4.8, 2.4, 11.0],
    ),
    Spacer(1, 2),
    P("Bab 1. Konteks Kasus Kelompok dan Peran Lapisan Processing", h1),
    P(
        "<b>Keterkaitan dengan kasus kelompok.</b> Laporan ini melanjutkan arsitektur sistem <b>pemantauan titik api (<i>hotspot</i>) kebakaran hutan dan lahan di Indonesia</b> "
        "menggunakan data satelit <b>VIIRS NASA FIRMS</b> (<i>sea_fires_7d.csv</i>, 19–25 September 2026) yang telah dirancang lapisan <i>storage</i>-nya pada <b>Topic 9 (Apache HBase)</b>. "
        "Sampel wilayah Indonesia berisi <b>54.516 baris</b> (rata-rata 7.788 titik/hari, puncak 10.974 titik pada 19 Sep dan 5.686 titik pada 25 Sep) yang tersebar pada <b>300 sel grid</b> (1° x 1°). "
        "Pada Topic 9, tabel HBase <font face='Courier'>hotspot</font> (<font face='Courier'>grid#tanggal_terbalik#jam#urut</font>) menjawab <i>get</i> satu titik (0,073 detik) dan <i>range scan</i> satu sel "
        "(0,967 detik untuk 925 baris <font face='Courier'>g087112</font>), tetapi HBase tidak mendukung <font face='Courier'>JOIN</font> maupun agregasi <font face='Courier'>GROUP BY</font>. "
        "Oleh sebab itu, <b>Pertanyaan 4</b> (penyaringan lintas sel tiap jam untuk peringatan dini) dan <b>Pertanyaan 5</b> (join ke batas provinsi & agregasi harian) dikerjakan di <b>lapisan processing</b> menggunakan <b>Apache Hive</b> dan <b>Spark SQL</b>."
    ),
    table(
        [
            ["No", "Pertanyaan Data Kasus Titik Api", "Pola Akses", "Frekuensi", "Lapisan & Mesin Penjawab"],
            ["1", "Tampilkan 20 titik api terbaru pada sel grid X (peta wilayah)", "Scan rentang sempit", "Setiap peta dibuka", "Storage Operasional: <b>HBase</b> (Topic 9)"],
            ["2", "Tampilkan detail satu titik api saat diklik pada peta", "Lookup per key (get)", "Puluhan kali/menit", "Storage Operasional: <b>HBase</b> (Topic 9)"],
            ["3", "Titik api pada sel X dalam N hari terakhir", "Scan rentang sempit", "Beberapa kali/menit", "Storage Operasional: <b>HBase</b> (Topic 9)"],
            ["4", "Peringatan dini titik api berbahaya (FRP >= 10 MW / high) pada hari puncak", "Filter partisi & agregasi", "Tiap jam", "Processing: <b>Spark SQL / Hive (Query 3)</b>"],
            ["5", "Jumlah titik api dan intensitas FRP per kategori serta per provinsi", "Agregasi & Join referensi", "Tiap jam / harian", "Processing: <b>Spark SQL / Hive (Query 1 & 2)</b>"],
        ],
        [0.7, 7.4, 3.1, 2.7, 4.3],
    ),
    Spacer(1, 2),
    P("Bab 2. Desain Skema Tabel (Teks, Parquet, Berpartisi) dan Tiga Query Uji", h1),
    P(
        "<b>Ukuran data uji (1x dan 10x).</b> Pengujian dilakukan pada dua skala data di direktori <font face='Courier'>/data</font> (<font face='Courier'>/root/topic10-data</font> pada filesystem <font face='Courier'>ext4</font> WSL2): "
        "<b>(1) Data Kecil (<font face='Courier'>1x</font> = 54.516 baris, 4,71 MB CSV)</b> berisi seluruh titik api Indonesia selama 7 hari (19–25 Sep 2026) dengan statistik identik Topic 9 "
        "(<i>nominal</i> 50.095, <i>low</i> 2.331, <i>high</i> 2.090; sel terpadat <font face='Courier'>g087112</font> = 5.107 baris); "
        "<b>(2) Data Diperbesar (<font face='Courier'>10x</font> = 545.160 baris, 47,71 MB CSV)</b> sebagai replikasi 10x lipat untuk menguji skalabilitas di luar waktu <i>start-up</i>; serta "
        "<b>(3) Tabel Referensi <font face='Courier'>ref_grid_provinsi</font> (300 baris)</b> yang memetakan seluruh 300 kode <font face='Courier'>grid_id</font> ke <font face='Courier'>provinsi</font>, <font face='Courier'>pulau</font>, <font face='Courier'>tingkat_rawan</font>, dan <font face='Courier'>luas_gambut_ha</font>."
    ),
    table(
        [
            ["Varian Tabel", "Nama Tabel (1x / 10x)", "Definisi Penyimpanan (Hive & Spark SQL)", "Perilaku Saat Query Berjalan"],
            ["1. Teks (CSV)", "hotspot_1x_text / hotspot_10x_text", "EXTERNAL TABLE ... ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE", "Membaca seluruh baris dan seluruh 14 kolom dari disk serta mengurai (parse) teks ke angka di CPU."],
            ["2. Parquet", "hotspot_1x_parquet / hotspot_10x_parquet", "STORED AS PARQUET (kolumnar biner terkompresi, tanpa partisi)", "Hanya membaca kolom yang diminta query (column projection) + memanfaatkan statistik min/max per blok."],
            ["3. Parquet Partisi", "hotspot_1x_part / hotspot_10x_part", "PARTITIONED BY (acq_date STRING) STORED AS PARQUET (7 partisi: 2026-09-19 s/d 2026-09-25)", "Proyeksi kolom Parquet + Partition Pruning: WHERE acq_date hanya membuka folder tanggal tersebut."],
        ],
        [2.5, 3.6, 5.7, 6.4],
        bold_first=True,
    ),
    Spacer(1, 2),
    P(
        "<b>Alasan pemilihan kolom partisi <font face='Courier'>acq_date</font>.</b> Kolom <font face='Courier'>acq_date</font> memiliki kardinalitas terukur (7 partisi/minggu, +-365 partisi/tahun) dan selalu menjadi filter utama laporan harian. "
        "Kami tidak mempartisi berdasar <font face='Courier'>hotspot_id</font> (54.516 nilai unik) karena akan menciptakan puluhan ribu folder kecil (<i>small files problem</i>) yang membebani Metastore dan HDFS."
    ),
    table(
        [
            ["Query", "Tujuan Analitik pada Kasus Titik Api", "Potongan Inti Query SQL (Sama di Hive dan Spark SQL)"],
            ["Q1_Agregasi", "Menghitung jumlah titik api, total FRP, rata-rata FRP, dan maksimum FRP per tingkat confidence & siang/malam.",
             "<font face='Courier'>SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp),2) AS total_frp_mw, ROUND(AVG(frp),2) AS rata_frp_mw, ROUND(MAX(frp),2) AS max_frp_mw FROM &lt;tabel&gt; GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;</font>"],
            ["Q2_Join", "Menggabungkan titik api (nominal & high) dengan tabel referensi 300 sel grid untuk Top 10 Provinsi Terdampak.",
             "<font face='Courier'>SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot, ROUND(SUM(h.frp),2) AS total_frp_mw, ROUND(AVG(h.frp),2) AS rata_frp_mw FROM &lt;tabel&gt; h JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal','high') GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;</font>"],
            ["Q3_Partisi", "Menyaring titik api berbahaya (FRP >= 10 MW) pada tanggal puncak kemarau (2026-09-19) per sel grid.",
             "<font face='Courier'>SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp),2) AS total_frp_mw, ROUND(MAX(frp),2) AS max_frp_mw FROM &lt;tabel&gt; WHERE acq_date = '2026-09-19' AND frp &gt;= 10.0 GROUP BY grid_id, confidence ORDER BY total_frp_mw DESC LIMIT 10;</font>"],
        ],
        [2.2, 4.8, 11.2],
        bold_first=True,
    ),
    PageBreak(),
]

# ---------------- Halaman 2: Bab 3 Bagian 1 (Instalasi, Web UI, & Tabel/Partisi) ----------------
E += [
    P("Bab 3. Bukti Hands-on Instalasi, Pembuatan Tabel, dan Hasil Query", h1),
    P(
        "<b>Lingkungan pengujian.</b> Seluruh pengukuran dijalankan pada mesin yang sama: <b>Windows 11 + WSL2 (Ubuntu 22.04 LTS)</b>, prosesor <b>Intel Core Ultra 7 155H (22 vCPU)</b>, <b>RAM 7,5 GiB</b>, SSD NVMe (<font face='Courier'>ext4</font>). "
        "<b>Apache Hive 4.2.1</b> dijalankan lewat kontainer resmi <font face='Courier'>apache/hive:4.2.1</font> di <b>Docker 29.1.3</b> (membawa JDK 21, HiveServer2, Derby Metastore, dan engine <b>Apache Tez</b>). "
        "<b>Apache Spark SQL</b> dijalankan lewat <b>PySpark 4.2.0</b> (<font face='Courier'>pip install pyspark==4.2.0 pyarrow</font>) di atas <b>OpenJDK 17.0.20.1</b> dan Python 3.10.12 dengan mode <font face='Courier'>local[*]</font> (22 thread). "
        "Sebagai pelengkap opsional materi kuliah, <b>Apache Pig 0.18.0</b> juga telah dipasang dan diverifikasi."
    ),
    shot("01_env_install.png", 12.6, "<b>Gambar 1.</b> Verifikasi instalasi Docker 29.1.3, kontainer hive4 (apache/hive:4.2.1 aktif di port 10000 & 10002), OpenJDK 17.0.20.1, PySpark 4.2.0, dan Pig 0.18.0. Menjawab: lingkungan kerja berjalan."),
    shot("02_hive_webui.png", 10.4, "<b>Gambar 2.</b> Antarmuka web HiveServer2 (http://localhost:10002) menampilkan layanan Apache Hive 4.2.1 aktif beserta riwayat eksekusi query Tez. Menjawab: server Hive & Metastore hidup.", crop=(0, 0, 1280, 580)),
    shot("03_hive_tables_part.png", 12.0, "<b>Gambar 3.</b> Beeline Hive: SHOW TABLES (7 tabel), SHOW PARTITIONS hotspot_1x_part (7 partisi tanggal), dan verifikasi jumlah baris (54.516 pada 1x dan 545.160 pada 10x). Menjawab: tabel Teks, Parquet, dan Partisi terbentuk."),
    PageBreak(),
]

# ---------------- Halaman 3: Bab 3 Bagian 2 (Hasil Query Hive & Spark + Log Benchmark) ----------------
E += [
    P("Bab 3 (Lanjutan). Bukti Hasil Eksekusi Tiga Query dan Pengukuran Waktu", h1),
    shot("04_hive_queries.png", 10.6, "<b>Gambar 4.</b> Hasil eksekusi tiga query (Q1_Agregasi, Q2_Join, Q3_Partisi) pada Apache Hive 4.2.1. Kalimantan Tengah tertinggi (26.136 titik, 362.561,43 MW) dan sel g087112 terpanas pada 19 Sep (6.585,45 MW)."),
    shot("05_spark_queries.png", 10.2, "<b>Gambar 5.</b> Hasil eksekusi tiga query yang sama di Apache Spark SQL (PySpark 4.2.0). Seluruh angka keluaran identik 100% dengan hasil Hive pada Gambar 4. Menjawab: konsistensi hasil lintas mesin."),
    shot_pair(
        "06_bench_hive.png",
        "<b>Gambar 6.</b> Log hasil pengukuran waktu 3 percobaan & median pada Apache Hive 4.2.1 (Tez) untuk data 1x & 10x.",
        "07_bench_spark.png",
        "<b>Gambar 7.</b> Log hasil pengukuran waktu 3 percobaan & median pada Apache Spark SQL (PySpark 4.2.0) untuk data 1x & 10x.",
        width_cm=8.8,
    ),
    PageBreak(),
]

# ---------------- Halaman 4: Bab 4 (Tabel Perbandingan & Analisis) ----------------
E += [
    P("Bab 4. Perbandingan Waktu Eksekusi Hive vs Spark SQL dan Analisis Teknis", h1),
    P(
        "<b>Tabel perbandingan waktu median (dari 3 kali percobaan).</b> Setelah 1 kali <i>warm-up</i> sesi, setiap query dijalankan 3 kali pada masing-masing kombinasi format tabel "
        "(Teks CSV, Parquet, Parquet Partisi) dan ukuran data (<b>1x = 54.516 baris</b> serta <b>10x = 545.160 baris</b>), lalu diambil nilai <b>median</b>-nya:"
    ),
    table(
        [
            ["Query", "Format Tabel", "Hive 1x (Run 1/2/3)", "Hive 1x Median", "Spark 1x Median", "Hive 10x (Run 1/2/3)", "Hive 10x Median", "Spark 10x Median", "Percepatan Spark (10x)"],
            ["Q1_Agregasi", "Teks (CSV)", "0,96 / 1,87 / 1,10", "1,102 s", "0,400 s", "1,22 / 1,16 / 1,10", "1,161 s", "0,451 s", "2,57x lebih cepat"],
            ["Q1_Agregasi", "Parquet", "1,20 / 1,17 / 1,01", "1,171 s", "0,260 s", "1,08 / 1,14 / 1,07", "1,084 s", "0,268 s", "4,04x lebih cepat"],
            ["Q1_Agregasi", "Parquet Partisi", "1,03 / 0,96 / 1,04", "1,034 s", "0,257 s", "1,06 / 1,01 / 0,99", "1,008 s", "0,208 s", "4,85x lebih cepat"],
            ["Q2_Join", "Teks (CSV)", "1,35 / 1,41 / 1,48", "1,413 s", "0,422 s", "1,64 / 1,66 / 1,72", "1,659 s", "0,429 s", "3,87x lebih cepat"],
            ["Q2_Join", "Parquet", "1,43 / 1,33 / 1,33", "1,326 s", "0,298 s", "1,45 / 1,44 / 1,39", "1,442 s", "0,409 s", "3,53x lebih cepat"],
            ["Q2_Join", "Parquet Partisi", "1,29 / 1,51 / 1,57", "1,512 s", "0,277 s", "1,54 / 1,49 / 1,42", "1,489 s", "0,261 s", "5,70x lebih cepat"],
            ["Q3_Partisi", "Teks (CSV)", "1,09 / 3,71 / 1,09", "1,094 s", "0,231 s", "1,38 / 1,37 / 1,43", "1,382 s", "0,272 s", "5,08x lebih cepat"],
            ["Q3_Partisi", "Parquet", "0,96 / 0,99 / 1,00", "0,993 s", "0,182 s", "0,90 / 0,82 / 0,98", "0,895 s", "0,171 s", "5,23x lebih cepat"],
            ["Q3_Partisi", "Parquet Partisi", "0,87 / 0,84 / 0,81", "<b>0,835 s</b>", "<b>0,151 s</b>", "0,89 / 0,80 / 0,92", "<b>0,893 s</b>", "<b>0,156 s</b>", "<b>5,72x lebih cepat</b>"],
        ],
        [2.0, 2.3, 2.4, 1.6, 1.6, 2.4, 1.6, 1.6, 2.7],
        bold_first=True,
    ),
    Spacer(1, 3),
    P("Analisis Teknis Hasil Pengukuran", h2),
    P(
        "<b>1. Mengapa format file (Teks CSV lawan Parquet) sangat berpengaruh?</b><br/>"
        "Pada tabel <b>Teks (CSV)</b>, mesin query wajib membaca setiap baris secara penuh (seluruh 14 kolom, 47,71 MB pada data 10x) lalu memecah delimiter koma dan mengonversi teks menjadi tipe numerik (<font face='Courier'>DOUBLE</font>/<font face='Courier'>INT</font>) di CPU. "
        "Sebaliknya, <b>Apache Parquet</b> menyimpan data secara <b>kolumnar biner</b> terkompresi (ukuran fisik di disk menyusut menjadi +-8,9 MB pada data 10x, menghemat >80% I/O) dan menanamkan statistik <font face='Courier'>min/max</font> di setiap <i>row group</i>. "
        "Saat menjalankan <font face='Courier'>Q1_Agregasi</font> yang hanya menyentuh 3 kolom (<font face='Courier'>confidence</font>, <font face='Courier'>daynight</font>, <font face='Courier'>frp</font>), pembaca Parquet langsung melompati 11 kolom lainnya (<i>column projection</i>). "
        "Di Spark SQL (10x), peralihan dari CSV ke Parquet mempercepat <font face='Courier'>Q1_Agregasi</font> dari <b>0,451 detik menjadi 0,268 detik (1,68x lebih cepat)</b>, dan di Hive mempercepat <font face='Courier'>Q3_Partisi</font> dari <b>1,382 detik menjadi 0,895 detik (1,54x lebih cepat)</b>."
    ),
    P(
        "<b>2. Mengapa partisi (<font face='Courier'>PARTITIONED BY acq_date</font>) mempercepat query berfilter tanggal?</b><br/>"
        "Pada <font face='Courier'>Q3_Partisi</font> (<font face='Courier'>WHERE acq_date = '2026-09-19' AND frp &gt;= 10.0</font>), tabel tanpa partisi harus memeriksa berkas seluruh 7 hari (545.160 baris pada 10x). "
        "Dengan <b>Parquet Berpartisi</b>, baik Hive maupun Spark melakukan <b>Partition Pruning</b>: mesin hanya membuka folder <font face='Courier'>acq_date=2026-09-19</font> (109.740 baris = 20,1% dari total data) dan melewati 6 folder tanggal lainnya tanpa membacanya sama sekali. "
        "Hasilnya, <font face='Courier'>Q3_Partisi</font> pada Parquet Berpartisi mencapai waktu tercepat di seluruh pengujian: <b>0,835 s (1x)</b> dan <b>0,893 s (10x)</b> di Hive, serta <b>0,151 s (1x)</b> dan <b>0,156 s (10x)</b> di Spark SQL. "
        "Sebaliknya, pada <font face='Courier'>Q1_Agregasi</font> dan <font face='Courier'>Q2_Join</font> yang tidak memfilter <font face='Courier'>acq_date</font>, seluruh 7 partisi tetap harus dibaca sehingga waktunya serupa dengan Parquet non-partisi."
    ),
    P(
        "<b>3. Mengapa Spark SQL 2,6x–5,7x lebih cepat daripada Hive (Tez), dan apa perbedaan sintaksnya?</b><br/>"
        "• <b>Perbedaan Mesin Eksekusi</b>: Walaupun Hive 4.2.1 sudah memakai <b>Apache Tez</b> (menghindari tulis ke HDFS antar-tahap seperti MapReduce lama), setiap query tetap melalui kompilasi rencana di HiveServer2, inisialisasi DAG Tez, dan pembacaan dari kontainer. "
        "Sebaliknya, <b>Spark SQL</b> mengandalkan <b>Catalyst Optimizer</b> dan <b>Tungsten Whole-Stage Code Generation</b> yang mengeksekusi tugas langsung di memori (<i>in-memory</i>) pada 22 thread paralel, serta secara otomatis melakukan <b>Broadcast Hash Join</b> terhadap tabel kecil <font face='Courier'>ref_grid_provinsi</font> (300 baris) pada <font face='Courier'>Q2_Join</font> (0,261 s di Spark vs 1,489 s di Hive, <b>5,70x lebih cepat</b>).<br/>"
        "• <b>Perbedaan Sintaks</b>: Sintaks SQL (<font face='Courier'>SELECT ... JOIN ... WHERE ... GROUP BY ... ORDER BY</font>) <b>100% identik</b> di kedua mesin. Perbedaannya hanya pada cara mendaftarkan tabel: Hive memakai DDL deklaratif di Metastore (<font face='Courier'>CREATE EXTERNAL TABLE ... PARTITIONED BY</font>), sedangkan PySpark memakai API DataFrame (<font face='Courier'>spark.read.parquet(...).createOrReplaceTempView(...)</font>)."
    ),
    P(
        "<b>4. Evaluasi Skalabilitas: Mengapa kenaikan 1x ke 10x landai, dan apa yang terjadi bila data diperbesar 100x?</b><br/>"
        "• <b>Dari 1x (54,5 rb baris) ke 10x (545,1 rb baris)</b>: Waktu hanya naik tipis (mis. <font face='Courier'>Q3_Partisi</font> CSV di Hive dari 1,094 s ke 1,382 s; Parquet Partisi di Spark dari 0,151 s ke 0,156 s). "
        "Ini membuktikan bahwa pada ukuran puluhan megabita, waktu eksekusi masih didominasi oleh <b>overhead tetap (penjadwalan task & inisialisasi DAG)</b> sebesar +-0,8 detik di Hive dan +-0,15 detik di Spark.<br/>"
        "• <b>Proyeksi pada 100x (5,45 juta baris, +-477 MB CSV) dan Arsip 10 Tahun (85 juta baris, +-7 GB CSV)</b>: Pada skala 100x ke atas, biaya baca disk (I/O) dan <i>shuffle</i> jaringan/memori akan mendominasi. "
        "Tabel <b>Teks (CSV)</b> akan melambat drastis secara linear, sementara <b>Parquet Berpartisi <font face='Courier'>acq_date</font></b> akan menjaga query peringatan harian tetap sub-detik karena hanya memindai 1 partisi tanggal. "
        "Dari sisi mesin: <b>Spark SQL</b> tetap jauh lebih cepat selama memori RAM klaster cukup menahan <i>hash table</i> dan buffer <i>shuffle</i>; namun jika memori terbatas saat melakukan <i>join</i> ratusan gigabita, Spark rawan mengalami <i>spill to disk</i> atau <i>OutOfMemoryError</i> (OOM), sedangkan <b>Hive di atas Tez</b> lebih stabil untuk pemrosesan <i>batch</i> raksasa dengan memori terbatas."
    ),
    PageBreak(),
]

# ---------------- Halaman 5: Bab 5 (Satu Halaman Catatan Keputusan Desain & Diagram v0.2) ----------------
E += [
    P("Bab 5. Catatan Keputusan Desain dan Diagram Arsitektur v0.2", h1),
    P(
        "Halaman ini merangkum <b>Catatan Keputusan Desain</b> pemilihan mesin query dan tata letak penyimpanan untuk lapisan <i>processing</i> proyek pemantauan titik api Indonesia, "
        "dilengkapi <b>Diagram Arsitektur v0.2</b> yang menambahkan lapisan <i>processing</i> di atas lapisan <i>storage</i> Topic 9."
    ),
    table(
        [
            ["Bagian", "Isi Keputusan Desain Proyek Pemantauan Titik Api Indonesia (Kelompok 6)"],
            [
                "Keputusan",
                "Memilih <b>Apache Spark SQL (PySpark 4.2.0) di atas format kolumnar Apache Parquet yang dipartisi per tanggal (<font face='Courier'>acq_date</font>)</b> sebagai mesin <i>processing</i> utama proyek, "
                "serta mempertahankan <b>Hive Metastore (Apache Hive 4.2.1)</b> di atas berkas Parquet yang sama untuk melayani akses SQL deklaratif/JDBC bagi laporan analitik dan BI.",
            ],
            [
                "Konteks",
                "Proyek memproses deteksi titik api VIIRS Indonesia (<b>54.516 baris/7 hari</b>, rata-rata <b>7.788 titik/hari</b>, puncak <b>10.974 titik/hari</b>, proyeksi 10 tahun <b>+-85 juta baris</b> pada <b>300 sel grid</b>). "
                "Lapisan <i>storage</i> operasional <b>HBase 2.6.7</b> (Topic 9) sudah menjawab <i>lookup</i> satu titik (0,073 s) dan <i>range scan</i> satu sel (0,967 s), tetapi sistem membutuhkan lapisan <i>processing</i> untuk menjawab: "
                "<b>(1) Pertanyaan 4 (peringatan dini tiap jam)</b> yang menyaring titik api berbahaya (<font face='Courier'>FRP &gt;= 10–50 MW</font> / confidence <font face='Courier'>high</font>) lintas sel, dan "
                "<b>(2) Pertanyaan 5 (laporan harian per provinsi)</b> yang menggabungkan (<font face='Courier'>JOIN</font>) titik api dengan 300 sel grid batas provinsi (<font face='Courier'>ref_grid_provinsi</font>). "
                "Selain itu, proyek akan berlanjut ke <i>streaming</i> (Topic 11: Kafka) dan pemodelan prediksi berbasis <i>machine learning</i>.",
            ],
            [
                "Alternatif ditolak",
                "1. <b>Format Teks (CSV) tanpa partisi</b>: Ditolak karena selalu membaca seluruh 14 kolom dan memindai semua tanggal; pada data 10x, <font face='Courier'>Q3_Partisi</font> di CSV (1,382 s di Hive; 0,272 s di Spark) "
                "lebih lambat <b>54%–74%</b> dibanding Parquet Berpartisi serta memakai ruang disk 5x lebih boros.<br/>"
                "2. <b>Apache Hive (Tez) sebagai satu-satunya mesin processing</b>: Ditolak untuk peringatan dini per jam dan pipeline terpadu karena latensinya pada seluruh pengujian (0,835–1,659 s) "
                "<b>2,57x hingga 5,72x lebih lambat</b> daripada Spark SQL (0,151–0,451 s), serta tidak mendukung <i>stream processing</i> dan ML dalam satu mesin.<br/>"
                "3. <b>Apache Pig (Pig Latin)</b>: Ditolak karena menggunakan bahasa <i>dataflow</i> prosedural khusus (diuji pada <font face='Courier'>hotspot_etl.pig</font>: 5,48 detik), tidak interaktif, dan tim sudah fasih memakai SQL.",
            ],
            [
                "Konsekuensi",
                "1. <b>Kebutuhan Memori (RAM) Lebih Tinggi</b>: Spark SQL memproses <i>shuffle</i> dan <font face='Courier'>BroadcastHashJoin</font> di memori, sehingga alokasi RAM executor dan jumlah partisi shuffle harus dijaga agar tidak mengalami OOM saat data mencapai puluhan juta baris.<br/>"
                "2. <b>Pipeline Konversi ke Parquet Berpartisi</b>: Data mentah harus ditulis ke format Parquet berpartisi <font face='Courier'>acq_date</font> dengan penggabungan file (<font face='Courier'>coalesce</font>/<font face='Courier'>repartition</font>) agar tidak menimbulkan ribuan <i>small files</i>.<br/>"
                "3. <b>Arsitektur Komplementer (HBase + Spark SQL/Hive)</b>: HBase melayani peta operasional berlatensi milidetik per key, sedangkan Spark SQL & Hive mengolah tabel analitik Parquet berpartisi untuk join provinsi dan agregasi.",
            ],
            [
                "Bukti",
                "Pengukuran median 3 kali percobaan pada data 1x (54.516 baris) dan 10x (545.160 baris) di mesin 22 vCPU / 7,5 GiB RAM (Gambar 3–7):<br/>"
                "• <b>Spark SQL vs Hive (10x Parquet Partisi)</b>: <font face='Courier'>Q1_Agregasi</font> <b>0,208 s vs 1,008 s (4,85x)</b>; <font face='Courier'>Q2_Join</font> <b>0,261 s vs 1,489 s (5,70x)</b>; <font face='Courier'>Q3_Partisi</font> <b>0,156 s vs 0,893 s (5,72x)</b>.<br/>"
                "• <b>Parquet Partisi vs Teks CSV (<font face='Courier'>Q3_Partisi</font> 10x)</b>: Waktu turun dari <b>1,382 s ke 0,893 s</b> di Hive (hemat 35,4%) dan dari <b>0,272 s ke 0,156 s</b> di Spark SQL (hemat 42,6%) berkat <i>Partition Pruning</i> (hanya membaca 1 dari 7 partisi = 109.740 baris).",
            ],
        ],
        [2.8, 15.4],
        bold_first=True,
    ),
    Spacer(1, 4),
    KeepTogether([
        P("<b>Diagram Arsitektur v0.2 (Storage HBase & Parquet + Layer Processing Spark SQL & Hive)</b>", base),
        Spacer(1, 2),
        DiagramV02(),
    ]),
]

doc.build(E, onFirstPage=footer, onLaterPages=footer)
print("PDF built successfully:", pdf_path)

# Also build DOCX version
try:
    from docx import Document
    from docx.shared import Inches, Pt

    wdoc = Document()
    wdoc.add_heading("Desain Lapisan Processing (Hive dan Spark SQL): Pemantauan Titik Api Indonesia", 0)
    wdoc.add_paragraph("Teknologi Big Data - Topic 10 - Tugas Kelompok (Kelompok 6)")
    wdoc.add_heading("Bab 1. Konteks Kasus Kelompok dan Peran Lapisan Processing", level=1)
    wdoc.add_paragraph(
        "Laporan ini melanjutkan arsitektur sistem pemantauan titik api (hotspot) kebakaran hutan dan lahan di Indonesia "
        "menggunakan data satelit VIIRS NASA FIRMS (sea_fires_7d.csv, 19-25 September 2026, 54.516 baris wilayah Indonesia pada 300 sel grid)."
    )
    for shot_file, caption_txt in [
        ("01_env_install.png", "Gambar 1. Verifikasi instalasi Docker, Hive 4.2.1, OpenJDK 17, PySpark 4.2.0, dan Pig 0.18.0."),
        ("02_hive_webui.png", "Gambar 2. Antarmuka web HiveServer2 (http://localhost:10002)."),
        ("03_hive_tables_part.png", "Gambar 3. SHOW TABLES, SHOW PARTITIONS, dan jumlah baris di Beeline Hive."),
        ("04_hive_queries.png", "Gambar 4. Hasil eksekusi tiga query (Agregasi, Join, Partisi) di Apache Hive 4.2.1."),
        ("05_spark_queries.png", "Gambar 5. Hasil eksekusi tiga query di Apache Spark SQL (PySpark 4.2.0)."),
        ("06_bench_hive.png", "Gambar 6. Pengukuran waktu 3 percobaan & median di Apache Hive 4.2.1."),
        ("07_bench_spark.png", "Gambar 7. Pengukuran waktu 3 percobaan & median di Apache Spark SQL 4.2.0."),
        ("08_diagram_v02.png", "Gambar 8. Diagram Arsitektur v0.2."),
    ]:
        sp = os.path.join(S, shot_file)
        if os.path.exists(sp):
            wdoc.add_picture(sp, width=Inches(6.0))
            wdoc.add_paragraph(caption_txt)
    docx_path = os.path.join(D, "Tugas_Topic10_Processing_Kelompok6.docx")
    wdoc.save(docx_path)
    print("DOCX built successfully:", docx_path)
except Exception as ex:
    print("DOCX build skipped:", ex)
