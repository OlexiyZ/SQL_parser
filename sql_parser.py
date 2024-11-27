# v11 - в функции extract_columns() добавляется парсиг столбцов с функциями - запятіми и кругліми скобками
import re
import json

sql = """
SELECT  
  kl.lookup_label as Business_Line,
  NVL(A1.field1, 0) AS qqq,
  A1.field2
FROM 
  (SELECT field1, field2 FROM business) A1,
  kyc_customer kc
  INNER JOIN kyc_customer_person kcp on kcp.customer_id = kc.id 
  INNER JOIN kyc_person_work_info kwi on kcp.person_id = kwi.kyc_person_id
  INNER JOIN kyc_lookup kl on kl.lookup_value = kwi.business_line
WHERE
  lookup_type = 'Business Line';
"""

query_counter = 0  # Счетчик для генерации уникальных имен запросов


def find_select_from_where(sql):
    global query_counter
    sql = query_cleaning(sql)
    # tokens = list(re.finditer(r"(SELECT|FROM|WHERE|;|\(|\))", sql, re.IGNORECASE))
    # tokens = list(re.finditer(r"(SELECT|FROM|WHERE|;)", sql, re.IGNORECASE))
    # tokens = list(re.finditer(r"(\bSELECT\b|\bFROM\b|\bWHERE\b|;)", sql, re.IGNORECASE))
    tokens = list(re.finditer(r"(\bSELECT\b|\bFROM\b|\bWHERE\b|;|\(\s*SELECT|\(|\))", sql, re.IGNORECASE))

    stack = []  # Стек для отслеживания вложенных SELECT
    queries = []  # Список найденных SELECT-FROM-WHERE конструкций
    current_query = None
    parentheses = False

    for match in tokens:
        keyword = match.group().upper()
        position = match.start()

        if keyword == "SELECT" or re.sub(r"[\s]+", "", keyword) == "(SELECT":
            if current_query:
                stack.append(current_query)
            query_counter += 1
            current_query = {
                "name": f"Query_{query_counter}",
                "SELECT": position,
                "FROM": None,
                "WHERE": None,
                "columns": [],
                "sources": [],
                "nested": []
            }

        elif keyword == "FROM":
            if current_query is None or (current_query is not None and current_query["FROM"] is None):   # current_query and current_query["FROM"] is None
                current_query["FROM"] = position
                # Извлечение столбцов
                select_text = sql[current_query["SELECT"]:position].strip()
                columns = extract_columns(select_text)
                current_query["columns"] = columns

                # Извлечение источников
                from_text = extract_from(sql, position)
                sources = parse_sources(from_text)
                current_query["sources"] = sources

        elif keyword == "WHERE":
            if current_query and current_query["WHERE"] is None:
                current_query["WHERE"] = position

        # elif re.sub(r"[\s]+", "", keyword) == "(SELECT":
        #     if current_query:
        #         stack.append(current_query)
        #         current_query = None

        elif keyword == "(":
            parentheses = True
            # if current_query:
            #     stack.append(current_query)
            #     current_query = None

        elif keyword == ")":
            if current_query and not parentheses:
                if stack:
                    parent_query = stack.pop()
                    parent_query["nested"].append(current_query)
                    current_query = parent_query
                else:
                    queries.append(current_query)
                    current_query = None
            else:
                parentheses = False

        elif keyword == ";":
            if current_query:
                # Обработка незавершенного SELECT, если FROM не найден
                if current_query["FROM"] is None:
                    select_text = sql[current_query["SELECT"]:position].strip()
                    current_query["columns"] = extract_columns(select_text)
                queries.append(current_query)
                current_query = None

    # Если остались незакрытые запросы
    if current_query:
        queries.append(current_query)

    return queries


