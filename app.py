# ================== IMPORTS ================== #

import streamlit as st
import json
import os
import base64
import requests
import uuid
from datetime import datetime

# ================== CONFIG ================== #

st.set_page_config(page_title="IEI Newsletter", layout="wide")

# ================== FOLDERS ================== #

os.makedirs("pdf", exist_ok=True)
os.makedirs("static", exist_ok=True)

# ================== ADMIN LOGIN ================== #

ADMIN_EMAIL = "madurailc@ieindia.org"
ADMIN_PASSWORD = "ieimlc_2026"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.sidebar.subheader("🔐 Admin Login")

    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")

    if st.sidebar.button("Login"):
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("Login successful")
        else:
            st.sidebar.error("Invalid credentials")

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

login()
if st.session_state.logged_in:
    logout()

# ================== GITHUB CONFIG ================== #

GITHUB_USERNAME = "seba003"
REPO_NAME = "iei-newsletter"
BRANCH = "main"

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    GITHUB_TOKEN = ""

BASE_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/"

# ================== UNIQUE ID ================== #

def generate_id():
    return str(uuid.uuid4())

# ================== GITHUB FUNCTIONS ================== #

def load_github_json(filename):
    try:
        url = BASE_URL + filename
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            content = r.json()["content"]
            decoded = base64.b64decode(content).decode()
            return json.loads(decoded)

        elif r.status_code == 404:
            save_github_json(filename, [])
            return []

        else:
            st.error(f"Load error: {r.text}")

    except Exception as e:
        st.error(f"Load Exception: {e}")

    return []

def save_github_json(filename, data):
    try:
        url = BASE_URL + filename
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        r = requests.get(url, headers=headers)
        sha = r.json()["sha"] if r.status_code == 200 else None

        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()

        payload = {
            "message": f"Update {filename}",
            "content": content,
            "branch": BRANCH
        }

        if sha:
            payload["sha"] = sha

        res = requests.put(url, json=payload, headers=headers)

        if res.status_code in [200, 201]:
            st.success(f"{filename} saved to GitHub")
        else:
            st.error(f"GitHub Error: {res.text}")

    except Exception as e:
        st.error(f"Save Exception: {e}")

# ================== FILE NAMES ================== #

ANN_FILE = "announcements.json"
EVENT_FILE = "events.json"
EXPERT_FILE = "expertise.json"
RECOG_FILE = "recognitions.json"
STUDENT_FILE = "students.json"

# ================== LOAD DATA ================== #

announcements = load_github_json(ANN_FILE)
events = load_github_json(EVENT_FILE)
expertise = load_github_json(EXPERT_FILE)
recognitions = load_github_json(RECOG_FILE)
students = load_github_json(STUDENT_FILE)

# ================== HELPERS ================== #

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return "N/A"

def upload_image(file):
    if file:
        return base64.b64encode(file.read()).decode()
    return ""

def display_image(img):
    if img:
        return f"data:image/png;base64,{img}"
    return ""

def clean_text(text):
    return text.strip().title() if text else ""

def clean_paragraph(text):
    return text.strip() if text else ""

# ================== DIVISIONS ================== #

divisions = [
    "Aerospace Engineering","Agricultural Engineering","Architectural Engineering",
    "Chemical Engineering","Civil Engineering","Computer Engineering",
    "Electrical Engineering","Electronics & Telecommunication Engineering",
    "Environmental Engineering","Marine Engineering","Mechanical Engineering",
    "Metallurgical & Materials Engineering","Mining Engineering",
    "Production Engineering","Textile Engineering"
]

# ================== SIDEBAR ================== #

st.sidebar.title("📚 IEI Newsletter")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Announcements", "Events", "Expertise", "Recognitions", "Students", "Admin"]
)

# ================== BASIC UI ================== #

st.markdown("""
<div style="background:#0B3D91;color:white;padding:15px;border-radius:10px;text-align:center;">
<h2>E-Newsletter</h2>
<h4>Institution of Engineers (India)</h4>
<h5>Madurai Local Centre</h5>
</div>
""", unsafe_allow_html=True)
# ================== FILTERS ================== #

st.sidebar.markdown("### 🔍 Filters")

division_filter = st.sidebar.selectbox("Engineering Division", ["All"] + divisions)

col1, col2 = st.sidebar.columns(2)

with col1:
    from_date = st.date_input("From")

with col2:
    to_date = st.date_input("To")

