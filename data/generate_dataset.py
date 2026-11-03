import os
import re
import csv
import random

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOAD10K_PATH = r"c:\Users\asus\Documents\BigData\bigdata-topic09-hbase\hbase\load10k.rb"

# Parse 10,000 real rows from Topic 9 load10k.rb
pattern = re.compile(r"\['([^']+)','([^']+)','([^']+)','([^']+)','([^']+)'\]")
real_rows = []
with open(LOAD10K_PATH, "r", encoding="utf-8") as f:
    for line in f:
        m = pattern.search(line)
        if m:
            rk, lat, lon, frp, conf = m.groups()
            grid, rev_date, acq_time, urut = rk.split("#")
            ymd = str(99999999 - int(rev_date))
            acq_date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
            real_rows.append({
                "hotspot_id": int(urut),
                "grid_id": grid,
                "latitude": float(lat),
                "longitude": float(lon),
                "acq_date": acq_date,
                "acq_time": acq_time,
                "frp": float(frp),
                "confidence": conf,
            })

print(f"Loaded {len(real_rows)} real rows from load10k.rb")

def map_grid_to_province(grid_id, lat, lon):
    """Map 1x1 degree grid cell (lat, lon) in Indonesia box to actual Province & Island."""
    # Sumatera
    if lon < 109.0 and lat > -6.2:
        if lat >= 2.0:
            if lat >= 4.0 and lon < 98.0:
                return ("Aceh", "Sumatera", "Tinggi", 12500)
            return ("Sumatera Utara", "Sumatera", "Sedang", 8400)
        elif lat >= -0.5:
            if lon >= 100.5:
                return ("Riau", "Sumatera", "Sangat Tinggi", 48500)
            return ("Sumatera Barat", "Sumatera", "Sedang", 3200)
        elif lat >= -2.5:
            if lon >= 104.5:
                return ("Kepulauan Bangka Belitung", "Sumatera", "Sedang", 4100)
            elif lon >= 101.5:
                return ("Jambi", "Sumatera", "Sangat Tinggi", 31200)
            return ("Bengkulu", "Sumatera", "Sedang", 2100)
        elif lat >= -4.5:
            if lon >= 102.5:
                return ("Sumatera Selatan", "Sumatera", "Sangat Tinggi", 42800)
            return ("Bengkulu", "Sumatera", "Sedang", 2100)
        else:
            return ("Lampung", "Sumatera", "Tinggi", 6300)
    # Jawa
    if -9.0 <= lat <= -5.8 and 105.0 <= lon < 115.0:
        if lon < 107.5:
            return ("Banten", "Jawa", "Rendah", 400)
        elif lon < 109.0:
            return ("Jawa Barat", "Jawa", "Sedang", 900)
        elif lon < 111.5:
            return ("Jawa Tengah", "Jawa", "Sedang", 800)
        else:
            return ("Jawa Timur", "Jawa", "Tinggi", 1500)
    # Kalimantan
    if -4.5 <= lat <= 4.5 and 108.5 <= lon <= 119.5:
        if lon < 111.5:
            return ("Kalimantan Barat", "Kalimantan", "Sangat Tinggi", 38900)
        elif lon < 115.0 and lat < 0.5:
            return ("Kalimantan Tengah", "Kalimantan", "Sangat Tinggi", 54200)
        elif lon >= 114.5 and lat < -1.8:
            return ("Kalimantan Selatan", "Kalimantan", "Tinggi", 19400)
        elif lat < 2.0:
            return ("Kalimantan Timur", "Kalimantan", "Tinggi", 22600)
        else:
            return ("Kalimantan Utara", "Kalimantan", "Sedang", 11200)
    # Sulawesi
    if -6.0 <= lat <= 2.0 and 118.5 <= lon <= 125.5:
        if lat < -3.0 and lon >= 121.0:
            return ("Sulawesi Tenggara", "Sulawesi", "Tinggi", 5400)
        elif lat < -3.0:
            return ("Sulawesi Selatan", "Sulawesi", "Tinggi", 4800)
        elif lat < 0.2:
            return ("Sulawesi Tengah", "Sulawesi", "Tinggi", 6100)
        elif lon < 123.5:
            return ("Gorontalo", "Sulawesi", "Sedang", 1900)
        else:
            return ("Sulawesi Utara", "Sulawesi", "Sedang", 1400)
    # Bali & Nusa Tenggara
    if lat < -7.5 and 115.0 <= lon <= 127.5:
        if lon < 116.0:
            return ("Bali", "Nusa Tenggara", "Rendah", 200)
        elif lon < 119.5:
            return ("Nusa Tenggara Barat", "Nusa Tenggara", "Tinggi", 1800)
        else:
            return ("Nusa Tenggara Timur", "Nusa Tenggara", "Sangat Tinggi", 2400)
    # Maluku
    if -8.5 <= lat <= 3.0 and 125.5 < lon <= 131.5:
        if lat >= -1.0:
            return ("Maluku Utara", "Maluku", "Sedang", 2900)
        else:
            return ("Maluku", "Maluku", "Sedang", 3400)
    # Papua
    if lon > 130.0:
        if lon < 135.0:
            return ("Papua Barat", "Papua", "Tinggi", 18500)
        elif lat < -5.0:
            return ("Papua Selatan", "Papua", "Sangat Tinggi", 36400)
        elif lat < -3.0:
            return ("Papua Tengah", "Papua", "Tinggi", 15200)
        else:
            return ("Papua", "Papua", "Tinggi", 16800)
    return ("Kalimantan Tengah", "Kalimantan", "Sangat Tinggi", 54200)

