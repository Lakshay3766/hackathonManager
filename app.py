import streamlit as st
from datetime import datetime, date
import sqlite3
import requests
from bs4 import BeautifulSoup
import altair as alt
import pandas as pd
import os

# Path to the database file
DB_FILE = "hackathons.db"
ATTACHMENT_FOLDER = "attachments"

# Ensure the attachment folder exists
if not os.path.exists(ATTACHMENT_FOLDER):
    os.makedirs(ATTACHMENT_FOLDER)

# Function to initialize the database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS hackathons (
                id INTEGER PRIMARY KEY,
                name TEXT,
                prize TEXT,
                location TEXT,
                deadline DATE,
                progress INTEGER,
                website TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                hackathon_id INTEGER,
                name TEXT,
                file_path TEXT,
                FOREIGN KEY (hackathon_id) REFERENCES hackathons (id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY,
                name TEXT,
                role TEXT,
                email TEXT
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Function to add a new hackathon
def add_hackathon(name, prize, location, deadline, website):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO hackathons (name, prize, location, deadline, progress, website)
            VALUES (?, ?, ?, ?, 0, ?)
        ''', (name, prize, location, deadline, website))
        conn.commit()

# Function to get all hackathons
def get_hackathons():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM hackathons')
        return c.fetchall()

# Function to add an attachment
def add_attachment(hackathon_id, name, file_path):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO attachments (hackathon_id, name, file_path)
            VALUES (?, ?, ?)
        ''', (hackathon_id, name, file_path))
        conn.commit()

