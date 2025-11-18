# inspect_db.py
import sqlite3, pandas as pd, os
DB = os.path.join(os.path.dirname(__file__), "usage_log.db")
print("Using DB:", DB)
conn = sqlite3.connect(DB)
df = pd.read_sql_query("SELECT * FROM usage_log", conn, parse_dates=["timestamp"])
conn.close()

print("Total rows in table:", len(df))
print("Head:\n", df.head(5))
print("Tail:\n", df.tail(5))

# timestamp info
if "timestamp" in df.columns:
    print("Timestamp dtype:", df["timestamp"].dtype)
    print("Min timestamp:", df["timestamp"].min())
    print("Max timestamp:", df["timestamp"].max())
    # show counts per second/minute
    df_sorted = df.sort_values("timestamp").set_index("timestamp")
    print("Counts per 1s:", df_sorted.resample("1S").size().describe())
    print("Counts per 15s:", df_sorted.resample("15S").size().describe())
else:
    print("No timestamp column found or parse failed.")
