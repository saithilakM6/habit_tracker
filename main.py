import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sqlite3

# Initialize database connection
def create_connection():
    conn = sqlite3.connect('habit_tracker.db')
    return conn

# User authentication functions
def register_user(username,password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(username, password)VALUES(?, ?)",(username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
def login_user(username,password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT *FROM users WHERE username=?AND password=?",(username, password))
    user = cursor.fetchone()
    conn.close()
    return user
def load_user_habits(user_id):
    conn = create_connection()
    query = "SELECT * FROM habits WHERE user_id=?"
    habits = pd.read_sql(query,conn,params=(user_id,))
    conn.close()
    if 'date' in habits.columns:
        habits['date'] = pd.to_datetime(habits['date'], errors='coerce')  # Convert to datetime and coerce errors
        
    return habits
def add_habit(user_id, habit_name, notes):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (user_id, name, date, status, notes) VALUES (?, ?, ?, ?, ?)",
                   (user_id, habit_name, datetime.datetime.now(), 'Started', notes))
    conn.commit()
    conn.close()
   # Creating tables if they do not exist
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Creating Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Creating Habits table
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
# Set up the Streamlit
st.set_page_config(page_title="Habit Tracker",layout="centered")
st.title("Welcome to login page")

# User authentication interface
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'habits_data' not in st.session_state:
    st.session_state.habits_data = pd.DataFrame(columns=["id","user_id","name","date","status","notes"])
st.header("User Authentication")
auth_option = st.radio("Select an option:", ["Login","Register"])
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
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        user = login_user(username,password)
        if user:
            st.session_state.user_id = user[0]
            st.session_state.username = username 
            st.session_state.logged_in = True
            st.success(f"Welcome back,{username}!")
            st.session_state.habits_data = load_user_habits(st.session_state.user_id)
        else:
            st.error("Invalid username or password.")

    # Main application logic 
if st.session_state.logged_in:
    menu = st.sidebar.radio("Menu", ["Add Habit", "Log Habit", "View Habits", "Visualize Habits","Dashboard"])
    
    #Adding habit
    if menu == "Add Habit":
        st.subheader("Add a New Habit")
        new_habit = st.text_input("Enter the name of the habit:")
        notes = st.text_area("Add notes about this habit (optional):")
        
        if st.button("Add Habit"):
            if new_habit:
                add_habit(st.session_state.user_id, new_habit, notes)
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
                st.success(f"Successfully added habit: {new_habit}")
            else:
                st.error("Habit name cannot be empty!")
    # Logging habit
    elif menu == "Log Habit":
        st.subheader("Log Your Habit Progress")
        if st.session_state.habits_data.empty:
            st.warning("No habits added yet.Add a habit first!")
        else:
            habit_names = st.session_state.habits_data["name"].unique()
            selected_habit = st.selectbox("Select a habit to log:",habit_names)
            log_status = st.radio("Status:", ["completed","inprogress","skipped"],horizontal=True)
            if st.button("Log Progress"):
                today = datetime.datetime.now().date()
                existing_entry = st.session_state.habits_data[
                    (st.session_state.habits_data["name"] == selected_habit) &
                    (st.session_state.habits_data["date"].dt.date == today)
                ]
                conn = create_connection()
                cursor = conn.cursor()
                if not existing_entry.empty:
         # Update existing entry
                    cursor.execute(
                        "UPDATE habits SET status = ? WHERE user_id = ? AND name = ? AND date = ?",
                        (log_status, st.session_state.user_id, selected_habit, existing_entry.iloc[0]['date'].to_pydatetime())
                    )
                    st.success(f"Updated progress for '{selected_habit}' to '{log_status}'.")
                else:
                    cursor.execute(
                        "INSERT INTO habits (user_id, name, date, status) VALUES (?, ?, ?, ?)",
                        (st.session_state.user_id, selected_habit, datetime.datetime.now(), log_status)  # Use datetime.now() here
                    )
                    st.success(f"Logged progress for '{selected_habit}' as '{log_status}'.")
                conn.commit()
                conn.close()
                st.session_state.habits_data = load_user_habits(st.session_state.user_id)
    # Viewing habit
    elif menu == "View Habits":
        st.subheader("Habit Logs")
        if st.session_state.habits_data.empty:
            st.info("No habit data available.")
        else:
            st.write(st.session_state.habits_data.sort_values(by="date", ascending=False))
        #Visualize Habits
    elif menu == "Visualize Habits":
        st.subheader("Visualize Your Habit Progress")
        if st.session_state.habits_data.empty:
            st.info("No habit data available for visualization.")
        else:
            habit_names = st.session_state.habits_data["name"].unique()
            selected_habit = st.selectbox("select a habit to visualize:",habit_names)
            # Check if date column is in datetime format
            if pd.api.types.is_datetime64_any_dtype(st.session_state.habits_data['date']):
                start_date = st.date_input("Start Date", value=st.session_state.habits_data["date"].min().date())
                end_date = st.date_input("End Date", value=st.session_state.habits_data["date"].max().date())

                # Filter data for the selected habit and date range
                filtered_data = st.session_state.habits_data[
                    (st.session_state.habits_data["name"] == selected_habit) &
                    (st.session_state.habits_data["date"] >= pd.Timestamp(start_date)) &
                    (st.session_state.habits_data["date"] <= pd.Timestamp(end_date))
                ]

                if filtered_data.empty:
                    st.warning("No data available for the selected habit and date range.")
                else:
                    # Group data by date and status
                    progress_summary = filtered_data.groupby(["date", "status"]).size().unstack(fill_value=0)

                    if progress_summary.empty:
                        st.warning("No data to plot for the selected habit and date range.")
                    else:
                        # Visualization: Pie Chart
                        status_counts = filtered_data["status"].value_counts()
                        fig2, ax2 = plt.subplots()
                        ax2.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
                        plt.title(f"Status Distribution for {selected_habit}")
                        st.pyplot(fig2)

                        # Visualization: Line Chart
                        progress_trend = filtered_data.groupby(["date", "status"]).size().unstack(fill_value=0).reset_index()

                        fig3, ax3 = plt.subplots(figsize=(10, 5))
                        for status in ["completed", "skipped", "pending"]:
                            if status in progress_trend.columns:
                                ax3.plot(
                                    progress_trend["date"],
                                    progress_trend[status],
                                    label=status.capitalize(),
                                    marker="o"
                                )

                        plt.title(f"Trend Over Time: {selected_habit}")
                        plt.ylabel("Count")
                        plt.xlabel("Date")
                        plt.legend()
                        plt.grid(True)
                        st.pyplot(fig3)

            else:
                st.error("The date column is not in datetime format.")
    elif menu == "Dashboard":
        st.subheader("Habits Overview")
        if st.session_state.habits_data.empty:
            st.info("No habit data available for Habits Overview.")
        if st.button("Logout"):
                st.session_state.logged_in = False
                st.success(f"bye bye {username} visit again!")
else:
   if not auth_option == 'Register':
       st.warning("Please log in or register to use the application.")
