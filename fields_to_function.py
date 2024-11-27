def generate_select_query(field_tuple, table_name):
    # Convert the field tuple elements to a comma-separated string
    field_list = ', '.join(field_tuple)

    # Create the SELECT query with the field list and table name
    select_query = f"SELECT {field_list} FROM {table_name}"

    return select_query

# Example usage:
field_tuple = ('name', 'age', 'city')
table_name = 'your_table_name'

# Call the function to generate the SELECT query
sql_query = generate_select_query(field_tuple, table_name)

print(sql_query)
