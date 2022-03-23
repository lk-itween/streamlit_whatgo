import sqlite3
conn = sqlite3.connect('data.db',check_same_thread=False)
c = conn.cursor()


###############
def create_user_table():
    c.execute('CREATE TABLE IF NOT EXISTS user_table(User_ID TEXT UNIQUE, Password TEXT);')
    conn.commit()

def create_employee_table(user_id):
    c.execute(f'CREATE TABLE IF NOT EXISTS employee_table_{user_id}(Employee_Name TEXT,Position TEXT,Email_Address TEXT,Entry_date DATE);')
    conn.commit()
    return f'employee_table_{user_id}'
    
def select_pwd(user_id):
    c.execute(f'SELECT Password FROM user_table WHERE User_ID={user_id};')
    data = c.fetchall()
    return data

def verify_pwd(user_id, pwd):
    user_pwd = select_pwd(user_id)
    if not user_pwd:
        return None
    user_pwd = user_pwd[0][0]
    if pwd == user_pwd:
        return True
    else:
        return False

def delete_userdata(user_id):
    c.execute(f'DELETE FROM user_table WHERE User_ID="{user_id}";')
    conn.commit()
    
def add_userdata(user_id, pwd):
    if select_pwd(user_id):
        return 'User already exists!'
    c.execute(f'INSERT INTO user_table (User_ID, Password) VALUES ("{user_id}", "{pwd}");')
    employee_table_name = create_employee_table(user_id)
    conn.commit()
    return employee_table_name

def view_all_data(table_name):
    c.execute(f'SELECT * FROM {table_name};')
    data = c.fetchall()
    return data

def view_all_employee_info(table_name):
    c.execute(f'SELECT DISTINCT Employee_Name FROM {table_name};')
    data = c.fetchall()
    return data

def add_employee(table_name, Name,Positions,Email,Entry_date):
    c.execute(f'INSERT INTO {table_name}(Employee_Name,Position,Email_Address,Entry_date) VALUES ("{Name}","{Positions}","{Email}","{Entry_date}");')
    conn.commit()

def edit_info_data(table_name, old_name, Position, Email_Address, Entry_date):
    c.execute(f'UPDATE {table_name} SET Position="{Position}", Email_Address="{Email_Address}", Entry_date="{Entry_date}" WHERE Employee_Name="{old_name}";')
    conn.commit()
    return data
              
def delete_data(table_name, employee_name):
    c.execute(f'DELETE FROM {table_name} WHERE Employee_Name="{employee_name}";')
    conn.commit()

def get_email(table_name, employee_name):
    c.execute(f'SELECT Email_Address FROM {table_name} WHERE Employee_Name="{employee_name}";')
    data = c.fetchall()
    return data 
    
def view_position(table_name, position):
    c.execute(f'SELECT Email_Address FROM {table_name} WHERE Position="{position}";')
    data = c.fetchall()
    return data