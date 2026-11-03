#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DIR/output"

# Create a helper inside hive4 container: /tmp/exec_sql.sh <sql_file>
docker exec -u root hive4 bash -c 'cat << "EOF" > /tmp/exec_sql.sh
#!/usr/bin/env bash
set -e
SQL_FILE="$1"
SQL_STR=$(grep -v "^[[:space:]]*--" "$SQL_FILE" | tr "\r\n" "  ")
export HADOOP_CLIENT_OPTS="$HADOOP_CLIENT_OPTS --enable-preview --enable-native-access=ALL-UNNAMED"
script -q -c "beeline -u jdbc:hive2://localhost:10000 -e \"$SQL_STR\"" /dev/null
EOF
chmod +x /tmp/exec_sql.sh'

echo "=== [1/4] Creating database & loading tables (01_create_load.sql) ==="
docker cp "$DIR/01_create_load.sql" hive4:/tmp/01_create_load.sql
docker exec hive4 /tmp/exec_sql.sh /tmp/01_create_load.sql > "$DIR/output/01_create_load.out" 2>&1
tail -n 25 "$DIR/output/01_create_load.out"

echo "=== [2/4] Verifying tables & partitions (02_verify_tables.sql) ==="
docker cp "$DIR/02_verify_tables.sql" hive4:/tmp/02_verify_tables.sql
docker exec hive4 /tmp/exec_sql.sh /tmp/02_verify_tables.sql > "$DIR/output/02_verify_tables.out" 2>&1
grep -E "^\+|^\||rows? selected" "$DIR/output/02_verify_tables.out" || cat "$DIR/output/02_verify_tables.out"

echo "=== [3/4] Running 3 demo queries (03_queries_demo.sql) ==="
docker cp "$DIR/03_queries_demo.sql" hive4:/tmp/03_queries_demo.sql
docker exec hive4 /tmp/exec_sql.sh /tmp/03_queries_demo.sql > "$DIR/output/03_queries_demo.out" 2>&1
grep -E "^\+|^\||rows? selected" "$DIR/output/03_queries_demo.out" || cat "$DIR/output/03_queries_demo.out"

echo "=== [4/4] Running 3x Benchmark across 1x & 10x (Text, Parquet, Partitioned) ==="
python3 "$DIR/benchmark_hive.py"
