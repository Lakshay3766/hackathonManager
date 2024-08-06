import streamlit as st
from datetime import datetime
import webbrowser
import requests
from bs4 import BeautifulSoup
import altair as alt
import pandas as pd
import json
import os

# Path to the JSON files to store hackathon and team member data
HACKATHON_DATA_FILE = "hackathons.json"
TEAM_MEMBER_DATA_FILE = "team_members.json"
ATTACHMENT_FOLDER = "attachments"

# Ensure the attachment folder exists
if not os.path.exists(ATTACHMENT_FOLDER):
    os.makedirs(ATTACHMENT_FOLDER)

# Function to save hackathon data to a JSON file
def save_hackathons(data):
    try:
        with open(HACKATHON_DATA_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving hackathon data: {e}")

# Function to load hackathon data from a JSON file
def load_hackathons():
    if os.path.exists(HACKATHON_DATA_FILE):
        try:
            with open(HACKATHON_DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Error loading hackathon data: JSON decode error.")
            return []
        except Exception as e:
            st.error(f"Error loading hackathon data: {e}")
            return []
    return []

# Function to save team member data to a JSON file
def save_team_members(data):
    try:
        with open(TEAM_MEMBER_DATA_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"Error saving team member data: {e}")

# Function to load team member data from a JSON file
def load_team_members():
    if os.path.exists(TEAM_MEMBER_DATA_FILE):
        try:
            with open(TEAM_MEMBER_DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Error loading team member data: JSON decode error.")
            return []
        except Exception as e:
            st.error(f"Error loading team member data: {e}")
            return []
    return []

# Load hackathon and team member data into session state
if 'hackathons' not in st.session_state:
    st.session_state.hackathons = load_hackathons()

if 'team_members' not in st.session_state:
    st.session_state.team_members = load_team_members()

# Function to add a new hackathon
def add_hackathon(name, prize, location, deadline, website):
    try:
        hackathon = {
            'name': name,
            'prize': prize,
            'location': location,
            'deadline': deadline,
            'progress': 0,  # Initial progress is 0%
            'website': website,
            'image_url': scrape_image(website),
            'attachments': []
        }
        st.session_state.hackathons.append(hackathon)
        save_hackathons(st.session_state.hackathons)
    except Exception as e:
        st.error(f"Error adding hackathon: {e}")

# Function to update progress
def update_progress(index):
    try:
        attachments_count = len(st.session_state.hackathons[index]['attachments'])
        st.session_state.hackathons[index]['progress'] = attachments_count * 25
        save_hackathons(st.session_state.hackathons)
    except Exception as e:
        st.error(f"Error updating progress: {e}")

# Function to delete a hackathon
def delete_hackathon(index):
    try:
        del st.session_state.hackathons[index]
        save_hackathons(st.session_state.hackathons)
    except Exception as e:
        st.error(f"Error deleting hackathon: {e}")

# Function to add an attachment to a hackathon
def add_attachment(hackathon_index, attachment_name, attachment_file):
    try:
        file_path = os.path.join(ATTACHMENT_FOLDER, attachment_file.name)
        with open(file_path, 'wb') as f:
            f.write(attachment_file.getbuffer())
        attachment = {
            'name': attachment_name,
            'file_path': file_path
        }
        st.session_state.hackathons[hackathon_index]['attachments'].append(attachment)
        update_progress(hackathon_index)
    except Exception as e:
        st.error(f"Error adding attachment: {e}")

# Function to add a new team member
def add_team_member(name, role, email):
    try:
        team_member = {
            'name': name,
            'role': role,
            'email': email
        }
        st.session_state.team_members.append(team_member)
        save_team_members(st.session_state.team_members)
    except Exception as e:
        st.error(f"Error adding team member: {e}")

# Function to scrape an image from the hackathon website
def scrape_image(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        img = soup.find('img')
        if img:
            return img['src']
    except Exception as e:
        st.error(f"Error scraping image: {e}")
    return None

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

st.markdown("---")  # Divider

# Main content layout
col1, col2 = st.columns([3, 1])

# Display existing hackathons in col1
with col1:
    st.header("Hackathon List")
    if st.session_state.hackathons:
        selected_hackathon = st.selectbox("Select a hackathon to view details:", options=[h['name'] for h in st.session_state.hackathons])

        for i, hackathon in enumerate(st.session_state.hackathons):
            if hackathon['name'] == selected_hackathon:
                st.subheader(f"{hackathon['name']} ({hackathon['location']})")
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
                st.markdown(
                    f"""
                    <div class="hackathon-details">
                        <div><strong>Prize:</strong> {hackathon['prize']}</div>
                        <div><strong>Deadline:</strong> {hackathon['deadline'].strftime('%Y-%m-%d')}</div>
                        <div><strong>Website:</strong> <a href="{hackathon['website']}" target="_blank">Link</a></div>
                        <div class="large-text"><strong>Days left:</strong> {(hackathon['deadline'] - datetime.today().date()).days} days</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                if hackathon['image_url']:
                    st.image(hackathon['image_url'], use_column_width=True)

                st.markdown(f"**Progress:** {hackathon['progress']}%")

                # Attachments
                st.write("**Attachments:**")
                attachment_name = st.text_input("Attachment Name", key=f"attachment_name_{i}")
                attachment_file = st.file_uploader("Choose a file", key=f"attachment_file_{i}")
                if st.button("Add Attachment", key=f"add_attachment_{i}"):
                    if attachment_name and attachment_file:
                        add_attachment(i, attachment_name, attachment_file)
                        st.success(f"Attachment '{attachment_name}' added successfully!")
                    else:
                        st.error("Please provide both attachment name and file.")

                if hackathon['attachments']:
                    for attachment in hackathon['attachments']:
                        st.write(f"- **{attachment['name']}**")
                        with open(attachment['file_path'], 'rb') as f:
                            st.download_button("Download", f, file_name=attachment['name'])

                # Delete button
                if st.button(f"Delete {hackathon['name']}", key=f"delete_{i}"):
                    delete_hackathon(i)
                    st.experimental_rerun()
    else:
        st.write("No hackathons added yet.")

    st.markdown("---")  # Divider

    # Display team members
    st.header("Team Members")
    if st.session_state.team_members:
        for member in st.session_state.team_members:
            st.markdown(f"**<span style='font-size:20px'>Name:</span>** <span style='font-size:20px'>{member['name']}</span>", unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size:20px'>Role:</span>** <span style='font-size:20px'>{member['role']}</span>", unsafe_allow_html=True)
            st.markdown(f"**<span style='font-size:20px'>Email:</span>** <span style='font-size:20px'>{member['email']}</span>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.write("No team members added yet.")

# Analyzer section in col2
with col2:
    st.header("Analyzer")
    if st.session_state.hackathons:
        hackathons_sorted = sorted(st.session_state.hackathons, key=lambda x: x['deadline'])
        for hackathon in hackathons_sorted:
            days_left = (hackathon['deadline'] - datetime.today().date()).days
            if days_left <= 7 or hackathon['progress'] < 50:
                st.warning(f"{hackathon['name']} ({hackathon['location']}) - {days_left} days left, Progress: {hackathon['progress']}%")
    else:
        st.info("No upcoming deadlines or low progress hackathons.")

    st.markdown("---")  # Divider

    # Analysis section with bar chart
    st.header("Hackathon Analysis")
    if st.session_state.hackathons:
        total_hackathons = len(st.session_state.hackathons)
        completed_tasks = sum(
            len(h['attachments']) == 4
            for h in st.session_state.hackathons
        )
        avg_progress = sum(h['progress'] for h in st.session_state.hackathons) / total_hackathons
        
        st.write(f"**Total Hackathons:** {total_hackathons}")
        st.write(f"**Completed Hackathons:** {completed_tasks}")
        st.write(f"**Average Progress:** {avg_progress:.2f}%")
        
        # Create a DataFrame for the bar chart
        hackathon_data = pd.DataFrame([
            {'name': h['name'], 'progress': h['progress']}
            for h in st.session_state.hackathons
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