def filter_data(data):

    filtered = data

    if division_filter != "All":
        filtered = [d for d in filtered if d.get("division") == division_filter]

    if from_date and to_date:
        filtered = [
            d for d in filtered
            if d.get("date") and
            from_date.strftime("%Y-%m-%d") <= d.get("date") <= to_date.strftime("%Y-%m-%d")
        ]

    return filtered


# ================== STYLES ================== #

st.markdown("""
<style>
.card {
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
}
.section-title {
    color:#0B3D91;
    border-bottom:2px solid #0B3D91;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)


# ================== HOME ================== #

if page == "Home":

    st.markdown("<h3 class='section-title'>🏠 Dashboard</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Announcements", len(announcements))
    col2.metric("Events", len(events))
    col3.metric("Expertise", len(expertise))

    col4, col5 = st.columns(2)
    col4.metric("Recognitions", len(recognitions))
    col5.metric("Students", len(students))


# ================== ANNOUNCEMENTS ================== #

elif page == "Announcements":

    st.markdown("<h3 class='section-title'>📢 Announcements</h3>", unsafe_allow_html=True)

    for item in filter_data(announcements):

        st.markdown(f"""
        <div class='card'>
        <b>{item.get('title')}</b><br>
        <b>Date:</b> {format_date(item.get('date'))} | {item.get('time')}<br>
        <b>Venue:</b> {item.get('venue')}<br>
        <b>Guest:</b> {item.get('guest')}<br><br>
        {item.get('notes')}
        </div>
        """, unsafe_allow_html=True)


# ================== EVENTS ================== #

elif page == "Events":

    st.markdown("<h3 class='section-title'>🎯 Events Conducted</h3>", unsafe_allow_html=True)

    for item in filter_data(events):

        st.markdown(f"""
        <div class='card'>
        <b>{item.get('title')}</b><br>
        <b>Date:</b> {format_date(item.get('date'))} | {item.get('time')}<br>
        <b>Venue:</b> {item.get('venue')}<br>
        <b>Guest:</b> {item.get('guest')}<br>
        <b>Participants:</b> {item.get('participants')}<br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     caption=item.get("caption"),
                     use_container_width=True)


# ================== EXPERTISE ================== #

