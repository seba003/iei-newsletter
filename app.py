# ---------------- IMPORTS ---------------- #

import streamlit as st
import json
import os
import base64
import requests
from datetime import datetime

# ---------------- CONFIG ---------------- #

st.set_page_config(page_title="IEI Newsletter", layout="wide")

# ---------------- FOLDERS ---------------- #

os.makedirs("pdf", exist_ok=True)
os.makedirs("static", exist_ok=True)

# ---------------- ADMIN LOGIN ---------------- #

ADMIN_EMAIL = "sebastinaero@gmail.com"
ADMIN_PASSWORD = "ieimlc_2026"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.sidebar.subheader("🔐 Admin Login")

    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")

    if st.sidebar.button("Login", key="login_btn"):
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("Login successful")
        else:
            st.sidebar.error("Invalid credentials")

def logout():
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False

login()
if st.session_state.logged_in:
    logout()

# ---------------- GITHUB CONFIG ---------------- #

GITHUB_USERNAME = "seba003"
REPO_NAME = "seba003.github.io"
BRANCH = "main"

try:
    GITHUB_TOKEN = st.secrets["github_token"]
except:
    GITHUB_TOKEN = ""

BASE_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/"

# ---------------- GITHUB FUNCTIONS ---------------- #

def load_github_json(filename):
    try:
        url = BASE_URL + filename
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            content = r.json()["content"]
            decoded = base64.b64decode(content).decode()
            return json.loads(decoded)
    except:
        pass
    return []

def save_github_json(filename, data):
    try:
        url = BASE_URL + filename
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        r = requests.get(url, headers=headers)
        sha = r.json()["sha"] if r.status_code == 200 else None

        content = base64.b64encode(json.dumps(data, indent=4).encode()).decode()

        payload = {
            "message": "Update newsletter data",
            "content": content,
            "branch": BRANCH
        }

        if sha:
            payload["sha"] = sha

        requests.put(url, json=payload, headers=headers)
    except:
        st.warning("GitHub save failed")

# ---------------- FILES ---------------- #

ANN_FILE = "announcements.json"
EVENT_FILE = "events.json"
EXPERT_FILE = "expertise.json"
RECOG_FILE = "recognitions.json"
STUDENT_FILE = "students.json"

# ---------------- LOAD DATA ---------------- #

announcements = load_github_json(ANN_FILE)
events = load_github_json(EVENT_FILE)
expertise = load_github_json(EXPERT_FILE)
recognitions = load_github_json(RECOG_FILE)
students = load_github_json(STUDENT_FILE)

# ---------------- HELPERS ---------------- #

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return "N/A"

def save_uploaded_pdf(file, name):
    if file:
        with open(f"static/{name}", "wb") as f:
            f.write(file.read())

# ---------------- IMAGE UPLOAD ---------------- #

def upload_image(file):
    if file:
        return base64.b64encode(file.read()).decode()
    return ""

def display_image(img_data):
    if img_data:
        return f"data:image/png;base64,{img_data}"
    return ""

# ---------------- TEXT CLEANING ---------------- #

def clean_text(text):
    return text.strip().title() if text else ""

def clean_paragraph(text):
    return text.strip() if text else ""

# ---------------- DIVISIONS ---------------- #

divisions = [
    "Aerospace Engineering","Agricultural Engineering","Architectural Engineering",
    "Chemical Engineering","Civil Engineering","Computer Engineering",
    "Electrical Engineering","Electronics & Telecommunication Engineering",
    "Environmental Engineering","Marine Engineering","Mechanical Engineering",
    "Metallurgical & Materials Engineering","Mining Engineering",
    "Production Engineering","Textile Engineering"
]

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("📚 IEI Newsletter")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Announcements", "Events", "Expertise", "Recognitions", "Students", "Admin"]
)

# ---------------- FILTERS ---------------- #

st.sidebar.markdown("### 🔍 Filters")

division_filter = st.sidebar.selectbox("Division", ["All"] + divisions, key="filter_div")

from_date = st.sidebar.date_input("From", key="filter_from")
to_date = st.sidebar.date_input("To", key="filter_to")

def filter_data(data):
    result = data

    if division_filter != "All":
        result = [d for d in result if d.get("division") == division_filter]

    if from_date and to_date:
        result = [
            d for d in result
            if d.get("date") and
            from_date.strftime("%Y-%m-%d") <= d.get("date") <= to_date.strftime("%Y-%m-%d")
        ]

    return result

# ---------------- HEADER ---------------- #

