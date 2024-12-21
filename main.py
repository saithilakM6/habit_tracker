#import necessary libraries
import streamlit as st
import pandas as pd
import datetime
from logic_habitTracker import load_user_habits, add_habit, create_connection
import sqlite3

# Initialize database connection
def create_connection():
    conn = sqlite3.connect('habit_tracker.db')
    return conn

# User authentication functions
def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def load_user_habits(user_id):
    conn = create_connection()
    query = "SELECT * FROM habits WHERE user_id=?"
    habits = pd.read_sql(query, conn, params=(user_id,))
    conn.close()
    
    # Ensure that 'date' is in datetime format
    if 'date' in habits.columns:
        habits['date'] = pd.to_datetime(habits['date'], errors='coerce')  # Convert to datetime and coerce errors
        habits['date'] = habits['date'].dt.date  # Extract date from datetime object
        
    return habits

def add_habit(user_id, habit_name, notes):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (user_id, name, date, status, notes) VALUES (?, ?, ?, ?, ?)",
                   (user_id, habit_name, datetime.datetime.now(), 'pending', notes))
    conn.commit()
    conn.close()

# Create tables if they do not exist
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Habits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

# User authentication functions
def register_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user
# User authentication interface
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'habits_data' not in st.session_state:
    st.session_state.habits_data = pd.DataFrame(columns=["id","user_id","name","date","status","notes"])

st.title("Welcome to login page")
auth_option = st.radio("Select an option:",["Login","Register"])
if auth_option == "Register":
    username = st.text_input("Username")
    password = st.text_input("Password",type='password')
    if st.button("Register"):
        if register_user(username,password):
            st.success("User registered successfully!")
        else:
            st.error("Username already exists!")
elif auth_option == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password",type='password')
    if st.button("Login"):
        user = login_user(username,password)
        if user:
            st.session_state.user_id = user[0] 
            st.session_state.username = username  
            st.session_state.logged_in = True 
            st.success(f"Welcome back,{username}!")

      # loading the habits that are entered by the user
            st.session_state.habits_data = load_user_habits(st.session_state.user_id)
        else:
            st.error("invalid username or password, or please try register")
        
# main app logic
if st.session_state.logged_in:
    st.title("Habit Tracker")
    menu = st.sidebar.radio("Menu",["Add Habit","Log Habit","View Habits","Visualize Habits"])

                     # Adding  New Habit
    if menu == "Add Habit":
        st.subheader("Add a New Habit")
        new_habit = st.text_input("Enter the name of the habit:")
        notes = st.text_area("Add notes about this habit (optional):")
        if st.button("Add Habit"):
            if new_habit:
                add_habit(st.session_state.user_id,new_habit, notes)
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
                st.success(f"Successfully added habit:{new_habit}")
            else:
                st.error("Habit name is empty")

     # Logging Habit<
    elif menu == "Log Habit":
        st.subheader("Log Your Habit Progress")
        
        if st.session_state.habits_data.empty:
            st.warning("No habits added yet.Add a habit first")
        else:
            habit_names = st.session_state.habits_data["name"].unique()
            selected_habit = st.selectbox("Select a habit to log:",habit_names)
            log_status = st.radio("Status:",["completed","skipped"],horizontal=True)
            if st.button("Log Progress"):
                today = datetime.datetime.now().date()
                existing_entry = st.session_state.habits_data[
                    (st.session_state.habits_data["name"] == selected_habit) &
                    (st.session_state.habits_data["date"].dt.date == today)
                ]
                conn = create_connection()
                cursor = conn.cursor()
                if not existing_entry.empty:
        # Updating
                    cursor.execute(
                        "UPDATE habits SET status = ? WHERE user_id = ? AND name = ? AND date = ?",
                        (log_status, st.session_state.user_id,selected_habit,existing_entry.iloc[0]['date'].to_pydatetime())
                    )
                    st.success(f"Updated progress for'{selected_habit}' to '{log_status}'.")
                else:
        # Creating new entry
                    cursor.execute(
                        "INSERT INTO habits(user_id, name, date, status)VALUES(?, ?, ?, ?)",
                        (st.session_state.user_id,selected_habit,datetime.datetime.now(),log_status)
                    )
                    st.success(f"Logged progress for '{selected_habit}' as '{log_status}'.")
                conn.commit()
                conn.close()
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
    #  View Habits
    elif menu == "View Habits":
        st.subheader("📋 Habit Logs")
        if st.session_state.habits_data.empty:
            st.info("No habit data available.")
        else:
            st.write(st.session_state.habits_data.sort_values(by="date", ascending=False))