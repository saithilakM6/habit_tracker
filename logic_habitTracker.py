import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import datetime
def create_connection():
    conn = sqlite3.conn('habit_tracker.db')
    return conn
#loading habits of a user
def load_user_habits(user_id):
    conn=create_connection()
    query="SELECT*FROM habits WHERE user_id=?"
    habits=pd.read_sql(query,conn,params=(user_id,))
    conn.close()
    if "date" in habits.coloumns:
        habits["date"]=pd.to_datetime(habits["date"],errors="coerce")
        return habits
    

#adding of habits
def add_habit(user_id,habit_name,notes):
    conn = create_connection()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO habits(user_id,name,date,status,notes)VALUES(?,?,?,?,?)",(user_id,habit_name,datetime.datetime.now(),'started',notes))
    conn.commit()
    conn.close()

#loggig of habits or editing the progress of habit
def log_habit_progress(user_id,habit_name,status):
    conn = create_connection()
    cursor = conn.cursor()
    current_time=datetime.datetime.now()
    cursor.execute("INSERT INTO habits (user_id,name,date,status) VALUES (?,?,?,?)",(user_id,habit_name,current_time,status))
    conn.commit()
    conn.close()