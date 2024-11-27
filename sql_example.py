# pass1 = input('Введіть пароль від 8 до 20 символів :')
# if len(pass1) < 8 or len(pass1) > 20:
#     print('Пароль неправильної довжии')
# else:
#     print('Пароль правильний')

# pass1 = input('Введіть пароль від 8 до 20 символів :')
# if 8 < len(pass1) < 20:
#     print('Пароль неправильної довжии')
# else:
#     print('Пароль правильний')

# sum1 = 0
# str1 = input('Введіть числа через кому :')
# str2 = str1.split(',')
# for i in str2:
#     sum1 += int(i)
# print(sum1)

# m = 0
# s = ''
# str1 = input('Введіть числа через кому :')
# for i in str1:
#     if m < str1.count(i):
#         s=str(i)
#         m = str1.count(i)
# print(m)

# str1 = 'hello world'
# print(str1[::-1]) # поввертає зворотній рядок

# import collections

# User = collections.namedtuple('User', ('username', 'password', 'email'))
# user1 = User('Olexiy', '20958sd', 'al@mail.com')
# print(user1.username)
# print(user1.password)
# print(user1.email)

# import collections

# User = collections.namedtuple('User', ('username', 'password', 'email'))
# user1 = User('Olexiy', '20958sd', 'al@mail.com')
# print(user1.username)
# print(user1.password)
# print(user1.email)

import sqlparse

sql = """
    SELECT
  kl.lookup_label as Business_Line
  (SELECT field1 FROM business) AS qqq,
  field1.A1
FROM
  (SELECT field1 FROM business) A1,
  kyc_customer kc
  INNER JOIN kyc_customer_person kcp on kcp.customer_id = kc.id 
  INNER JOIN kyc_person_work_info kwi on kcp.person_id = kwi.kyc_person_id
  INNER JOIN kyc_lookup kl on kl.lookup_value = kwi.business_line
WHERE
  lookup_type = 'Business Line';"""

# print(sqlstring)

# encod = sqlparse.parse(sqlstring)
# print(encod)

# print(sqlparse.format(sql, reindent=True, keyword_case='upper'))

position = sql.find("SELECT")
if position != -1:
    print(f"Found at {position}")


parsed = sqlparse.parse(sql.strip())
stmt = parsed[0]

print(stmt)

print(stmt.tokens)

# print(str(stmt.tokens[-1]))

for token in stmt.tokens:
    print(token)