# Function to get attachments for a hackathon
def get_attachments(hackathon_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM attachments WHERE hackathon_id = ?', (hackathon_id,))
        return c.fetchall()

# Function to delete a hackathon
def delete_hackathon(hackathon_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM hackathons WHERE id = ?', (hackathon_id,))
        c.execute('DELETE FROM attachments WHERE hackathon_id = ?', (hackathon_id,))
        conn.commit()

# Function to update progress
def update_progress(hackathon_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM attachments WHERE hackathon_id = ?', (hackathon_id,))
        attachments_count = c.fetchone()[0]
        progress = attachments_count * 25
        c.execute('UPDATE hackathons SET progress = ? WHERE id = ?', (progress, hackathon_id))
        conn.commit()

# Function to add a new team member
def add_team_member(name, role, email):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO team_members (name, role, email)
            VALUES (?, ?, ?)
        ''', (name, role, email))
        conn.commit()

# Function to get all team members
def get_team_members():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM team_members')
        return c.fetchall()

# Streamlit app
st.set_page_config(layout="wide")  # Set layout to wide

st.title("Hackathon Management Tool")

# Display logo
st.image('download.png', width=100)

# Sidebar for adding new hackathons and team members
st.sidebar.header("Add New Hackathon")
with st.sidebar.form("Add Hackathon", clear_on_submit=True):
    name = st.text_input("Hackathon Name")
    prize = st.text_input("Prize")
    location = st.text_input("Location")
    deadline = st.date_input("Deadline")
    website = st.text_input("Website URL")
    submit = st.form_submit_button("Add Hackathon")

    if submit:
        add_hackathon(name, prize, location, deadline, website)
        st.sidebar.success(f"Hackathon '{name}' added successfully!")
        # Rerun the app by resetting the session state
        st.session_state['last_added'] = name

st.sidebar.markdown("---")

st.sidebar.header("Add New Team Member")
with st.sidebar.form("Add Team Member", clear_on_submit=True):
    member_name = st.text_input("Member Name")
    member_role = st.text_input("Role")
    member_email = st.text_input("Email")
    submit_member = st.form_submit_button("Add Team Member")

    if submit_member:
        add_team_member(member_name, member_role, member_email)
        st.sidebar.success(f"Team member '{member_name}' added successfully!")
        # Rerun the app by resetting the session state
        st.session_state['last_added_member'] = member_name

st.markdown("---")  # Divider

# Main content layout
col1, col2 = st.columns([3, 1])

# Display existing hackathons in col1
with col1:
    st.header("Hackathon List")
    hackathons = get_hackathons()
    if hackathons:
        selected_hackathon_name = st.selectbox("Select a hackathon to view details:", options=[h[1] for h in hackathons])

        for hackathon in hackathons:
            if hackathon[1] == selected_hackathon_name:
                hackathon_id = hackathon[0]
                st.subheader(f"{hackathon[1]} ({hackathon[3]})")
                st.markdown(
                    f"""
                    <style>
                    .hackathon-details {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                        font-size: 20px;
                    }}
                    .hackathon-details > div {{
                        flex: 1 1 300px;
                    }}
                    .bold-text {{
                        font-weight: bold;
                    }}
                    .large-text {{
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
                days_left = (datetime.strptime(hackathon[4], '%Y-%m-%d').date() - date.today()).days
                st.markdown(
                    f"""
                    <div class="hackathon-details">
                        <div><strong>Prize:</strong> {hackathon[2]}</div>
                        <div><strong>Deadline:</strong> {hackathon[4]}</div>
                        <div><strong>Website:</strong> <a href="{hackathon[5]}" target="_blank">Link</a></div>
                        <div class="large-text"><strong>Days left:</strong> {days_left} days</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

                st.markdown(f"**Progress:** {hackathon[5]}%")

                # Attachments
                st.write("**Attachments:**")
                attachment_name = st.text_input("Attachment Name", key=f"attachment_name_{hackathon_id}")
                attachment_file = st.file_uploader("Choose a file", key=f"attachment_file_{hackathon_id}")
                if st.button("Add Attachment", key=f"add_attachment_{hackathon_id}"):
                    if attachment_name and attachment_file:
                        file_path = os.path.join(ATTACHMENT_FOLDER, attachment_file.name)
                        with open(file_path, 'wb') as f:
                            f.write(attachment_file.getbuffer())
                        add_attachment(hackathon_id, attachment_name, file_path)
                        update_progress(hackathon_id)
                        st.success(f"Attachment '{attachment_name}' added successfully!")
                        # Rerun the app by resetting the session state
                        st.session_state['last_attachment'] = attachment_name

                attachments = get_attachments(hackathon_id)
                if attachments:
                    for attachment in attachments:
                        st.write(f"- **{attachment[2]}**")
                        with open(attachment[3], 'rb') as f:
                            st.download_button("Download", f, file_name=attachment[2])

                # Delete button
                if st.button(f"Delete {hackathon[1]}", key=f"delete_{hackathon_id}"):
                    delete_hackathon(hackathon_id)
                    st.success(f"Hackathon '{hackathon[1]}' deleted successfully!")
                    # Rerun the app by resetting the session state
                    st.session_state['last_deleted'] = hackathon[1]
                    st.experimental_rerun()
    else:
        st.write("No hackathons added yet.")

    st.markdown("---")  # Divider

    # Display team members
    st.header("Team Members")
    team_members = get_team_members()
    if team_members:
        for member in team_members:
            st.markdown(f"**<span style='font-size:20px'>Name:</span>** <span style='font-size:20px'>{member[1]}</span>", unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size:20px'>Role:</span>** <span style='font-size:20px'>{member[2]}</span>", unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size:20px'>Email:</span>** <span style='font-size:20px'>{member[3]}</span>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.write("No team members added yet.")

# Analyzer section in col2
with col2:
    st.header("Analyzer")
    if hackathons:
        for hackathon in hackathons:
            days_left = (datetime.strptime(hackathon[4], '%Y-%m-%d').date() - date.today()).days
            if days_left <= 7 or hackathon[5] < 50:
                st.warning(f"{hackathon[1]} ({hackathon[3]}) - {days_left} days left, Progress: {hackathon[5]}%")
    else:
        st.info("No upcoming deadlines or low progress hackathons.")

    st.markdown("---")  # Divider

    # Analysis section with bar chart
    st.header("Hackathon Analysis")
    if hackathons:
        total_hackathons = len(hackathons)
        completed_tasks = sum(
            len(get_attachments(h[0])) == 4
            for h in hackathons
        )
        avg_progress = sum(h[5] for h in hackathons) / total_hackathons
        
        st.write(f"**Total Hackathons:** {total_hackathons}")
        st.write(f"**Completed Hackathons:** {completed_tasks}")
        st.write(f"**Average Progress:** {avg_progress:.2f}%")
        
        # Create a DataFrame for the bar chart
        hackathon_data = pd.DataFrame([
            {'name': h[1], 'progress': h[5]}
            for h in hackathons
        ])

        # Create and display the bar chart
        chart = alt.Chart(hackathon_data).mark_bar().encode(
            x='name',
            y='progress',
            color='name'
        ).properties(
            width=300,
            height=300,
            title='Hackathon Progress'
        )

        st.altair_chart(chart)
    else:
        st.info("No hackathons available for analysis.")
