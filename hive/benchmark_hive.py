#!/usr/bin/env python3
"""
Benchmark 3 Query (Agregasi, Join, Partisi) di Apache Hive 4.2.1 (Tez)
Mengukur 3 percobaan per kombinasi (Data 1x & 10x; Format Teks, Parquet, Partisi)
dan mengambil nilai MEDIAN dari 3 kali percobaan.
"""
import os
import re
import json
import statistics
import subprocess

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUT_DIR, exist_ok=True)

TABLES = [
    ("1x", "Teks (CSV)", "hotspot_1x_text"),
    ("1x", "Parquet", "hotspot_1x_parquet"),
    ("1x", "Parquet Partisi", "hotspot_1x_part"),
    ("10x", "Teks (CSV)", "hotspot_10x_text"),
    ("10x", "Parquet", "hotspot_10x_parquet"),
    ("10x", "Parquet Partisi", "hotspot_10x_part"),
]

QUERIES = {
    "Q1_Agregasi": """
SELECT confidence, daynight, COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(AVG(frp), 2) AS rata_frp_mw,
       ROUND(MAX(frp), 2) AS max_frp_mw
FROM {table}
GROUP BY confidence, daynight
ORDER BY total_frp_mw DESC;
""".strip(),
    "Q2_Join": """
SELECT p.provinsi, p.pulau, COUNT(h.hotspot_id) AS jumlah_hotspot,
       ROUND(SUM(h.frp), 2) AS total_frp_mw, ROUND(AVG(h.frp), 2) AS rata_frp_mw
FROM {table} h
JOIN ref_grid_provinsi p ON h.grid_id = p.grid_id
WHERE h.confidence IN ('nominal', 'high')
GROUP BY p.provinsi, p.pulau
ORDER BY jumlah_hotspot DESC
LIMIT 10;
""".strip(),
    "Q3_Partisi": """
SELECT grid_id, confidence, COUNT(*) AS jumlah_hotspot,
       ROUND(SUM(frp), 2) AS total_frp_mw, ROUND(MAX(frp), 2) AS max_frp_mw
FROM {table}
WHERE acq_date = '2026-09-19' AND frp >= 10.0
GROUP BY grid_id, confidence
ORDER BY total_frp_mw DESC
LIMIT 10;
""".strip(),
}

# Build a single SQL batch file so Beeline connects once, runs 1 warm-up query,
# then executes 3 trials for each (table, query) combination.
sql_lines = [
    "USE hotspot_db;",
    "-- Warm-up",
    "SELECT COUNT(*) FROM hotspot_1x_part;",
]

order_keys = []
for scale, fmt_label, tbl in TABLES:
    for qname, qtmpl in QUERIES.items():
        qsql = " ".join(qtmpl.format(table=tbl).splitlines())
        for run_idx in range(1, 4):
            sql_lines.append(f"-- MARKER|{scale}|{fmt_label}|{tbl}|{qname}|run{run_idx}")
            sql_lines.append(qsql)
            order_keys.append((scale, fmt_label, tbl, qname, run_idx))

batch_sql_path = os.path.join(OUT_DIR, "bench_all.sql")
with open(batch_sql_path, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines) + "\n")

print("Copying bench_all.sql to container hive4 and executing via Beeline...")
subprocess.run(["docker", "cp", batch_sql_path, "hive4:/tmp/bench_all.sql"], check=True)

proc = subprocess.run(
    ["docker", "exec", "hive4", "/tmp/exec_sql.sh", "/tmp/bench_all.sql"],
    capture_output=True,
    text=True,
    check=True,
)

raw_log = proc.stdout + "\n" + proc.stderr
with open(os.path.join(OUT_DIR, "beeline_bench_raw.log"), "w", encoding="utf-8") as f:
    f.write(raw_log)

# Parse times from Beeline output: "X row(s) selected (Y.YYY seconds)"
time_matches = re.findall(r"rows? selected \(([0-9.]+) seconds\)", raw_log)
print(f"Found {len(time_matches)} timed query executions (expected 1 warm-up + {len(order_keys)} = {len(order_keys)+1})")

# Skip the first match (warm-up SELECT COUNT(*))
query_times = [float(x) for x in time_matches[1:]]
assert len(query_times) == len(order_keys), f"Mismatch: got {len(query_times)} vs {len(order_keys)}"

results = {}
for (scale, fmt_label, tbl, qname, run_idx), t_sec in zip(order_keys, query_times):
    key = f"{scale}|{fmt_label}|{qname}"
    if key not in results:
        results[key] = {
            "scale": scale,
            "format": fmt_label,
            "table": tbl,
            "query": qname,
            "runs": [],
        }
    results[key]["runs"].append(round(t_sec, 4))

summary_lines = [
    "========================================================================================",
    "HASIL BENCHMARK APACHE HIVE 4.2.1 (TEZ) - MEDIAN DARI 3 PERCOBAAN (DETIK)",
    "========================================================================================",
    f"{'Skala':<6} | {'Format Tabel':<16} | {'Query':<13} | {'Run 1':<7} | {'Run 2':<7} | {'Run 3':<7} | {'Median (s)':<10}",
    "-" * 88,
]

for key, item in results.items():
    med = round(statistics.median(item["runs"]), 4)
    item["median"] = med
    r1, r2, r3 = item["runs"]
    summary_lines.append(
        f"{item['scale']:<6} | {item['format']:<16} | {item['query']:<13} | {r1:<7.3f} | {r2:<7.3f} | {r3:<7.3f} | {med:<10.3f}"
    )

summary_text = "\n".join(summary_lines)
print(summary_text)

with open(os.path.join(OUT_DIR, "benchmark_hive.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

with open(os.path.join(OUT_DIR, "benchmark_hive_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary_text + "\n")

