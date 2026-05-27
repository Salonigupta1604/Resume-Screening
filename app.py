import streamlit as st

from database.db import init_db, connect_db
from services.auth_service import register_user, login_user
from services.ai_service import analyze_resume
from utils.pdf_parser import extract_text_from_pdf

# INIT DB
init_db()

st.set_page_config(
    page_title="AI Resume Screening",
    layout="wide"
)

# SESSION
if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN / REGISTER
# =====================================================

if st.session_state.user is None:

    st.title("🚀 AI Resume Screening System")

    menu = st.radio(
        "Select Option",
        ["Login", "Register"]
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # REGISTER
    if menu == "Register":

        role = st.selectbox(
            "Register As",
            ["admin", "applicant"]
        )

        if st.button("Register"):

            if register_user(username, password, role):
                st.success("Account Created Successfully")

            else:
                st.error("Username already exists")

    # LOGIN
    else:

        if st.button("Login"):

            user = login_user(username, password)

            if user:
                st.session_state.user = user
                st.rerun()

            else:
                st.error("Invalid Credentials")

# =====================================================
# AFTER LOGIN
# =====================================================

else:

    user = st.session_state.user

    st.sidebar.success(
        f"Logged in as: {user['username']} ({user['role']})"
    )

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # =====================================================
    # ADMIN PANEL
    # =====================================================

    if user["role"] == "admin":

        st.title("👨‍💼 Admin Dashboard")

        # CREATE JOB
        st.header("📝 Create Job")

        title = st.text_input("Job Title")

        description = st.text_area("Job Description")

        if st.button("Create Job"):

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO jobs (title, description) VALUES (?, ?)",
                (title, description)
            )

            conn.commit()
            conn.close()

            st.success("Job Created Successfully")

        st.divider()

        # VIEW JOBS
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM jobs")
        jobs = cursor.fetchall()

        if jobs:

            job_dict = {
                job[1]: job[0]
                for job in jobs
            }

            selected_job = st.selectbox(
                "Select Job",
                list(job_dict.keys())
            )

            job_id = job_dict[selected_job]

            # RUN AI SHORTLIST
            if st.button("🚀 Run AI Shortlisting"):

                conn = connect_db()
                cursor = conn.cursor()

                cursor.execute("""
                SELECT id, applicant_name, resume_text
                FROM applications
                WHERE job_id=?
                """, (job_id,))

                applications = cursor.fetchall()

                cursor.execute(
                    "SELECT description FROM jobs WHERE id=?",
                    (job_id,)
                )

                job_description = cursor.fetchone()[0]

                ranked_candidates = []

                for app in applications:

                    app_id = app[0]
                    name = app[1]
                    resume_text = app[2]

                    result = analyze_resume(
                        resume_text,
                        job_description
                    )

                    score = result["match_score"]
                    reasoning = result["reasoning"]

                    ranked_candidates.append({
                        "name": name,
                        "score": score,
                        "reasoning": reasoning
                    })

                    # UPDATE DB
                    cursor.execute("""
                    UPDATE applications
                    SET score=?, reasoning=?, status=?
                    WHERE id=?
                    """, (
                        score,
                        reasoning,
                        "Shortlisted" if score >= 60 else "Rejected",
                        app_id
                    ))

                conn.commit()
                conn.close()

                # SORT
                ranked_candidates.sort(
                    key=lambda x: x["score"],
                    reverse=True
                )

                st.header("🏆 Top Candidates")

                for candidate in ranked_candidates[:10]:

                    st.success(
                        f"{candidate['name']} — {candidate['score']}%"
                    )

                    st.write(candidate["reasoning"])

                st.header("❌ Rejected")

                for candidate in ranked_candidates:

                    if candidate["score"] < 60:

                        st.error(
                            f"{candidate['name']} — {candidate['score']}%"
                        )

    # =====================================================
    # APPLICANT PANEL
    # =====================================================

    else:

        st.title("👨‍🎓 Applicant Dashboard")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM jobs")

        jobs = cursor.fetchall()

        conn.close()

        if jobs:

            job_dict = {
                job[1]: job[0]
                for job in jobs
            }

            selected_job = st.selectbox(
                "Select Job",
                list(job_dict.keys())
            )

            uploaded_file = st.file_uploader(
                "Upload Resume PDF",
                type=["pdf"]
            )

            if st.button("Apply"):

                if uploaded_file:

                    resume_text = extract_text_from_pdf(
                        uploaded_file
                    )

                    conn = connect_db()
                    cursor = conn.cursor()

                    cursor.execute("""
                    INSERT INTO applications
                    (applicant_name, resume_text, job_id)
                    VALUES (?, ?, ?)
                    """, (
                        user["username"],
                        resume_text,
                        job_dict[selected_job]
                    ))

                    conn.commit()
                    conn.close()

                    st.success(
                        "Application Submitted Successfully"
                    )

        else:
            st.warning("No jobs available")