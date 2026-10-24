
import json
import html
from pathlib import Path
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE = Path(__file__).parent / "school_data.json"


# =========================================================
# DATABASE
# =========================================================

def load_data():
    if not DATABASE.exists():
        return {"students": [], "teachers": []}

    try:
        content = DATABASE.read_text(encoding="utf-8").strip()
        if not content:
            return {"students": [], "teachers": []}

        loaded = json.loads(content)

        if not isinstance(loaded, dict):
            raise ValueError("Database must be a JSON object.")

        loaded.setdefault("students", [])
        loaded.setdefault("teachers", [])

        for student in loaded["students"]:
            student.setdefault("grades", [])
            if not isinstance(student["grades"], list):
                student["grades"] = []

        if not isinstance(loaded["students"], list):
            raise ValueError("Students must be a list.")
        if not isinstance(loaded["teachers"], list):
            raise ValueError("Teachers must be a list.")

        return loaded

    except (OSError, json.JSONDecodeError, ValueError) as error:
        st.error(f"Database error: {error}")
        st.stop()


if "data" not in st.session_state:
    st.session_state.data = load_data()

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"

if "register_type" not in st.session_state:
    st.session_state.register_type = "Student"

data = st.session_state.data


def save_data():
    temp = DATABASE.with_suffix(".tmp")
    try:
        temp.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        temp.replace(DATABASE)
        return True
    except OSError as error:
        st.error(f"Unable to save database: {error}")
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
        return False


# =========================================================
# HELPERS
# =========================================================

def navigate_to(page):
    st.session_state.nav_page = page


def open_registration(person_type):
    st.session_state.register_type = person_type
    st.session_state.nav_page = "Register a person"


def generate_id(person_type):
    prefix = "STU" if person_type == "Student" else "TCH"
    records = data["students"] if person_type == "Student" else data["teachers"]
    existing = {str(r.get("id", "")) for r in records}
    number = 1

    while f"{prefix}{number:04d}" in existing:
        number += 1

    return f"{prefix}{number:04d}"


def find_student(student_id):
    return next(
        (s for s in data["students"]
         if str(s.get("id", "")) == str(student_id)),
        None
    )


def search_records(records, query):
    query = query.strip().lower()
    if not query:
        return []

    results = []
    for record in records:
        text = " ".join(
            str(value)
            for key, value in record.items()
            if key != "grades"
        ).lower()

        if query in text:
            results.append(record)

    return results


def student_label(student):
    return (
        f"{student.get('id', 'N/A')} — "
        f"{student.get('name', 'Unknown')} "
        f"({student.get('email', '')})"
    )


def grade_average(grades):
    percentages = []

    for grade in grades:
        try:
            obtained = float(grade.get("marks_obtained", 0))
            maximum = float(grade.get("max_marks", 0))
            if maximum > 0:
                percentages.append(obtained / maximum * 100)
        except (ValueError, TypeError):
            continue

    return sum(percentages) / len(percentages) if percentages else None


def display_records(records, columns):
    if not records:
        st.info("No matching records found.")
        return

    st.dataframe(
        [
            {column: record.get(column, "") for column in columns}
            for record in records
        ],
        use_container_width=True,
        hide_index=True
    )


def show_student_details(student):
    st.subheader(f"{student.get('name', '')} — {student.get('id', '')}")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Email:** {student.get('email', 'N/A')}")
        st.write(f"**Phone:** {student.get('phone', 'N/A')}")
        st.write(f"**Course:** {student.get('course', 'N/A')}")

    with col2:
        st.write(f"**Department:** {student.get('department', 'N/A')}")
        st.write(f"**Registered:** {student.get('created_at', 'N/A')}")

    grades = student.get("grades", [])
    average = grade_average(grades)

    m1, m2 = st.columns(2)
    m1.metric("Subjects", len(grades))
    m2.metric(
        "Average Percentage",
        f"{average:.2f}%" if average is not None else "N/A"
    )

    st.markdown("**Subject-wise Grades**")

    if grades:
        rows = []
        for grade in grades:
            obtained = float(grade.get("marks_obtained", 0))
            maximum = float(grade.get("max_marks", 0))
            percentage = obtained / maximum * 100 if maximum else 0

            rows.append({
                "Subject": grade.get("subject", ""),
                "Marks Obtained": obtained,
                "Maximum Marks": maximum,
                "Percentage": f"{percentage:.2f}%"
            })

        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No grades have been entered for this student.")


