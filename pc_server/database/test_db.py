from db_manager import init_db, insert_stats

if __name__ == "__main__":
    # Step 1: Initialize DB
    init_db()
    print("Database initialized.")

    # Step 2: Insert a test record
    insert_stats(cpu=50.0, memory=30.0, disk=20.0, battery=80.0)
    print("Test record inserted successfully!")
