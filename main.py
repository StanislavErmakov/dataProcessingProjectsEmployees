from getpass import getpass
from mysql.connector import connect, Error
import pandas as pd
import numpy as np


def create_connection(db_hostport, db_user, db_password, db_name):
    try:
        connection = connect(
            host=db_hostport,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print("Подключение к базе данных Redmine прошло успешно")
        return(connection)
    except Error as e:
        print(f'Произошла ошибка "{e}"')


class Employee:
    def __init__(self, last_name, first_name):
        self._last_name = last_name
        self._first_name = first_name

    def get_last_name(self):
        return self._last_name
    
    def set_last_name(self, last_name):
        if isinstance(last_name, str) and last_name.isalpha():
            self._last_name = last_name
        else:
            raise ValueError(f'Некорректная фамилия сотрудника - {last_name}')
    last_name = property(get_last_name, set_last_name)

    def get_first_name(self):
        return self._first_name

    def set_first_name(self, first_name):
        if isinstance(first_name, str) and first_name.isalpha():
            self._first_name = first_name
        else:
            raise ValueError(f'Некорректное имя сотрудника - {first_name}')
    first_name = property(get_first_name, set_first_name)


with open("autentificationKeys.txt", "r", encoding="utf-8") as keys:
    [host, login, password, MySQLTable] = map(lambda x: x.rstrip("\n"), keys.readlines())
con = create_connection(host,login, password, MySQLTable)

#запрос для получения даты рождения сотрудника Ермакова Станислава
# query = ('SELECT value FROM custom_values WHERE custom_field_id=64 AND customized_id=167')
# cursor.execute(query)
# result = cursor.fetchall()
# for row in result:
#     print(row)



def group_id(con, group) -> int:

    """Функция получения id указанной группы сотрудников"""

    query = f"SELECT id FROM users WHERE lastname='{group}'"
    cursor = con.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if not result:
        raise ValueError("Неизвестная группа сотрудников!")
    else:
        number = result[0][0]
        return int(number)
    

print(group_id(con, "ТКЗ ИЦ СПБ"))


def employees(con, group) -> list:
    """Функция получения списка всех работающих и неработающих сотрудников"""


    def query_list_empl(status):
        return f"""SELECT u.lastname, u.firstname, u.id FROM users AS u JOIN groups_users AS gr ON u.id = gr.user_id 
    WHERE gr.group_id = {group_id(con, group)} AND u.status = {status} ORDER BY u.lastname"""

    
    cursor = con.cursor()
    query1 =  query_list_empl(1)
    cursor.execute(query1)
    working_employees = cursor.fetchall()
    query3 =  query_list_empl(3)
    cursor.execute(query3)
    not_working_employees = cursor.fetchall()
    cursor.close()
    result = working_employees + not_working_employees
    # with open("users_TKZ_IC_SPb.txt", "w") as f:
    #     for res in result:
    #         print(*res, file=f)
    return result


#print(*employees(con, "ТКЗ ИЦ СПБ"))

def custom_field_id(con, custom_field_name) -> int:
    cursor = con.cursor()
    query = f"SELECT id FROM custom_fields WHERE name='{custom_field_name}'"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if not result:
        raise ValueError("Неизвестное имя настраиваемого поля!")
    else:
        number = result[0][0]
        return int(number)

year = 2024
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

def create_data_finance_employees(employees):
    list_employees = list(map(lambda x: f'{x[0]} {x[1]}', employees))
    count_employees = len(list_employees)
    columns = ['Сотрудник']
    for month in months:
        for fin in ["Зарплата", "Премия"]:
            columns.append(f'{month} {fin}')
    finance_employees = []
    for i in range(count_employees):
        finance_employees.append([list_employees[i]])
        finance_employees[i].extend([None for _ in range(24)])
    data_finance_employees = pd.DataFrame(finance_employees, columns=columns, index=[i for i in range(1, count_employees+1)])
    return data_finance_employees


data_finance_employees = create_data_finance_employees(employees(con, "ТКЗ ИЦ СПБ"))
print(data_finance_employees)

def create_new_file_finance_employees(data_finance_employees):
    writer = pd.ExcelWriter(f'Finances employees for {year}.xlsx')
    data_finance_employees.to_excel(writer, sheet_name='Финансы сотрудников')
    writer.close()

#create_new_file_finance_employees(data_finance_employees)

def read_file_finance_employees(file):
    xl = pd.ExcelFile(file)
    data_finance_employees2 = xl.parse('Финансы сотрудников', index_col=0)
    return data_finance_employees2


print(read_file_finance_employees('Finances employees for 2024.xlsx'))

# print(custom_field_id(con, "Дата трудоустройства"))
# print(custom_field_id(con, "Ставка"))
# print(custom_field_id(con, "День рождения"))


cursor = con.cursor()
query = "SELECT value FROM custom_values WHERE custom_field_id=64 AND customized_id=167"
cursor.execute(query)
result = cursor.fetchall()
#print(result)


# просмотр затраченного времени выбранного сотрудника за выбранный промежуток времени
# query = "SELECT project_id, issue_id, hours, spent_on FROM time_entries WHERE user_id=167 and spent_on BETWEEN '2024-06-01' AND '2024-06-10'"
# cursor.execute(query)
# result = cursor.fetchall()
# with open("time_entries.txt", "w") as f:
#     for res in result:
#         print(*res, file=f)


# кусок алгоритма записывания названий столбцов и первых 5 строк данных всех таблиц БД в файлы
# cursor.execute("SHOW TABLES")
# result = cursor.fetchall()
# for row in result:
#     table = row[0]
#     with open(f'./Tables/{table}.txt', 'w', encoding='utf-8') as f:
#         query = f'show columns from {table}'
#         cursor.execute(query)
#         columns = cursor.fetchall()
#         for col in columns:
#             print(f'{col[0]}', end=" ", file=f)
#         print("\n", file=f)
#         query = f'SELECT * FROM {table} LIMIT 5'
#         cursor.execute(query)
#         data = cursor.fetchall()
#         for d in data:
#             print(*d, file=f)
#             print("\n", file=f)


# query = 'show columns from groups_users'
# query = ('SELECT * FROM custom_fields')
# cursor.execute(query)
# result = cursor.fetchall()
# for i in result:
#     print(i)


# cursor.execute("SHOW columns FROM custom_fields")
# with open('COLUMNS custom_fields.txt', 'w', encoding='utf-8') as f:
#     for row in cursor.fetchall():
#         print(row[0])
#         print(f'{row[0]}\n', file=f)


# query = ('SELECT * FROM custom_fields')
# cursor.execute(query)
# result = cursor.fetchall()
# for row in result:
#     print(row)


#запрос для получения даты рождения сотрудника Ермакова Станислава
# query = ('SELECT value FROM custom_values WHERE custom_field_id=64 AND customized_id=167')
# cursor.execute(query)
# result = cursor.fetchall()
# print(result)
# for row in result:
#     print(row)


# query = ('SELECT * FROM easy_alerts')
# cursor.execute(query)
# result = cursor.fetchall()
# for row in result:
#     print(row)


# cursor.execute("SHOW TABLES") # execute 'SHOW TABLES' (but data is not returned)
# easy_tables = cursor.fetchall()
# for table in easy_tables:
#     name_table = table[0]
#     query = (f'SELECT * FROM {name_table}')
#     cursor.execute(query)
#     result = cursor.fetchall()
#     for row in result:
#         if 'ТКЗ ИЦ СПБ' in row:
#             print(f'{name_table} - {row}')


# query = ('SELECT * FROM information_schema.columns WHERE table_name="users"')
# cursor.execute(query)
# result = cursor.fetchall()
# print(result)

print("Все операции завершены успешно")
cursor.close()
con.close()