def query_cleaning(sql_text):
    """
    Removes single-line and multi-line comments from SQL text.
    """
    # Remove multi-line comments (/* ... */)
    sql_text = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.DOTALL)
    # Remove single-line comments (-- ...)
    sql_text = re.sub(r"--.*?$", "", sql_text, flags=re.MULTILINE)
    # Remove extra whitespace and return cleaned SQL
    sql_text = sql_text.strip()

    return sql_text.replace(" .", ".")


def extract_columns(select_text):
    """
    Extracts column names, aliases, and source aliases from a SELECT clause.
    Handles functions with parentheses and commas.
    """
    select_text = re.sub(r"(?i)(\bSELECT\b|\(\s*SELECT)", "", select_text, count=1).strip()
    columns = []

    # Split columns by commas, ignoring commas inside parentheses
    def split_columns(text):
        result = []
        current = []
        open_parentheses = 0

        for char in text:
            if char == ',' and open_parentheses == 0:
                result.append(''.join(current).strip())
                current = []
            else:
                if char == '(':
                    open_parentheses += 1
                elif char == ')':
                    open_parentheses -= 1
                current.append(char)
        # Add the last column
        if current:
            result.append(''.join(current).strip())
        return result

    # Define column types
    def define_column_type(column_name, alias, source_alias):
        if re.search(r"(\bSELECT\b|\(\s*SELECT)", column_name.strip(), re.IGNORECASE):
            return {
                        "field_alias": alias.strip() if alias else None,
                        "field_source_type": "data_source",
                        "field_source": source_alias.strip() if source_alias else None,
                        "field_name": column_name.strip() if column_name else None,
                        "field_value": None,
                        "field_function": None,
                        "function_field_list": None
                    }
        elif '(' in column_name.strip() and ')' in column_name.strip():
            return {
                        "field_alias": alias.strip() if alias else None,
                        "field_source_type": "function",
                        "field_source": source_alias.strip() if source_alias else None,
                        "field_name": None,
                        "field_value": None,
                        "field_function": column_name.strip() if column_name else None,
                        "function_field_list": column_name.strip() if column_name else None,
                    }
        elif column_name.strip().replace('.', '').isdigit() or column_name.strip().upper() == 'NULL' \
                or "'" in column_name.strip() or '"' in column_name.strip():  #  or ('(' not in column_name.strip() and ')' not in column_name.strip())
            return {
                        "field_alias": alias.strip() if alias else None,
                        "field_source_type": "value",
                        "field_source": source_alias.strip() if source_alias else None,
                        "field_name": None,
                        "field_value": column_name.strip() if column_name else None,
                        "field_function": None,
                        "function_field_list": None
                    }
        else:
            return {
                        "field_alias": alias.strip() if alias else None,
                        "field_source_type": "data_source",
                        "field_source": source_alias.strip() if source_alias else None,
                        "field_name": column_name.strip() if column_name else None,
                        "field_value": None,
                        "field_function": None,
                        "function_field_list": None
                    }

    # Split the SELECT text into individual column definitions
    column_definitions = split_columns(select_text)

    # Process each column definition
    for col in column_definitions:
        # Match column expressions with optional alias
        # match_function = re.match(r"(.+?)\s+(?:AS\s+)?(\w+)$", col, re.IGNORECASE)
        match_function = re.match(r"(.+)\s+AS\s+(\w+)$", col.strip(), flags=re.DOTALL | re.IGNORECASE)
        if match_function:
            column_expr = match_function.group(1).strip()
            alias = match_function.group(2)
            # column_expr, alias = match_function.groups()
            # Check for source alias in column expression
            match_source_alias = re.match(r"(?:(\w+)\.)?(.+)", column_expr.strip(), re.DOTALL)
            if match_source_alias:
                source_alias, column_name = match_source_alias.groups()
                column_object = define_column_type(column_name, alias, source_alias)
                columns.append(column_object)
        else:
            # Simple expression without alias
            match_simple = re.match(r"(?:(\w+)\.)?(.+)", col)
            if match_simple:
                alias = None
                source_alias, column_name = match_simple.groups()
                column_object = define_column_type(column_name, alias, source_alias)
                columns.append(column_object)

    return columns