st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
background:linear-gradient(90deg,#0B3D91,#1E88E5);
padding:15px;border-radius:12px;color:white;">

<img src="https://www.ieindia.org/WebUI/img/logo.png" width="80">

<div style="text-align:center;">
<h2 style="margin:0;">E-Newsletter</h2>
<h4 style="margin:0;">Institution of Engineers (India)</h4>
<h5 style="margin:0;">Madurai Local Centre</h5>
</div>

<div>www.ieimadurailc.org</div>

</div>
""", unsafe_allow_html=True)

# ---------------- STYLES ---------------- #

st.markdown("""
<style>
.main-card {
    background:#fff;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    box-shadow:0px 2px 6px rgba(0,0,0,0.1);
}
.section-title {
    color:#0B3D91;
    border-bottom:2px solid #0B3D91;
}
</style>
""", unsafe_allow_html=True)

# ---------------- ANALYTICS ---------------- #

def show_analytics():
    col1, col2, col3 = st.columns(3)
    col1.metric("Announcements", len(announcements))
    col2.metric("Events", len(events))
    col3.metric("Expertise", len(expertise))

    col4, col5 = st.columns(2)
    col4.metric("Recognitions", len(recognitions))
    col5.metric("Students", len(students))

# ---------------- PAGE ROUTING ---------------- #

if page == "Home":

    st.markdown("<h3 class='section-title'>Home</h3>", unsafe_allow_html=True)

    show_analytics()

    if st.button("Generate Newsletter", key="gen_pdf"):
        try:
            file = generate_full_pdf(
                announcements, events, expertise, recognitions, students
            )
            with open(file, "rb") as f:
                st.download_button("Download PDF", f, file_name="newsletter.pdf")
        except Exception as e:
            st.error(e)

# ---------------- ANNOUNCEMENTS ---------------- #

elif page == "Announcements":

    st.markdown("<h3 class='section-title'>Announcements</h3>", unsafe_allow_html=True)

    for item in filter_data(announcements):
        st.markdown(f"""
        <div class='main-card'>
        <b>{item.get('title')}</b><br>
        {format_date(item.get('date'))} | {item.get('time')}<br>
        {item.get('venue')}<br>
        {item.get('guest')}<br><br>
        {item.get('notes')}
        </div>
        """, unsafe_allow_html=True)

# ---------------- EVENTS ---------------- #

elif page == "Events":

    st.markdown("<h3 class='section-title'>Events</h3>", unsafe_allow_html=True)

    for item in filter_data(events):
        st.markdown(f"""
        <div class='main-card'>
        <b>{item.get('title')}</b><br>
        {format_date(item.get('date'))} | {item.get('time')}<br>
        {item.get('venue')}<br>
        {item.get('guest')}<br>
        Participants: {item.get('participants')}<br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     caption=item.get("caption"),
                     use_container_width=True)

# ---------------- EXPERTISE ---------------- #

