import sqlite3
import json

json_data = '{"key": "value", "age": 25}'
data = json.loads(json_data)

field_tuple = ('name', 'age', 'city')
print(type(field_tuple))
field_list = ', '.join(field_tuple)

table_name = "your_table_name"
columns = ", ".join(data.keys())
values = ", ".join(f"'{value}'" for value in data.values())

insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"


connection = sqlite3.connect("your_database.db")
cursor = connection.cursor()

cursor.execute(insert_query)
connection.commit()
connection.close()
