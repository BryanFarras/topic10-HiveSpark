$ErrorActionPreference = "Stop"
$D = (Resolve-Path "$PSScriptRoot\..").Path
$W = (wsl -d Ubuntu-22.04 wslpath -a ($D -replace '\\','/')).Trim()

# 1. 01_env_install.png
& "$PSScriptRoot\cap.ps1" -Name "01_env_install" -Bash "cat $W/hive/output/clean_01_env.txt" -Cols 145 -Lines 24

# 2. 02_hive_webui.png via Chrome headless
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --headless --disable-gpu --window-size=1280,1020 --screenshot="$D\report\shots\02_hive_webui.png" "http://localhost:10002"
Write-Host "saved 02_hive_webui.png"

# 3. 03_hive_tables_part.png
& "$PSScriptRoot\cap.ps1" -Name "03_hive_tables_part" -Bash "cat $W/hive/output/clean_02_verify.txt" -Cols 145 -Lines 42

# 4. 04_hive_queries.png
& "$PSScriptRoot\cap.ps1" -Name "04_hive_queries" -Bash "cat $W/hive/output/clean_03_queries.txt" -Cols 155 -Lines 48

# 5. 05_spark_queries.png
& "$PSScriptRoot\cap.ps1" -Name "05_spark_queries" -Bash "cat $W/spark/output/clean_05_spark_queries.txt" -Cols 145 -Lines 48

# 6. 06_bench_hive.png
& "$PSScriptRoot\cap.ps1" -Name "06_bench_hive" -Bash "cat $W/hive/output/clean_06_bench_hive.txt" -Cols 115 -Lines 28

# 7. 07_bench_spark.png
& "$PSScriptRoot\cap.ps1" -Name "07_bench_spark" -Bash "cat $W/spark/output/clean_07_bench_spark.txt" -Cols 115 -Lines 28
