import sqlite3

conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()


def create_table():
	c.execute('CREATE TABLE IF NOT EXISTS t_caloriss(Session_ID TEXT, Ingredients TEXT, Amount_of_Ingredients TEXT, Units TEXT, Note TEXT)')


def add_data(session_id, ingredient,amount,units,note):
	c.execute('INSERT INTO t_caloriss(Session_ID, Ingredients, Amount_of_Ingredients, Units, Note) VALUES (?,?,?,?)',(session_id, ingredient,amount,units,note))
	conn.commit()


def view_all_data(session_id):
	c.execute(f'SELECT * FROM t_caloriss WHERE Session_ID="{session_id}"')
	data = c.fetchall()
	return data

def view_all_ingredients_data(session_id):
	c.execute(f'SELECT DISTINCT Ingredients FROM t_caloriss WHERE Session_ID="{session_id}"')
	data = c.fetchall()
	return data

def delete_data(session_id, ingredients):
	c.execute(f'DELETE FROM t_caloriss WHERE Ingredients="{ingredients}" AND Session_ID="{session_id}"')
	conn.commit()