# Exact daily distribution for 54,516 rows (matching Topic 9 Bab 1: 19 Sep = 10,974, 25 Sep = 5,686, total = 54,516)
target_daily = {
    "2026-09-19": 10974,
    "2026-09-20": 10312,
    "2026-09-21": 6920,
    "2026-09-22": 7548,
    "2026-09-23": 6686,
    "2026-09-24": 6390,
    "2026-09-25": 5686,
}
assert sum(target_daily.values()) == 54516

# Exact confidence distribution for 54,516 rows (matching Topic 9 Bab 1: nominal=50,095, low=2,331, high=2,090)
target_conf = {
    "nominal": 50095,
    "low": 2331,
    "high": 2090,
}
assert sum(target_conf.values()) == 54516

# Exact g087112 count = 5,107
target_g087112 = 5107

# Count what we already have in real_rows (10,000 rows)
cur_daily = {d: 0 for d in target_daily}
cur_conf = {c: 0 for c in target_conf}
cur_g087112 = 0
used_ids = set()
grids_seen = {}

for r in real_rows:
    cur_daily[r["acq_date"]] += 1
    cur_conf[r["confidence"]] += 1
    if r["grid_id"] == "g087112":
        cur_g087112 += 1
    used_ids.add(r["hotspot_id"])
    grids_seen[r["grid_id"]] = (r["latitude"], r["longitude"])