def metric_card(icon, label, value, description, color):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <span class="metric-icon"
                    style="background:{color}18;color:{color}">
                    {html.escape(icon)}
                </span>
                <span class="metric-label">{html.escape(label)}</span>
            </div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-description">{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
.stApp {background:#F4F7FC;color:#1E293B}
[data-testid="stHeader"] {background:#F4F7FC}
.block-container {max-width:1500px;padding-top:2rem;padding-bottom:2rem}
h1,h2,h3,h4,h5,h6 {color:#172B4D!important}
p,li,label {color:#334155}
[data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #DCE4EF}
[data-testid="stSidebar"] * {color:#24344D}
.page-subtitle {color:#52627A!important;margin-top:-8px;margin-bottom:24px}
.section-heading {color:#172B4D!important;font-size:1.15rem;font-weight:700}
.metric-card {background:#FFFFFF;border:1px solid #DCE4EF;border-radius:16px;padding:20px;min-height:150px}
.metric-top {display:flex;align-items:center;gap:12px;margin-bottom:15px}
.metric-icon {width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:21px}
.metric-label {color:#475569!important;font-weight:650}
.metric-value {color:#172B4D!important;font-size:2rem;font-weight:750}
.metric-description {color:#64748B!important;font-size:.8rem}
.stTextInput input,.stTextArea textarea,.stNumberInput input {
    background:#FFFFFF!important;color:#172B4D!important;
    -webkit-text-fill-color:#172B4D!important;border:1px solid #B8C5D8!important
}
.stTextInput input::placeholder {color:#64748B!important;-webkit-text-fill-color:#64748B!important;opacity:1}
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] * {
    background-color:#FFFFFF!important;color:#172B4D!important;
    -webkit-text-fill-color:#172B4D!important
}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"] {background:#FFFFFF!important}
[role="option"],[role="option"] * {
    background:#FFFFFF!important;color:#172B4D!important;
    -webkit-text-fill-color:#172B4D!important
}
[role="option"]:hover,[role="option"][aria-selected="true"] {background:#E8EEFF!important}
.stButton>button {
    background:#FFFFFF!important;color:#263B60!important;
    border:1px solid #C9D4E4!important;border-radius:9px;min-height:42px
}
.stButton>button:hover {background:#EAF0FF!important;color:#253B91!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {
    background:#4054B2!important;color:#FFFFFF!important;border-color:#4054B2!important
}
[data-testid="stForm"] {background:#FFFFFF;padding:20px;border:1px solid #DCE4EF;border-radius:14px}
[data-testid="stMetric"] {background:#FFFFFF;border:1px solid #DCE4EF;border-radius:12px;padding:15px}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] p {color:#52627A!important}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] div {color:#172B4D!important}
[data-testid="stDataFrame"] {background:#FFFFFF;border:1px solid #DCE4EF;border-radius:12px}
[data-testid="stAlert"] p {color:#24344D!important}
hr {border-color:#DCE4EF!important}
.app-footer {text-align:center;color:#64748B!important;font-size:.8rem;padding-top:12px}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.title("🎓 Student Portal")
    st.caption("STUDENT MANAGEMENT SYSTEM")
    st.divider()

    st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Register a person",
            "View Students",
            "View Teachers",
            "Search Records",
            "Student Grades",
            "Delete Records"
        ],
        key="nav_page"
    )

    st.divider()
    st.markdown("**DATABASE OVERVIEW**")
    st.caption(f"🎓 Students: {len(data['students'])}")
    st.caption(f"📚 Teachers: {len(data['teachers'])}")
    st.divider()
    st.caption("Version 4.0 · Streamlit")


page = st.session_state.nav_page


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":
    st.markdown('<div class="section-heading">OVERVIEW</div>', unsafe_allow_html=True)
    st.title("Student Dashboard")
    st.markdown(
        '<div class="page-subtitle">Manage students, teachers and academic grades.</div>',
        unsafe_allow_html=True
    )

    students_count = len(data["students"])
    teachers_count = len(data["teachers"])
    total_people = students_count + teachers_count

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🎓", "Total Students", students_count, "Registered students", "#4F65D5")
    with c2:
        metric_card("📚", "Total Teachers", teachers_count, "Registered teachers", "#159B91")
    with c3:
        metric_card("👥", "Total People", total_people, "Students and teachers", "#8863CE")

    st.divider()
    st.markdown("### Quick Actions")

    a, b, c = st.columns(3)

    with a:
        st.button("＋ Register Student", use_container_width=True,
                  on_click=open_registration, args=("Student",))
    with b:
        st.button("＋ Register Teacher", use_container_width=True,
                  on_click=open_registration, args=("Teacher",))
    with c:
        st.button("View Student Grades", use_container_width=True,
                  on_click=navigate_to, args=("Student Grades",))

    st.divider()
    left, right = st.columns([1.7, 1])

    with left:
        st.markdown("### Recent Students")
        if data["students"]:
            display_records(
                data["students"][-5:][::-1],
                ["id", "name", "course", "email"]
            )
        else:
            st.info("No students registered yet.")

    with right:
        st.markdown("### System Summary")
        with st.container(border=True):
            st.metric("Total Registered People", total_people)
            st.write(f"Students: {students_count}")
            st.progress(students_count / total_people if total_people else 0)
            st.write(f"Teachers: {teachers_count}")
            st.progress(teachers_count / total_people if total_people else 0)


# =========================================================
# REGISTRATION
# =========================================================

elif page == "Register a person":
    st.title("Register a Person")
    st.markdown("Add a student or teacher to the database.")

    person_type = st.radio(
        "Person Type", ["Student", "Teacher"],
        horizontal=True, key="register_type"
    )

    with st.form("registration_form", clear_on_submit=True):
        st.subheader(f"{person_type} Information")
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
        phone = st.text_input("Phone Number")

        if person_type == "Student":
            course = st.text_input("Course *")
            department = st.text_input("Department")
        else:
            subject = st.text_input("Subject *")
            qualification = st.text_input("Qualification")
            department = st.text_input("Department")

        submitted = st.form_submit_button(
            f"Register {person_type}", type="primary", use_container_width=True
        )

        if submitted:
            if not name.strip():
                st.error("Enter the full name.")
            elif "@" not in email.strip() or "." not in email.strip().split("@")[-1]:
                st.error("Enter a valid email address.")
            elif person_type == "Student" and not course.strip():
                st.error("Enter the student's course.")
            elif person_type == "Teacher" and not subject.strip():
                st.error("Enter the teacher's subject.")
            else:
                all_records = data["students"] + data["teachers"]
                duplicate = any(
                    r.get("email", "").strip().lower() == email.strip().lower()
                    for r in all_records
                )

                if duplicate:
                    st.error("This email is already registered.")
                else:
                    record = {
                        "id": generate_id(person_type),
                        "name": name.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                        "department": department.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    if person_type == "Student":
                        record["course"] = course.strip()
                        record["grades"] = []
                        data["students"].append(record)
                    else:
                        record["subject"] = subject.strip()
                        record["qualification"] = qualification.strip()
                        data["teachers"].append(record)

                    if save_data():
                        st.success(f"{person_type} registered! ID: {record['id']}")


# =========================================================
# VIEW STUDENTS — SEARCH FIRST, THEN SHOW FULL DETAILS
# =========================================================

elif page == "View Students":
    st.title("View Students")
    st.markdown("Search for a student to view their complete profile and grades.")

    query = st.text_input(
        "Search Student",
        placeholder="Enter student name, ID, email or course",
        key="view_students_search"
    )

    if query.strip():
        results = search_records(data["students"], query)

        if results:
            st.success(f"{len(results)} matching student(s) found.")

            # Choose the matching result by clicking a radio option.
            chosen_label = st.radio(
                "Click a student to view complete details",
                options=[student_label(s) for s in results],
                key="view_students_result"
            )

            chosen_id = chosen_label.split(" — ", 1)[0]
            chosen_student = find_student(chosen_id)

            if chosen_student:
                st.divider()
                show_student_details(chosen_student)
        else:
            st.warning("No student matches your search.")
    else:
        st.info("Enter a search term above. Student records will appear after searching.")


# =========================================================
# VIEW TEACHERS — SEARCH FIRST, THEN SHOW FULL DETAILS
# =========================================================

elif page == "View Teachers":
    st.title("View Teachers")
    st.markdown("Search for a teacher to view their complete profile.")

    query = st.text_input(
        "Search Teacher",
        placeholder="Enter teacher name, ID, email or subject",
        key="view_teachers_search"
    )

    if query.strip():
        results = search_records(data["teachers"], query)

        if results:
            st.success(f"{len(results)} matching teacher(s) found.")

            chosen_label = st.radio(
                "Click a teacher to view complete details",
                options=[
                    f"{t.get('id', 'N/A')} — {t.get('name', 'Unknown')} "
                    f"({t.get('email', '')})"
                    for t in results
                ],
                key="view_teachers_result"
            )

            chosen_id = chosen_label.split(" — ", 1)[0]
            teacher = next(
                (t for t in data["teachers"]
                 if str(t.get("id", "")) == chosen_id),
                None
            )

            if teacher:
                st.divider()
                st.subheader(f"{teacher.get('name', '')} — {teacher.get('id', '')}")

                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Email:** {teacher.get('email', 'N/A')}")
                    st.write(f"**Phone:** {teacher.get('phone', 'N/A')}")
                    st.write(f"**Subject:** {teacher.get('subject', 'N/A')}")
                with c2:
                    st.write(f"**Qualification:** {teacher.get('qualification', 'N/A')}")
                    st.write(f"**Department:** {teacher.get('department', 'N/A')}")
                    st.write(f"**Registered:** {teacher.get('created_at', 'N/A')}")
        else:
            st.warning("No teacher matches your search.")
    else:
        st.info("Enter a search term above. Teacher records will appear after searching.")


# =========================================================
# SEARCH RECORDS
# =========================================================

elif page == "Search Records":
    st.title("Search Records")

    record_type = st.radio(
        "Search in", ["All", "Students", "Teachers"], horizontal=True
    )

    query = st.text_input(
        "Search",
        placeholder="Enter name, ID, email, course or subject"
    )

    if query.strip():
        if record_type == "Students":
            results = search_records(data["students"], query)
            display_records(results, ["id", "name", "email", "phone", "course", "department"])

        elif record_type == "Teachers":
            results = search_records(data["teachers"], query)
            display_records(results, ["id", "name", "email", "phone", "subject", "qualification"])

        else:
            students = search_records(data["students"], query)
            teachers = search_records(data["teachers"], query)
            combined = (
                [{"type": "Student", **s} for s in students]
                + [{"type": "Teacher", **t} for t in teachers]
            )
            display_records(combined, ["type", "id", "name", "email", "phone"])

        st.caption(f"{len(results) if record_type != 'All' else len(combined)} matching record(s).")
    else:
        st.info("Enter a search term to display matching records.")


# =========================================================
# STUDENT GRADES — SEARCH STUDENT, THEN MANAGE GRADES
# =========================================================

elif page == "Student Grades":
    st.title("Student Grades Management")
    st.markdown("Search for a student first. Then add, update or delete their subject grades.")

    query = st.text_input(
        "Find Student",
        placeholder="Type student name, ID, email or course",
        key="grades_student_search"
    )

    if not query.strip():
        st.info("Start typing a student's name or ID to find them.")
    else:
        results = search_records(data["students"], query)

        if not results:
            st.warning("No student matches your search.")
        else:
            st.success(f"{len(results)} matching student(s) found.")

            chosen_label = st.radio(
                "Select student",
                options=[student_label(s) for s in results],
                key="grades_student_result"
            )

            chosen_id = chosen_label.split(" — ", 1)[0]
            student = find_student(chosen_id)

            if student:
                student.setdefault("grades", [])
                grades = student["grades"]

                st.divider()
                st.subheader(f"{student.get('name', '')} — {student.get('id', '')}")

                st.write(f"**Course:** {student.get('course', 'N/A')}")
                st.write(f"**Email:** {student.get('email', 'N/A')}")

                average = grade_average(grades)
                total_obtained = sum(float(g.get("marks_obtained", 0)) for g in grades)
                total_max = sum(float(g.get("max_marks", 0)) for g in grades)

                c1, c2, c3 = st.columns(3)
                c1.metric("Subjects", len(grades))
                c2.metric("Average Percentage", f"{average:.2f}%" if average is not None else "N/A")
                c3.metric("Total Marks", f"{total_obtained:g} / {total_max:g}")

                st.subheader("Subject-wise Results")

                if grades:
                    rows = []
                    for g in grades:
                        obtained = float(g.get("marks_obtained", 0))
                        maximum = float(g.get("max_marks", 0))
                        percent = obtained / maximum * 100 if maximum else 0

                        rows.append({
                            "Subject": g.get("subject", ""),
                            "Marks Obtained": obtained,
                            "Maximum Marks": maximum,
                            "Percentage": f"{percent:.2f}%"
                        })

                    st.dataframe(rows, use_container_width=True, hide_index=True)
                else:
                    st.info("No grades entered for this student yet.")

                # ADD GRADE
                st.divider()
                st.subheader("Add Subject Grade")

                with st.form(f"add_grade_{chosen_id}", clear_on_submit=True):
                    subject = st.text_input("Subject Name *")
                    a, b = st.columns(2)

                    with a:
                        obtained = st.number_input(
                            "Marks Obtained", min_value=0.0,
                            max_value=100000.0, value=0.0, step=1.0
                        )

                    with b:
                        maximum = st.number_input(
                            "Maximum Marks", min_value=1.0,
                            max_value=100000.0, value=100.0, step=1.0
                        )

                    add = st.form_submit_button(
                        "Add Grade", type="primary", use_container_width=True
                    )

                    if add:
                        if not subject.strip():
                            st.error("Enter a subject name.")
                        elif obtained > maximum:
                            st.error("Marks obtained cannot exceed maximum marks.")
                        elif any(
                            g.get("subject", "").strip().lower() == subject.strip().lower()
                            for g in grades
                        ):
                            st.error("This subject already exists. Use Update Grade.")
                        else:
                            grades.append({
                                "subject": subject.strip(),
                                "marks_obtained": obtained,
                                "max_marks": maximum,
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })

                            if save_data():
                                st.success("Grade added successfully.")
                                st.rerun()

                # UPDATE GRADE
                st.divider()
                st.subheader("Update Grade")

                if grades:
                    subject_names = [g.get("subject", "") for g in grades]
                    chosen_subject = st.radio(
                        "Choose subject to update",
                        subject_names,
                        key=f"update_subject_{chosen_id}"
                    )
                    grade_index = subject_names.index(chosen_subject)
                    old_grade = grades[grade_index]

                    with st.form(f"update_grade_{chosen_id}_{grade_index}"):
                        updated_subject = st.text_input(
                            "Subject Name",
                            value=old_grade.get("subject", "")
                        )
                        u1, u2 = st.columns(2)

                        with u1:
                            updated_obtained = st.number_input(
                                "Updated Marks Obtained",
                                min_value=0.0, max_value=100000.0,
                                value=float(old_grade.get("marks_obtained", 0)),
                                step=1.0
                            )

                        with u2:
                            updated_maximum = st.number_input(
                                "Updated Maximum Marks",
                                min_value=1.0, max_value=100000.0,
                                value=max(1.0, float(old_grade.get("max_marks", 100))),
                                step=1.0
                            )

                        update = st.form_submit_button(
                            "Save Grade Changes",
                            type="primary",
                            use_container_width=True
                        )

                        if update:
                            duplicate = any(
                                i != grade_index
                                and g.get("subject", "").strip().lower()
                                == updated_subject.strip().lower()
                                for i, g in enumerate(grades)
                            )

                            if not updated_subject.strip():
                                st.error("Subject name cannot be empty.")
                            elif updated_obtained > updated_maximum:
                                st.error("Marks obtained cannot exceed maximum marks.")
                            elif duplicate:
                                st.error("Another grade already uses this subject name.")
                            else:
                                previous = old_grade.copy()
                                old_grade.update({
                                    "subject": updated_subject.strip(),
                                    "marks_obtained": updated_obtained,
                                    "max_marks": updated_maximum,
                                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })

                                if save_data():
                                    st.success("Grade updated.")
                                    st.rerun()
                                else:
                                    old_grade.clear()
                                    old_grade.update(previous)

                    # DELETE GRADE
                    st.divider()
                    st.subheader("Delete Subject Grade")

                    delete_subject = st.radio(
                        "Choose subject to delete",
                        [g.get("subject", "") for g in grades],
                        key=f"delete_subject_{chosen_id}"
                    )

                    confirm = st.checkbox(
                        f"Confirm deletion of {delete_subject}",
                        key=f"confirm_grade_delete_{chosen_id}"
                    )

                    if st.button(
                        "Delete Subject Grade",
                        type="primary",
                        use_container_width=True,
                        key=f"delete_grade_{chosen_id}"
                    ):
                        if not confirm:
                            st.warning("Confirm before deleting.")
                        else:
                            idx = next(
                                i for i, g in enumerate(grades)
                                if g.get("subject", "") == delete_subject
                            )
                            removed = grades.pop(idx)

                            if save_data():
                                st.success("Subject grade deleted.")
                                st.rerun()
                            else:
                                grades.insert(idx, removed)
                else:
                    st.info("Add a grade first to update or delete it.")


# =========================================================
# DELETE STUDENT / TEACHER
# =========================================================

elif page == "Delete Records":
    st.title("Delete Records")
    st.markdown("Search for a student or teacher before deleting.")

    person_type = st.radio(
        "Record Type", ["Student", "Teacher"], horizontal=True
    )
    query = st.text_input(
        "Search Record",
        placeholder="Type a name, ID or email"
    )

    records = data["students"] if person_type == "Student" else data["teachers"]

    if query.strip():
        results = search_records(records, query)

        if results:
            chosen_label = st.radio(
                "Select record to delete",
                [
                    f"{r.get('id', 'N/A')} — {r.get('name', 'Unknown')} "
                    f"({r.get('email', '')})"
                    for r in results
                ],
                key="delete_record_search_result"
            )

            selected_id = chosen_label.split(" — ", 1)[0]
            st.caption(f"Selected ID: {selected_id}")

            confirm = st.checkbox(
                "I confirm that I want to permanently delete this record.",
                key="confirm_record_delete"
            )

            if st.button(
                "Delete Selected Record",
                type="primary",
                use_container_width=True
            ):
                if not confirm:
                    st.warning("Please confirm before deleting.")
                else:
                    original = records.copy()
                    records[:] = [
                        r for r in records
                        if str(r.get("id", "")) != selected_id
                    ]

                    if save_data():
                        st.success(f"{person_type} {selected_id} deleted.")
                        st.rerun()
                    else:
                        records[:] = original
        else:
            st.warning("No matching record found.")
    else:
        st.info("Search by name, ID or email to display records for deletion.")


# =========================================================
# FOOTER
# =========================================================

st.divider()
st.markdown(
    '<div class="app-footer">Student Management System · Python & Streamlit</div>',
    unsafe_allow_html=True
)