elif page == "Expertise":

    st.markdown("<h3 class='section-title'>👨‍🏫 Engineering Expertise</h3>", unsafe_allow_html=True)

    for item in expertise:

        st.markdown(f"""
        <div class='card'>
        <b>{item.get('title')}</b><br>
        <b>Expert:</b> {item.get('expert')}<br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     caption=item.get("caption"),
                     use_container_width=True)


# ================== RECOGNITIONS ================== #

elif page == "Recognitions":

    st.markdown("<h3 class='section-title'>🏆 Member Recognitions</h3>", unsafe_allow_html=True)

    for item in recognitions:

        st.markdown(f"""
        <div class='card'>
        <b>{item.get('name')}</b><br>
        <b>Member No:</b> {item.get('number')}<br><br>
        {item.get('achievement')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     use_container_width=True)


# ================== STUDENTS ================== #

elif page == "Students":

    st.markdown("<h3 class='section-title'>🎓 Student Corner</h3>", unsafe_allow_html=True)

    for item in students:

        st.markdown(f"""
        <div class='card'>
        <b>{item.get('name')}</b><br>
        <b>Institution:</b> {item.get('institution')}<br>
        <b>Chapter:</b> {item.get('chapter')} | {item.get('year')}<br><br>
        <b>{item.get('title')}</b><br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     use_container_width=True)
# ================== ADMIN PANEL ================== #

elif page == "Admin":

    if not st.session_state.logged_in:
        st.warning("🔐 Please login first")
        st.stop()

    st.markdown("<h3 class='section-title'>🛠 Admin Panel</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Announcements", "Events", "Expertise", "Recognitions", "Students"
    ])

    # ================== ANNOUNCEMENTS ================== #
    with tab1:

        st.subheader("➕ Add Announcement")

        title = st.text_input("Title", key="ann_title")
        date = st.date_input("Date", key="ann_date")
        time = st.text_input("Time", key="ann_time")
        venue = st.text_input("Venue", key="ann_venue")
        guest = st.text_input("Chief Guest / Resource Person", key="ann_guest")
        notes = st.text_area("Notes", key="ann_notes")
        division = st.selectbox("Division", divisions, key="ann_div")

        if st.button("Save Announcement", key="ann_save"):
            announcements.append({
                "id": generate_id(),
                "title": clean_text(title),
                "date": date.strftime("%Y-%m-%d"),
                "time": time,
                "venue": clean_text(venue),
                "guest": clean_text(guest),
                "notes": clean_paragraph(notes),
                "division": division
            })
            save_github_json(ANN_FILE, announcements)
            st.success("Saved successfully")
            st.rerun()

    # ================== EVENTS ================== #
    with tab2:

        st.subheader("➕ Add Event")

        title = st.text_input("Title", key="ev_title")
        date = st.date_input("Date", key="ev_date")
        time = st.text_input("Time", key="ev_time")
        venue = st.text_input("Venue", key="ev_venue")
        guest = st.text_input("Chief Guest", key="ev_guest")
        participants = st.number_input("Participants", min_value=0, key="ev_part")
        report = st.text_area("Report (300-400 words)", key="ev_report")

        image_file = st.file_uploader("Upload Image", key="ev_img")
        image = upload_image(image_file)

        caption = st.text_input("Image Caption", key="ev_cap")
        division = st.selectbox("Division", divisions, key="ev_div")

        if st.button("Save Event", key="ev_save"):
            events.append({
                "id": generate_id(),
                "title": clean_text(title),
                "date": date.strftime("%Y-%m-%d"),
                "time": time,
                "venue": clean_text(venue),
                "guest": clean_text(guest),
                "participants": participants,
                "report": clean_paragraph(report),
                "image": image,
                "caption": clean_text(caption),
                "division": division
            })
            save_github_json(EVENT_FILE, events)
            st.success("Saved successfully")
            st.rerun()

    # ================== EXPERTISE ================== #
    with tab3:

        st.subheader("➕ Add Expertise")

        expert = st.text_input("Expert Name", key="ex_name")
        title = st.text_input("Title (max 10 words)", key="ex_title")
        report = st.text_area("Report (200-250 words)", key="ex_report")

        image_file = st.file_uploader("Upload Image", key="ex_img")
        image = upload_image(image_file)

        caption = st.text_input("Image Caption", key="ex_cap")

        if st.button("Save Expertise", key="ex_save"):
            expertise.append({
                "id": generate_id(),
                "expert": clean_text(expert),
                "title": clean_text(title),
                "report": clean_paragraph(report),
                "image": image,
                "caption": clean_text(caption)
            })
            save_github_json(EXPERT_FILE, expertise)
            st.success("Saved successfully")
            st.rerun()

    # ================== RECOGNITIONS ================== #
    with tab4:

        st.subheader("➕ Add Recognition")

        name = st.text_input("Member Name", key="rec_name")
        number = st.text_input("Member Number", key="rec_num")
        achievement = st.text_area("Achievement Details", key="rec_ach")

        image_file = st.file_uploader("Upload Image", key="rec_img")
        image = upload_image(image_file)

        if st.button("Save Recognition", key="rec_save"):
            recognitions.append({
                "id": generate_id(),
                "name": clean_text(name),
                "number": number,
                "achievement": clean_paragraph(achievement),
                "image": image
            })
            save_github_json(RECOG_FILE, recognitions)
            st.success("Saved successfully")
            st.rerun()

    # ================== STUDENTS ================== #
    with tab5:

        st.subheader("➕ Add Student Entry")

        name = st.text_input("Student Name", key="stu_name")
        chapter = st.text_input("Student Chapter", key="stu_ch")
        year = st.text_input("Year of Study", key="stu_year")
        institution = st.text_input("Institution", key="stu_inst")
        title = st.text_input("Project / Achievement Title", key="stu_title")
        report = st.text_area("Report", key="stu_report")

        image_file = st.file_uploader("Upload Image", key="stu_img")
        image = upload_image(image_file)

        if st.button("Save Student", key="stu_save"):
            students.append({
                "id": generate_id(),
                "name": clean_text(name),
                "chapter": chapter,
                "year": year,
                "institution": institution,
                "title": clean_text(title),
                "report": clean_paragraph(report),
                "image": image
            })
            save_github_json(STUDENT_FILE, students)
            st.success("Saved successfully")
            st.rerun()
# ================== EDIT + DELETE SYSTEM ================== #

elif page == "Admin":

    if not st.session_state.logged_in:
        st.warning("🔐 Please login first")
        st.stop()

    st.markdown("<h3 class='section-title'>🛠 Manage Data</h3>", unsafe_allow_html=True)

    dataset = st.selectbox(
        "Select Section",
        ["Announcements", "Events", "Expertise", "Recognitions", "Students"]
    )

    if dataset == "Announcements":
        data = announcements
        file_name = ANN_FILE

    elif dataset == "Events":
        data = events
        file_name = EVENT_FILE

    elif dataset == "Expertise":
        data = expertise
        file_name = EXPERT_FILE

    elif dataset == "Recognitions":
        data = recognitions
        file_name = RECOG_FILE

    else:
        data = students
        file_name = STUDENT_FILE

    st.markdown("### ✏️ Edit / Delete Entries")

    for i, item in enumerate(data):

        with st.expander(f"{item.get('title', item.get('name','Entry'))}"):

            new_title = st.text_input("Title", item.get("title",""), key=f"t_{i}")
            new_report = st.text_area("Report / Notes", item.get("report", item.get("notes","")), key=f"r_{i}")

            col1, col2 = st.columns(2)

            if col1.button("💾 Update", key=f"u_{i}"):
                if dataset == "Announcements":
                    data[i]["title"] = new_title
                    data[i]["notes"] = new_report
                else:
                    data[i]["title"] = new_title
                    data[i]["report"] = new_report

                save_github_json(file_name, data)
                st.success("Updated")
                st.rerun()

            if col2.button("❌ Delete", key=f"d_{i}"):
                data.pop(i)
                save_github_json(file_name, data)
                st.warning("Deleted")
                st.rerun()


# ================== PDF SYSTEM ================== #

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfMerger

title_style = ParagraphStyle(name='Title', fontName='Times-Bold', fontSize=16, spaceAfter=10)
body_style = ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=11, leading=15)

def header_footer(c, doc):
    c.setFont("Times-Roman", 9)

    # Header
    c.drawString(40, 800, "E-Newsletter IEI-MLC")
    c.drawRightString(550, 800, "www.ieimadurailc.org")

    # Footer
    c.drawString(40, 30, "Institution of Engineers (India) – Madurai Local Centre")
    c.drawString(40, 18, "Promoting Engineering Excellence for Nation Building")
    c.drawString(40, 6, "Contact: madurailc@ieindia.org")

    c.drawRightString(550, 6, f"Page {doc.page}")


def generate_content_pdf():

    doc = SimpleDocTemplate("pdf/content.pdf", pagesize=A4)
    story = []

    # ANNOUNCEMENTS
    story.append(Paragraph("ANNOUNCEMENTS", title_style))
    for item in announcements:
        story.append(Paragraph(item.get("title",""), body_style))
        story.append(Paragraph(item.get("notes",""), body_style))
        story.append(Spacer(1,10))
    story.append(PageBreak())

    # EVENTS
    story.append(Paragraph("EVENTS CONDUCTED", title_style))
    for item in events:
        story.append(Paragraph(item.get("title",""), body_style))
        story.append(Paragraph(item.get("report",""), body_style))
        story.append(Spacer(1,10))
    story.append(PageBreak())

    # EXPERTISE
    story.append(Paragraph("ENGINEERING EXPERTISE", title_style))
    for item in expertise:
        story.append(Paragraph(item.get("title",""), body_style))
        story.append(Paragraph(item.get("report",""), body_style))
        story.append(Spacer(1,10))
    story.append(PageBreak())

    # RECOGNITIONS
    story.append(Paragraph("MEMBER RECOGNITIONS", title_style))
    for item in recognitions:
        story.append(Paragraph(item.get("name",""), body_style))
        story.append(Paragraph(item.get("achievement",""), body_style))
        story.append(Spacer(1,10))
    story.append(PageBreak())

    # STUDENTS
    story.append(Paragraph("STUDENT CORNER", title_style))
    for item in students:
        story.append(Paragraph(item.get("name",""), body_style))
        story.append(Paragraph(item.get("report",""), body_style))
        story.append(Spacer(1,10))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

    return "pdf/content.pdf"


def generate_full_pdf(a, e, x, r, s):

    merger = PdfMerger()

    # Cover pages
    for f in ["cover.pdf", "chairman.pdf", "secretary.pdf"]:
        path = f"static/{f}"
        if os.path.exists(path):
            merger.append(path)

    # Main content
    merger.append(generate_content_pdf())

    # Special page
    if os.path.exists("static/special.pdf"):
        merger.append("static/special.pdf")

    output = "pdf/final_newsletter.pdf"
    merger.write(output)
    merger.close()

    return output


# ================== DOWNLOAD BUTTON ================== #

if page == "Home":

    st.markdown("### 📥 Download Newsletter")

    if st.button("Generate Full Newsletter"):

        file = generate_full_pdf(
            announcements, events, expertise, recognitions, students
        )

        with open(file, "rb") as f:
            st.download_button(
                "⬇ Download PDF",
                f,
                file_name="IEI_Newsletter.pdf"
            )
