import psycopg2
from psycopg2.extras import DictCursor

# Connect to the database
conn = psycopg2.connect(
    dbname="your_dbname", 
    user="your_username", 
    password="your_password", 
    host="your_host"
)

# Create a cursor object with DictCursor
cur = conn.cursor(cursor_factory=DictCursor)

# Execute a query
cur.execute("SELECT * FROM your_table_name")

# Fetch all rows as dictionaries
rows = cur.fetchall()

# Process and print each row
for row in rows:
    print(dict(row))

# Close the cursor and connection
cur.close()
conn.close()
