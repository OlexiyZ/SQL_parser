import psycopg2

# Connect to the database
conn = psycopg2.connect(
    dbname="your_dbname", 
    user="your_username", 
    password="your_password", 
    host="your_host"
)

# Create a cursor object
cur = conn.cursor()

# Execute a query
cur.execute("SELECT * FROM your_table_name")

# Fetch the column names
column_names = [desc[0] for desc in cur.description]

# Fetch all rows
rows = cur.fetchall()

# Print column names and rows
print("Column names:", column_names)
for row in rows:
    print(row)

# Close the cursor and the connection
cur.close()
conn.close()
