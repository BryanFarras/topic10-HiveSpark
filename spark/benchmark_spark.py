#!/usr/bin/env python3
"""
Benchmark & Demo 3 Query (Agregasi, Join, Partisi) di Apache Spark SQL (PySpark 4.2.0)
Membuat dataset berformat Teks (CSV), Parquet, dan Parquet Berpartisi (acq_date),
menjalankan 3 query yang sama persis dengan Hive, mengukur waktu 3 kali percobaan,
dan mencatat nilai MEDIAN dari 3 percobaan.
"""
import os
import time
import json
import shutil
import statistics
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType
)

BASE_DIR = "/root/topic10-data"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT_DIR, exist_ok=True)

spark = (
    SparkSession.builder
    .appName("Topic10_Hotspot_VIIRS_SparkSQL_Kelompok6")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "8")
    .config("spark.ui.showConsoleProgress", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

print(f"Spark Version : {spark.version}")
print(f"Spark Master  : {spark.sparkContext.master}")
print(f"Default Par.  : {spark.sparkContext.defaultParallelism}")

hotspot_schema = StructType([
    StructField("hotspot_id", IntegerType(), True),
    StructField("grid_id", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("bright_ti4", DoubleType(), True),
    StructField("scan", DoubleType(), True),
    StructField("track", DoubleType(), True),
    StructField("acq_date", StringType(), True),
    StructField("acq_time", StringType(), True),
    StructField("satellite", StringType(), True),
    StructField("confidence", StringType(), True),
    StructField("bright_ti5", DoubleType(), True),
    StructField("frp", DoubleType(), True),
    StructField("daynight", StringType(), True),
])

ref_schema = StructType([
    StructField("grid_id", StringType(), True),
    StructField("provinsi", StringType(), True),
    StructField("pulau", StringType(), True),
    StructField("tingkat_rawan", StringType(), True),
    StructField("luas_gambut_ha", IntegerType(), True),
])

# 1. Load Reference Table
df_ref = spark.read.schema(ref_schema).csv(f"{BASE_DIR}/ref_grid/ref_grid_provinsi.csv")
df_ref.createOrReplaceTempView("ref_grid_provinsi")

# 2. Prepare Parquet & Partitioned Parquet directories for Spark SQL
spark_store = f"{BASE_DIR}/spark_tables"
if os.path.exists(spark_store):
    shutil.rmtree(spark_store)
os.makedirs(spark_store, exist_ok=True)

for scale, folder in [("1x", "hotspot_1x"), ("10x", "hotspot_10x")]:
    csv_path = f"{BASE_DIR}/{folder}/hotspot_{scale}.csv"
    pq_path = f"{spark_store}/hotspot_{scale}_parquet"
    part_path = f"{spark_store}/hotspot_{scale}_part"

    df_csv = spark.read.schema(hotspot_schema).csv(csv_path)
    df_csv.createOrReplaceTempView(f"hotspot_{scale}_text")

    df_csv.coalesce(1).write.mode("overwrite").parquet(pq_path)
    df_pq = spark.read.parquet(pq_path)
    df_pq.createOrReplaceTempView(f"hotspot_{scale}_parquet")

    df_csv.repartition(1, "acq_date").write.mode("overwrite").partitionBy("acq_date").parquet(part_path)
    df_part = spark.read.parquet(part_path)
    df_part.createOrReplaceTempView(f"hotspot_{scale}_part")

print("All Spark SQL views registered: hotspot_1x_{text,parquet,part} & hotspot_10x_{text,parquet,part}")

QUERIES = {
    "Q1_Agregasi": """
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,
       ROUND(MAX(frp), 2) AS max_frp_mw
FROM {table}
GROUP BY confidence, daynight
ORDER BY total_frp_mw DESC
""".strip(),
    "Q2_Join": """
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,
       ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw
FROM {table} h
JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id
WHERE h.confidence IN ('nominal', 'high')
GROUP BY p.provinsi, p.pulau
ORDER BY jumlah_hotspot DESC
LIMIT 10
""".strip(),
    "Q3_Partisi": """
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw
FROM {table}
WHERE acq_date = '2026-09-19' AND frp >= 10.0
GROUP BY grid_id, confidence
ORDER BY total_frp_mw DESC
LIMIT 10
""".strip(),
}

# Print sample outputs from hotspot_1x_part for verification & screenshot
demo_lines = [
    "========================================================================",
    f"HASIL EKSEKUSI 3 QUERY DI SPARK SQL (PySpark {spark.version})",
    "========================================================================",
]
for qname, qtmpl in QUERIES.items():
    print(f"\n--- {qname} (hotspot_1x_part) ---")
    demo_lines.append(f"\n--- {qname} (hotspot_1x_part) ---")
    df_res = spark.sql(qtmpl.format(table="hotspot_1x_part"))
    out_str = df_res._jdf.showString(10, 40, False)
    print(out_str)
    demo_lines.append(out_str)

with open(os.path.join(OUT_DIR, "spark_queries_demo.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(demo_lines) + "\n")

# Warm-up Catalyst & JVM
spark.sql("SELECT COUNT(*) FROM hotspot_1x_part").collect()

TABLES = [
    ("1x", "Teks (CSV)", "hotspot_1x_text"),
    ("1x", "Parquet", "hotspot_1x_parquet"),
    ("1x", "Parquet Partisi", "hotspot_1x_part"),
    ("10x", "Teks (CSV)", "hotspot_10x_text"),
    ("10x", "Parquet", "hotspot_10x_parquet"),
    ("10x", "Parquet Partisi", "hotspot_10x_part"),
]

results = {}
for scale, fmt_label, tbl in TABLES:
    for qname, qtmpl in QUERIES.items():
        qsql = qtmpl.format(table=tbl)
        runs = []
        for run_idx in range(1, 4):
            spark.catalog.clearCache()
            t0 = time.perf_counter()
            _ = spark.sql(qsql).collect()
            elapsed = time.perf_counter() - t0
            runs.append(round(elapsed, 4))
        med = round(statistics.median(runs), 4)
        key = f"{scale}|{fmt_label}|{qname}"
        results[key] = {
            "scale": scale,
            "format": fmt_label,
            "table": tbl,
            "query": qname,
            "runs": runs,
            "median": med,
        }

summary_lines = [
    "========================================================================================",
    f"HASIL BENCHMARK SPARK SQL (PySpark {spark.version}) - MEDIAN DARI 3 PERCOBAAN (DETIK)",
    "========================================================================================",
    f"{'Skala':<6} | {'Format Tabel':<16} | {'Query':<13} | {'Run 1':<7} | {'Run 2':<7} | {'Run 3':<7} | {'Median (s)':<10}",
    "-" * 88,
]
for key, item in results.items():
    r1, r2, r3 = item["runs"]
    summary_lines.append(
        f"{item['scale']:<6} | {item['format']:<16} | {item['query']:<13} | {r1:<7.4f} | {r2:<7.4f} | {r3:<7.4f} | {item['median']:<10.4f}"
    )

summary_text = "\n".join(summary_lines)
print("\n" + summary_text)

with open(os.path.join(OUT_DIR, "benchmark_spark.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

with open(os.path.join(OUT_DIR, "benchmark_spark_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary_text + "\n")

spark.stop()