def extract_from(sql, from_position):
    """
    Извлечение текста после FROM.
    """
    # stack_from = []
    parentheses_from = False
    # current_from = None


    from_text = sql[from_position:]
    # stop_match = re.search(r"(\bWHERE\b|;|\(|\))", from_text, re.IGNORECASE)
    stop_match = list(re.finditer(r"(\bWHERE\b|;|\(|\))", from_text, re.IGNORECASE))

    for match in stop_match:
        keyword = match.group().upper()
        # position = match.start()

        if keyword == "(":
            parentheses_from = True

        elif keyword == ")" and not parentheses_from or keyword in ("WHERE", ";"):
            from_text = from_text[:match.start()]
            # from_text = re.sub(r"(?i)(\bFROM\b)", "", from_text).strip()
            return from_text.strip()
            # if current_from and not parentheses_from:
            #     if stack_from:
            #         parent_from = stack.pop()
            #         parent_from["nested"].append(current_from)
            #         current_from = parent_from
            #     else:
            #         # queries.append(current_query)
            #         current_from = None
        else:
            parentheses_from = False

    # if stop_match:
    #     from_text = from_text[:stop_match.start()]
    # return from_text.strip()


def parse_sources(from_text):
    """
    Извлечение источников данных и их алиасов, включая подзапросы.
    """
    from_text = re.sub(r"(?i)\bFROM\b", "", from_text).strip()
    sources = []
    for source in from_text.split(","):
        source = source.strip()
        # Подзапросы с алиасами
        match_subquery = re.match(r"\((SELECT.+)\)\s+(?:AS\s+)?(\w+)$", source, re.IGNORECASE)
        if match_subquery:
            subquery, alias = match_subquery.groups()
            sources.append({"table": subquery.strip(), "alias": alias})
        else:
            # Простые таблицы с алиасами
            # match = re.match(r"(\w+)(?:\s+AS\s+|\s+)(\w+)$", source, re.IGNORECASE)
            match = re.match(r"(?:(\w+)\.)?(\w+)(?:\s+(\w+))?", source, re.IGNORECASE)
            if match:
                schema = match.group(1)  # Название схемы
                table = match.group(2)  # Название таблицы
                alias = match.group(3)   # Алиас
                sources.append({
                    "field_alias": alias.strip() if alias else None,
                    "source_type": "table",
                    "source_name": table.strip() if table else None,
                    "source_scheme": schema.strip() if schema else None,
                    "source_system": None,
                    "union_type": None,
                    "union_condition": None,
                    "source_description": None
                })
            # else:
            #     # Если алиас не найден
            #     sources.append({"table": source, "alias": None})
    return sources


def queries_to_json(queries):
    def format_query(query):
        return {
            "name": query["name"],
            "SELECT": query["SELECT"],
            "FROM": query["FROM"],
            "WHERE": query["WHERE"],
            "columns": query["columns"],
            "sources": query["sources"],
            "nested": [format_query(nested_query) for nested_query in query["nested"]],
        }
    return [format_query(query) for query in queries]


# Основная программа
try:
    with open("query2.sql", "r", encoding="utf-8") as file:
        sql = file.read()
except FileNotFoundError:
    print("File not found!")
except IOError:
    print("Error reading the file!")

result = find_select_from_where(sql)

# Преобразование результата в JSON
if result:
    # json_result = json.dumps(queries_to_json(result), indent=4)
    # print("Nested Queries in JSON Format:")
    # print(json_result)

    # Запись JSON в файл
    with open("nested_queries.json", "w", encoding="utf-8") as json_file:
        json.dump(queries_to_json(result), json_file, indent=4, ensure_ascii=False)
    print("\nJSON записан в файл nested_queries.json.")
else:
    print("\nNo queries found.")