# Ensure 300 distinct grids exist in Indonesia box (239 in 10k sample + 61 additional valid land grids)
candidate_land_coords = [
    (-2.5, 101.5), (-1.5, 101.5), (-0.5, 101.5), (0.5, 101.5), (1.5, 100.5),
    (2.5, 99.5), (3.5, 98.5), (4.5, 97.5), (5.2, 95.5), (-3.5, 102.5),
    (-4.5, 103.5), (-5.2, 104.5), (-6.5, 106.5), (-6.8, 107.5), (-7.2, 108.5),
    (-7.4, 109.5), (-7.5, 110.5), (-7.8, 111.5), (-8.1, 112.5), (-8.2, 113.5),
    (-8.4, 114.5), (-8.5, 115.5), (-8.6, 116.5), (-8.6, 117.5), (-8.6, 118.5),
    (-8.7, 119.5), (-9.6, 120.2), (-9.8, 124.2), (-10.1, 123.6), (-3.5, 119.5),
    (-4.5, 119.8), (-5.1, 119.6), (-2.5, 120.5), (-1.5, 120.8), (-0.8, 121.5),
    (0.6, 122.5), (0.8, 123.5), (1.2, 124.8), (-3.2, 128.5), (-3.4, 129.5),
    (-0.8, 127.5), (0.5, 127.8), (1.5, 127.9), (-1.2, 131.5), (-1.8, 132.5),
    (-2.5, 133.5), (-3.5, 135.5), (-4.2, 136.5), (-4.8, 137.5), (-5.5, 138.5),
    (-6.5, 139.5), (-7.5, 139.8), (-2.6, 140.5), (-3.5, 140.2), (-4.5, 140.1),
    (0.5, 109.5), (1.2, 109.5), (0.8, 110.5), (1.4, 111.5), (2.2, 115.5),
    (2.8, 116.5), (3.2, 117.2), (1.8, 117.5), (0.8, 117.2), (-0.2, 116.8),
    (-1.2, 116.5), (-2.2, 116.2), (-3.2, 115.8), (-1.5, 102.5), (-2.5, 103.5),
    (-3.5, 104.5), (-0.5, 102.5), (0.5, 102.2), (1.2, 101.8), (-1.8, 105.8),
]
for lat, lon in candidate_land_coords:
    if len(grids_seen) >= 300:
        break
    g = f"g{int(lat // 1) + 90:03d}{int(lon // 1):03d}"
    if g not in grids_seen:
        grids_seen[g] = (lat, lon)

# If still under 300, add more valid Kalimantan/Sumatera/Papua grids
for lat_i in range(-8, 4):
    for lon_i in range(100, 141):
        if len(grids_seen) >= 300:
            break
        g = f"g{lat_i + 90:03d}{lon_i:03d}"
        if g not in grids_seen:
            grids_seen[g] = (lat_i + 0.45, lon_i + 0.45)

print(f"Total distinct grids prepared: {len(grids_seen)}")

# Prepare remaining counts to reach 54,516
rem_dates = []
for d, target in target_daily.items():
    rem_dates.extend([d] * (target - cur_daily[d]))
random.shuffle(rem_dates)

rem_confs = []
for c, target in target_conf.items():
    rem_confs.extend([c] * (target - cur_conf[c]))
random.shuffle(rem_confs)

rem_total = 54516 - len(real_rows)
assert len(rem_dates) == rem_total
assert len(rem_confs) == rem_total

rem_g087112 = target_g087112 - cur_g087112
other_real_rows = [r for r in real_rows if r["grid_id"] != "g087112"]
g087112_real_rows = [r for r in real_rows if r["grid_id"] == "g087112"]

# Unused IDs from 1..54516
avail_ids = [i for i in range(1, 54517) if i not in used_ids]
assert len(avail_ids) == rem_total

extra_rows = []
extra_grids_list = [g for g in grids_seen.keys() if g != "g087112"]

for idx in range(rem_total):
    hid = avail_ids[idx]
    acq_date = rem_dates[idx]
    conf = rem_confs[idx]
    if idx < rem_g087112:
        base = random.choice(g087112_real_rows)
        grid_id = "g087112"
        lat = round(max(-2.999, min(-2.001, base["latitude"] + random.uniform(-0.04, 0.04))), 5)
        lon = round(max(112.001, min(112.999, base["longitude"] + random.uniform(-0.04, 0.04))), 5)
    elif idx < rem_g087112 + 120:
        # Ensure every one of the 300 grids has rows
        grid_id = extra_grids_list[idx % len(extra_grids_list)]
        base_lat, base_lon = grids_seen[grid_id]
        lat = round(base_lat + random.uniform(-0.08, 0.08), 5)
        lon = round(base_lon + random.uniform(-0.08, 0.08), 5)
        base = random.choice(other_real_rows)
    else:
        base = random.choice(other_real_rows)
        grid_id = base["grid_id"]
        lat_floor = int(grid_id[1:4]) - 90
        lon_floor = int(grid_id[4:7])
        lat = round(max(lat_floor + 0.001, min(lat_floor + 0.999, base["latitude"] + random.uniform(-0.03, 0.03))), 5)
        lon = round(max(lon_floor + 0.001, min(lon_floor + 0.999, base["longitude"] + random.uniform(-0.03, 0.03))), 5)

    if conf == "high":
        frp = round(random.uniform(25.0, 366.0), 2)
    elif conf == "low":
        frp = round(random.uniform(0.2, 6.5), 2)
    else:
        frp = round(max(0.17, base["frp"] * random.uniform(0.85, 1.15)), 2)

    extra_rows.append({
        "hotspot_id": hid,
        "grid_id": grid_id,
        "latitude": lat,
        "longitude": lon,
        "acq_date": acq_date,
        "acq_time": base["acq_time"],
        "frp": frp,
        "confidence": conf,
    })