elif page == "Expertise":

    st.markdown("<h3 class='section-title'>Expertise</h3>", unsafe_allow_html=True)

    for item in expertise:
        st.markdown(f"""
        <div class='main-card'>
        <b>{item.get('title')}</b><br>
        Expert: {item.get('expert')}<br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     caption=item.get("caption"),
                     use_container_width=True)

# ---------------- RECOGNITIONS ---------------- #

elif page == "Recognitions":

    st.markdown("<h3 class='section-title'>Recognitions</h3>", unsafe_allow_html=True)

    for item in recognitions:
        st.markdown(f"""
        <div class='main-card'>
        <b>{item.get('name')}</b><br>
        {item.get('number')}<br><br>
        {item.get('achievement')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     use_container_width=True)

# ---------------- STUDENTS ---------------- #

elif page == "Students":

    st.markdown("<h3 class='section-title'>Students</h3>", unsafe_allow_html=True)

    for item in students:
        st.markdown(f"""
        <div class='main-card'>
        <b>{item.get('name')}</b><br>
        {item.get('institution')}<br>
        {item.get('chapter')} | {item.get('year')}<br><br>
        {item.get('title')}<br><br>
        {item.get('report')}
        </div>
        """, unsafe_allow_html=True)

        if item.get("image"):
            st.image(display_image(item.get("image")),
                     use_container_width=True)
            
# ---------------- ADMIN PANEL ---------------- #

elif page == "Admin":

    if not st.session_state.logged_in:
        st.warning("🔐 Login required")
        st.stop()

    st.markdown("<h3 class='section-title'>Admin Panel</h3>", unsafe_allow_html=True)

    # ✅ Tabs (FIXED ISSUE)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Announcements", "Events", "Expertise",
        "Recognitions", "Students", "PDF Upload"
    ])

    # ---------------- ANNOUNCEMENTS ---------------- #
    with tab1:

        title = st.text_input("Title", key="ann_title")
        date = st.date_input("Date", key="ann_date")
        time = st.text_input("Time", key="ann_time")
        venue = st.text_input("Venue", key="ann_venue")
        guest = st.text_input("Guest", key="ann_guest")
        notes = st.text_area("Notes", key="ann_notes")
        division = st.selectbox("Division", divisions, key="ann_div")

        if st.button("Save Announcement", key="ann_save"):
            announcements.append({
                "title": clean_text(title),
                "date": date.strftime("%Y-%m-%d"),
                "time": time,
                "venue": clean_text(venue),
                "guest": clean_text(guest),
                "notes": clean_paragraph(notes),
                "division": division
            })
            save_github_json(ANN_FILE, announcements)
            st.success("Saved")

    # ---------------- EVENTS ---------------- #
    with tab2:

        title = st.text_input("Title", key="ev_title")
        date = st.date_input("Date", key="ev_date")
        time = st.text_input("Time", key="ev_time")
        venue = st.text_input("Venue", key="ev_venue")
        guest = st.text_input("Guest", key="ev_guest")
        participants = st.number_input("Participants", key="ev_part")
        report = st.text_area("Report", key="ev_report")

        image_file = st.file_uploader("Upload Image", key="ev_img")
        image = upload_image(image_file)

        caption = st.text_input("Caption", key="ev_cap")
        division = st.selectbox("Division", divisions, key="ev_div")

        if st.button("Save Event", key="ev_save"):
            events.append({
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
            st.success("Saved")

    # ---------------- EXPERTISE ---------------- #
    with tab3:

        expert = st.text_input("Expert", key="ex_exp")
        title = st.text_input("Title", key="ex_title")
        report = st.text_area("Report", key="ex_report")

        image_file = st.file_uploader("Upload Image", key="ex_img")
        image = upload_image(image_file)

        caption = st.text_input("Caption", key="ex_cap")

        if st.button("Save Expertise", key="ex_save"):
            expertise.append({
                "expert": clean_text(expert),
                "title": clean_text(title),
                "report": clean_paragraph(report),
                "image": image,
                "caption": clean_text(caption)
            })
            save_github_json(EXPERT_FILE, expertise)
            st.success("Saved")

    # ---------------- RECOGNITIONS ---------------- #
    with tab4:

        name = st.text_input("Name", key="rec_name")
        number = st.text_input("Member No", key="rec_num")
        achievement = st.text_area("Achievement", key="rec_ach")

        image_file = st.file_uploader("Upload Image", key="rec_img")
        image = upload_image(image_file)

        if st.button("Save Recognition", key="rec_save"):
            recognitions.append({
                "name": clean_text(name),
                "number": number,
                "achievement": clean_paragraph(achievement),
                "image": image
            })
            save_github_json(RECOG_FILE, recognitions)
            st.success("Saved")

    # ---------------- STUDENTS ---------------- #
    with tab5:

        name = st.text_input("Student Name", key="stu_name")
        chapter = st.text_input("Chapter", key="stu_ch")
        year = st.text_input("Year", key="stu_year")
        institution = st.text_input("Institution", key="stu_inst")
        title = st.text_input("Title", key="stu_title")
        report = st.text_area("Report", key="stu_rep")

        image_file = st.file_uploader("Upload Image", key="stu_img")
        image = upload_image(image_file)

        if st.button("Save Student", key="stu_save"):
            students.append({
                "name": clean_text(name),
                "chapter": chapter,
                "year": year,
                "institution": institution,
                "title": clean_text(title),
                "report": clean_paragraph(report),
                "image": image
            })
            save_github_json(STUDENT_FILE, students)
            st.success("Saved")

    # ---------------- PDF UPLOAD ---------------- #
    with tab6:

        cover = st.file_uploader("Cover PDF", key="pdf1")
        chairman = st.file_uploader("Chairman PDF", key="pdf2")
        secretary = st.file_uploader("Secretary PDF", key="pdf3")
        special = st.file_uploader("Special PDF", key="pdf4")

        if st.button("Upload PDFs", key="pdf_save"):
            save_uploaded_pdf(cover, "cover.pdf")
            save_uploaded_pdf(chairman, "chairman.pdf")
            save_uploaded_pdf(secretary, "secretary.pdf")
            save_uploaded_pdf(special, "special.pdf")
            st.success("Uploaded")

# ---------------- PDF ENGINE ---------------- #

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfMerger

style = ParagraphStyle(name="Normal", fontName="Times-Roman", fontSize=11, leading=14)

def generate_content_pdf():
    doc = SimpleDocTemplate("pdf/content.pdf", pagesize=A4)
    story = []

    for item in announcements:
        story.append(Paragraph(item.get("title",""), style))
        story.append(Spacer(1,10))

    story.append(PageBreak())

    for item in events:
        story.append(Paragraph(item.get("title",""), style))
        story.append(Paragraph(item.get("report",""), style))
        story.append(Spacer(1,10))

    doc.build(story)
    return "pdf/content.pdf"

def generate_full_pdf(a,e,x,r,s):
    merger = PdfMerger()

    for f in ["cover.pdf","chairman.pdf","secretary.pdf"]:
        path = f"static/{f}"
        if os.path.exists(path):
            merger.append(path)

    merger.append(generate_content_pdf())

    if os.path.exists("static/special.pdf"):
        merger.append("static/special.pdf")

    output = "pdf/final.pdf"
    merger.write(output)
    merger.close()

    return output