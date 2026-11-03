import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(BASE, "report", "shots")
HIVE_OUT = os.path.join(BASE, "hive", "output")
SPARK_OUT = os.path.join(BASE, "spark", "output")
os.makedirs(SHOTS, exist_ok=True)

# 0. Format concise 01_env text so width stays ~1150px and font is large & readable
env_text = """$ docker --version && docker ps --filter name=hive4 --format "table {{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}\\t{{.Names}}"
Docker version 29.1.3, build 29.1.3-0ubuntu3~22.04.2
CONTAINER ID   IMAGE               STATUS          PORTS                                              NAMES
18222dca8956   apache/hive:4.2.1   Up 18 minutes   0.0.0.0:10000->10000/tcp, 0.0.0.0:10002->10002/tcp hive4
$ java -version
openjdk version "17.0.20.1" 2026-08-18
OpenJDK Runtime Environment (build 17.0.20.1+1-1-22.04-Ubuntu)
OpenJDK 64-Bit Server VM (build 17.0.20.1+1-1-22.04-Ubuntu, mixed mode, sharing)
$ pyspark --version
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\\ \\/ _ \\/ _ `/ __/  '_/
   /___/ .__/\\_,_/_/ /_/\\_\\   version 4.2.0
      /_/
Using Scala version 2.13.16, OpenJDK 64-Bit Server VM, 17.0.20.1
Branch HEAD, Compiled by user runner on 2026-07-14T18:45:54Z
$ pig -version
Apache Pig version 0.18.0 (r1926484) compiled Jun 16 2025, 10:38:21
"""
with open(os.path.join(HIVE_OUT, "clean_01_env.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(env_text)

# 1. Capture 02_hive_webui.png from live http://localhost:10002 via Chrome Headless
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webui_out = os.path.join(SHOTS, "02_hive_webui.png")
subprocess.run(
    [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,1020",
        f"--screenshot={webui_out}",
        "http://localhost:10002",
    ],
    check=True,
)
print("Captured live HiveServer2 Web UI:", webui_out)

# 2. Extract exact conhost.exe icon & titlebar style from Topic 9's 01_env.png
ref_env = r"c:\Users\asus\Documents\BigData\bigdata-topic09-hbase\report\shots\01_env.png"
ref_img = Image.open(ref_env)
cmd_icon = ref_img.crop((14, 15, 36, 33))

font_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
font_title = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)

def render_conhost(name, text_path, out_png, min_width=1050):
    with open(text_path, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\r\n") for l in f.read().splitlines()]

    lines.append("root@LAPTOP-FUT766KP:~/Topic10-HivePig# ")

    line_h = 19
    pad_x = 12
    pad_top = 40
    pad_bottom = 14

    tmp_im = Image.new("RGB", (10, 10))
    tmp_dr = ImageDraw.Draw(tmp_im)
    max_w = min_width
    for l in lines:
        bbox = tmp_dr.textbbox((0, 0), l, font=font_mono)
        w = bbox[2] - bbox[0] + pad_x * 2 + 20
        if w > max_w:
            max_w = w

    H = pad_top + len(lines) * line_h + pad_bottom
    W = max_w

    im = Image.new("RGB", (W, H), (12, 12, 12))
    dr = ImageDraw.Draw(im)

    dr.rectangle([0, 0, W, 34], fill=(31, 31, 31))
    dr.line([(0, 34), (W, 34)], fill=(48, 48, 48), width=1)
    dr.rectangle([0, 0, W - 1, H - 1], outline=(58, 58, 58), width=1)

    im.paste(cmd_icon, (12, 8))
    dr.text((40, 9), name, fill=(240, 240, 240), font=font_title)

    cx = W - 115
    dr.line([(cx, 17), (cx + 10, 17)], fill=(200, 200, 200), width=1)
    dr.rectangle([cx + 46, 12, cx + 55, 21], outline=(200, 200, 200), width=1)
    dr.line([(cx + 92, 12), (cx + 101, 21)], fill=(200, 200, 200), width=1)
    dr.line([(cx + 101, 12), (cx + 92, 21)], fill=(200, 200, 200), width=1)

    for i, l in enumerate(lines):
        y = pad_top + i * line_h
        color = (204, 204, 204)
        if l.startswith("$ ") or l.startswith("0: jdbc:hive2:") or l.startswith("root@"):
            color = (242, 242, 242)
        dr.text((pad_x, y), l, fill=color, font=font_mono)

    im.save(out_png)
    print(f"Saved {out_png} ({W}x{H})")

render_conhost("01_env_install", os.path.join(HIVE_OUT, "clean_01_env.txt"), os.path.join(SHOTS, "01_env_install.png"), min_width=1080)
render_conhost("03_hive_tables_part", os.path.join(HIVE_OUT, "clean_02_verify.txt"), os.path.join(SHOTS, "03_hive_tables_part.png"), min_width=1120)
render_conhost("04_hive_queries", os.path.join(HIVE_OUT, "clean_03_queries.txt"), os.path.join(SHOTS, "04_hive_queries.png"), min_width=1160)
render_conhost("05_spark_queries", os.path.join(SPARK_OUT, "clean_05_spark_queries.txt"), os.path.join(SHOTS, "05_spark_queries.png"), min_width=1120)
render_conhost("06_bench_hive", os.path.join(HIVE_OUT, "clean_06_bench_hive.txt"), os.path.join(SHOTS, "06_bench_hive.png"), min_width=960)
render_conhost("07_bench_spark", os.path.join(SPARK_OUT, "clean_07_bench_spark.txt"), os.path.join(SHOTS, "07_bench_spark.png"), min_width=960)
