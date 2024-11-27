# 1. Install psycopg2:
# pip install psycopg2

# 2. Import the necessary modules:
import psycopg2
# from psycopg2 import sql

vendor_data = [
    {"vendor_id": 1, "vendor_name": "Vendor A"},
    {"vendor_id": 2, "vendor_name": "Vendor B"},
    {"vendor_id": 3, "vendor_name": "Vendor C"}
]

# 3. Establish a connection to the PostgreSQL database:
dbname = "techsvit"
user = "postgres"
password = "postgres"
host = "localhost"
port = "5432"  # Default is usually 5432

try:
    connection = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cursor = connection.cursor()
    print("Connected to the database")
except Exception as e:
    print(f"Error: {e}")

# 4. Execute SQL queries:
try:
    for vendor in vendor_data:
        cursor.execute(
            """INSERT INTO vdm.erc_vendors (vendor_id, vendor_name) 
            VALUES (%s, %s)""",
            (vendor['vendor_id'], vendor['vendor_name'])
        )
    connection.commit()
    print("Data inserted successfully")
except Exception as e:
    print(f"Error inserting data: {e}")


# try:
#     query = "SELECT * FROM your_table_name"
#     cur.execute(query)
#     rows = cur.fetchall()
#     for row in rows:
#         print(row)
# except Exception as e:
#     print(f"Error executing query: {e}")


# 5. Close the cursor and the database connection when you're done:
cursor.close()
connection.close()