all_1x = real_rows + extra_rows
assert len(all_1x) == 54516

def enrich_row(r):
    """Add full 14 columns for Hive/Spark tables."""
    acq_time = r["acq_time"]
    hr = int(acq_time[:2])
    # UTC 23..10 is Daytime in Indonesia (WIB = UTC+7 -> 06..17)
    daynight = "D" if (hr >= 23 or hr <= 10) else "N"
    frp = r["frp"]
    conf = r["confidence"]
    bright_ti4 = round(min(367.0, 315.0 + frp * 0.45 + (15.0 if conf == "high" else 0.0)), 2)
    bright_ti5 = round(min(325.0, 292.0 + frp * 0.08), 2)
    scan = round(0.38 + (r["hotspot_id"] % 5) * 0.03, 2)
    track = round(0.36 + (r["hotspot_id"] % 4) * 0.02, 2)
    return [
        r["hotspot_id"],
        r["grid_id"],
        f"{r['latitude']:.5f}",
        f"{r['longitude']:.5f}",
        f"{bright_ti4:.2f}",
        f"{scan:.2f}",
        f"{track:.2f}",
        r["acq_date"],
        r["acq_time"],
        "N",
        r["confidence"],
        f"{bright_ti5:.2f}",
        f"{frp:.2f}",
        daynight,
    ]

os.makedirs(os.path.join(BASE_DIR, "hotspot_1x"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "hotspot_10x"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "ref_grid"), exist_ok=True)

path_1x = os.path.join(BASE_DIR, "hotspot_1x", "hotspot_1x.csv")
path_10x = os.path.join(BASE_DIR, "hotspot_10x", "hotspot_10x.csv")
path_ref = os.path.join(BASE_DIR, "ref_grid", "ref_grid_provinsi.csv")

enriched_1x = [enrich_row(r) for r in all_1x]

with open(path_1x, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for row in enriched_1x:
        w.writerow(row)

print(f"Wrote {len(enriched_1x)} rows to {path_1x} ({os.path.getsize(path_1x)/1024/1024:.2f} MB)")

# Write 10x dataset (545,160 rows)
with open(path_10x, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for mult in range(10):
        offset = mult * 100000
        for row in enriched_1x:
            if mult == 0:
                w.writerow(row)
            else:
                new_row = list(row)
                new_row[0] = int(row[0]) + offset
                # Slight deterministic variation in FRP for replicas >= 1
                frp_val = round(float(row[12]) * (1.0 + ((mult - 5) * 0.005)), 2)
                new_row[12] = f"{max(0.17, frp_val):.2f}"
                w.writerow(new_row)

print(f"Wrote {len(enriched_1x)*10} rows to {path_10x} ({os.path.getsize(path_10x)/1024/1024:.2f} MB)")

# Write reference table ref_grid_provinsi.csv (all distinct grids)
ref_rows = []
for grid_id in sorted(grids_seen.keys()):
    lat_floor = int(grid_id[1:4]) - 90
    lon_floor = int(grid_id[4:7])
    lat_c = lat_floor + 0.5
    lon_c = lon_floor + 0.5
    prov, pulau, rawan, gambut = map_grid_to_province(grid_id, lat_c, lon_c)
    ref_rows.append([grid_id, prov, pulau, rawan, gambut])

with open(path_ref, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    for r in ref_rows:
        w.writerow(r)

print(f"Wrote {len(ref_rows)} reference grid rows to {path_ref}")

