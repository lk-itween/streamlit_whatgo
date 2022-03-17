import sqlite3
conn = sqlite3.connect('data.db',check_same_thread=False)
c = conn.cursor()


def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS t_caloriss(Ingredients TEXT, Amount_of_Ingredients TEXT , Units TEXT,Note TEXT)')


def add_data(ingredient,amount,units,note):
	c.execute('INSERT INTO t_caloriss(Ingredients, Amount_of_Ingredients, Units, Note) VALUES (?,?,?,?)',(ingredient,amount,units,note))
	conn.commit()


def view_all_data():
	c.execute('SELECT * FROM t_caloriss')
	data = c.fetchall()
	return data

def view_all_ingredients_data():
	c.execute('SELECT DISTINCT Ingredients FROM t_caloriss')
	data = c.fetchall()
	return data

def delete_data(ingredients1):
	c.execute('DELETE FROM t_caloriss WHERE Ingredients="{}"'.format(ingredients1))
	conn.commit()

def edit_info_data(new_name,new_position_status,new_email,new_entry_date,Name,Position,Email,Entry_date):
	c.execute("UPDATE t_empoyeetable SET Employee_Name =?,Position=?,Email_Address=?,Entry_date=? WHERE Employee_Name =? and Position=?and Email_Address=? and Entry_date=? ",(new_name,new_position_status,new_email,new_entry_date,Name,Position,Email,Entry_date))
	conn.commit()
	data = c.fetchall()
	return data
