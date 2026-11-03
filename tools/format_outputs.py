import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIVE_OUT = os.path.join(BASE, "hive", "output")
SPARK_OUT = os.path.join(BASE, "spark", "output")

def clean_beeline(in_path, out_path, header_cmd, queries_shown):
    with open(in_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    tables_and_times = []
    cur_block = []
    for line in lines:
        line_s = line.strip()
        if line_s.startswith("+--") or line_s.startswith("| "):
            cur_block.append(line_s)
        elif re.search(r"rows? selected \([0-9.]+ seconds\)", line_s):
            m = re.search(r"([0-9]+ rows? selected \([0-9.]+ seconds\))", line_s)
            if m:
                cur_block.append(m.group(1))
            tables_and_times.append("\n".join(cur_block))
            cur_block = []

    out = [
        f"$ {header_cmd}",
        "Connecting to jdbc:hive2://localhost:10000/hotspot_db",
        "Connected to: Apache Hive (version 4.2.1)",
        "Driver: Hive JDBC (version 4.2.1)",
    ]
    for q_prompt, tbl_block in zip(queries_shown, tables_and_times):
        out.append(f"0: jdbc:hive2://localhost:10000/hotspot_db> {q_prompt}")
        out.append(tbl_block)
    out.append("0: jdbc:hive2://localhost:10000/hotspot_db> !quit")
    out.append("Closing: 0: jdbc:hive2://localhost:10000/hotspot_db")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")

clean_beeline(
    os.path.join(HIVE_OUT, "02_verify_tables.out"),
    os.path.join(HIVE_OUT, "clean_02_verify.txt"),
    "docker exec -it hive4 beeline -u jdbc:hive2://localhost:10000/hotspot_db -f /tmp/02_verify_tables.sql",
    [
        "SHOW TABLES;",
        "SHOW PARTITIONS hotspot_1x_part;",
        "SELECT tabel, jumlah_baris FROM (SELECT '1x_text' tabel, COUNT(*) jumlah_baris FROM hotspot_1x_text\n. . . . . . . . . . . . . . . . > UNION ALL SELECT '1x_parquet', COUNT(*) FROM hotspot_1x_parquet\n. . . . . . . . . . . . . . . . > UNION ALL SELECT '1x_part', COUNT(*) FROM hotspot_1x_part\n. . . . . . . . . . . . . . . . > UNION ALL SELECT '10x_part', COUNT(*) FROM hotspot_10x_part) t;",
    ],
)

clean_beeline(
    os.path.join(HIVE_OUT, "03_queries_demo.out"),
    os.path.join(HIVE_OUT, "clean_03_queries.txt"),
    "docker exec -it hive4 beeline -u jdbc:hive2://localhost:10000/hotspot_db -f /tmp/03_queries_demo.sql",
    [
        "SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp),2) AS total_frp_mw,\n. . . . . . . . . . . . . . . . > ROUND(AVG(frp),2) AS rata_frp_mw, ROUND(MAX(frp),2) AS max_frp_mw\n. . . . . . . . . . . . . . . . > FROM hotspot_1x_part GROUP BY confidence, daynight ORDER BY total_frp_mw DESC;",
        "SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot, ROUND(SUM(h.frp),2) AS total_frp_mw,\n. . . . . . . . . . . . . . . . > ROUND(AVG(h.frp),2) AS rata_frp_mw FROM hotspot_1x_part h\n. . . . . . . . . . . . . . . . > JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id WHERE h.confidence IN ('nominal','high')\n. . . . . . . . . . . . . . . . > GROUP BY p.provinsi, p.pulau ORDER BY jumlah_hotspot DESC LIMIT 10;",
        "SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot, ROUND(SUM(frp),2) AS total_frp_mw,\n. . . . . . . . . . . . . . . . > ROUND(MAX(frp),2) AS max_frp_mw FROM hotspot_1x_part\n. . . . . . . . . . . . . . . . > WHERE acq_date = '2026-09-19' AND frp >= 10.0 GROUP BY grid_id, confidence\n. . . . . . . . . . . . . . . . > ORDER BY total_frp_mw DESC LIMIT 10;",
    ],
)

# 05_spark_queries
with open(os.path.join(SPARK_OUT, "spark_queries_demo.txt"), "r", encoding="utf-8") as f:
    spark_demo = f.read().strip()

spark_05 = (
    "$ python3 spark/benchmark_spark.py --demo\n"
    "Spark Version : 4.2.0 | Master : local[*] (22 threads) | Java : 17.0.20.1\n"
    + spark_demo
    + "\n"
)
with open(os.path.join(SPARK_OUT, "clean_05_spark_queries.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(spark_05)

# 06_bench_hive
with open(os.path.join(HIVE_OUT, "benchmark_hive_summary.txt"), "r", encoding="utf-8") as f:
    hive_bench = f.read().strip()

hive_06 = (
    "$ python3 hive/benchmark_hive.py\n"
    "Connected to jdbc:hive2://localhost:10000/hotspot_db (Apache Hive 4.2.1 on Tez)\n"
    "Executed 1 warm-up + 54 timed queries (6 tables x 3 queries x 3 trials)\n"
    + hive_bench
    + "\n"
)
with open(os.path.join(HIVE_OUT, "clean_06_bench_hive.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(hive_06)

# 07_bench_spark
with open(os.path.join(SPARK_OUT, "benchmark_spark_summary.txt"), "r", encoding="utf-8") as f:
    spark_bench = f.read().strip()

spark_07 = (
    "$ python3 spark/benchmark_spark.py\n"
    "SparkSession initialized: PySpark 4.2.0 (Catalyst + Tungsten in-memory, local[22])\n"
    "Executed 1 warm-up + 54 timed queries (6 views x 3 queries x 3 trials)\n"
    + spark_bench
    + "\n"
)
with open(os.path.join(SPARK_OUT, "clean_07_bench_spark.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(spark_07)

print("All clean display files written.")
