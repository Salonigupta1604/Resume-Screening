import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from database.db import init_db, connect_db
from services.auth_service import register_user, login_user
from services.ai_service import analyze_resume
from utils.pdf_parser import extract_text_from_pdf

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# FLOATING PARTICLES
# =====================================================

particles_js = """
<!DOCTYPE html>
<html>
<head>

<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>

<style>

#particles-js {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
    top: 0;
    left: 0;
    background: transparent;
}

</style>

</head>

<body>

<div id="particles-js"></div>

<script>

particlesJS("particles-js", {

  "particles": {

    "number": {
      "value": 90,
      "density": {
        "enable": true,
        "value_area": 800
      }
    },

    "color": {
      "value": "#00FFFF"
    },

    "shape": {
      "type": "circle"
    },

    "opacity": {
      "value": 0.5,
      "random": true
    },

    "size": {
      "value": 3,
      "random": true
    },

    "line_linked": {
      "enable": true,
      "distance": 150,
      "color": "#00FFFF",
      "opacity": 0.4,
      "width": 1
    },

    "move": {
      "enable": true,
      "speed": 2,
      "direction": "none",
      "random": false,
      "straight": false,
      "out_mode": "out",
      "bounce": false
    }
  },

  "interactivity": {

    "detect_on": "canvas",

    "events": {

      "onhover": {
        "enable": true,
        "mode": "grab"
      },

      "onclick": {
        "enable": true,
        "mode": "push"
      }

    },

    "modes": {

      "grab": {
        "distance": 140,
        "line_linked": {
          "opacity": 1
        }
      },

      "push": {
        "particles_nb": 4
      }

    }

  },

  "retina_detect": true

});

</script>

</body>
</html>
"""

components.html(
    particles_js,
    height=0,
    width=0
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background-image: url("https://thumbs.dreamstime.com/b/ai-machine-learning-hands-robot-human-touching-big-data-network-connection-background-science-artificial-intelligence-172987598.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* DARK OVERLAY */

[data-testid="stAppViewContainer"] {
    background: rgba(0,0,0,0.72);
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: rgba(20,20,20,0.90);
    backdrop-filter: blur(12px);
}

/* TITLE */

.title {
    text-align: center;
    font-size: 50px;
    font-weight: bold;
    color: white;
    margin-top: 20px;
}

.subtitle {
    text-align: center;
    color: #cccccc;
    font-size: 18px;
    margin-bottom: 30px;
}

/* BUTTONS */

.stButton>button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
    background: linear-gradient(90deg,#00C9FF,#92FE9D);
    color: black;
    font-size: 16px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.03);
    transition: 0.3s;
    box-shadow: 0 0 15px #00FFFF;
}

/* INPUT FIELDS */

.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.08);
    color: white;
    border-radius: 10px;
}

.stTextArea textarea {
    background-color: rgba(255,255,255,0.08);
    color: white;
    border-radius: 10px;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08);
    border-radius: 10px;
}

/* RADIO BUTTONS */

.stRadio label {
    color: white !important;
}

/* CARDS */

.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

/* METRIC CARDS */

.metric-card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.15);
}

/* TABLE */

[data-testid="stDataFrame"] {
    background-color: rgba(255,255,255,0.05);
    border-radius: 15px;
}

/* FILE UPLOADER */

[data-testid="stFileUploader"] {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
}

/* SUCCESS MESSAGE */

.stSuccess {
    border-radius: 10px;
}

/* WARNING MESSAGE */

.stWarning {
    border-radius: 10px;
}

/* REMOVE EXTRA STREAMLIT ELEMENTS */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# DATABASE INIT
# =====================================================

init_db()

# =====================================================
# SESSION STATE
# =====================================================

if "user" not in st.session_state:
    st.session_state.user = None

# =====================================================
# LOGIN / REGISTER PAGE
# =====================================================

if st.session_state.user is None:

    st.markdown(
        "<div class='title'>😊 AI Resume Screening System</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='subtitle'>Smart AI Hiring Platform for Modern Companies</div>",
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1,2,1])

    with center:

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        option = st.radio(
            "Choose Option",
            ["Login", "Register"]
        )

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        # REGISTER

        if option == "Register":

            role = st.selectbox(
                "Register As",
                ["admin", "applicant"]
            )

            if st.button("Create Account"):

                if register_user(
                    username,
                    password,
                    role
                ):
                    st.success("✅ Account Created Successfully")

                else:
                    st.error("❌ Username already exists")

        # LOGIN

        else:

            if st.button("Login"):

                user = login_user(
                    username,
                    password
                )

                if user:

                    st.session_state.user = user
                    st.rerun()

                else:
                    st.error("❌ Invalid Credentials")

        st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# MAIN DASHBOARD
# =====================================================

else:

    user = st.session_state.user

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.title("😊 AI Hiring")

    st.sidebar.success(
        f"{user['username']} ({user['role']})"
    )
    if user["role"] == "admin":
        menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Jobs",
            "Applications",
            "AI Shortlisting",
            "Resume Analyzer"
        ]
    )
    else:
        menu = st.sidebar.radio(
        "Navigation",
        ["Apply Job"]
    )

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # =====================================================
    # ADMIN PANEL
    # =====================================================

    if user["role"] == "admin":

        # DASHBOARD

        if menu == "Dashboard":

            st.title("📊 Admin Dashboard")

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM jobs
                           WHERE recruiter_id=%s
                           """,(user["id"],))
            total_jobs = cursor.fetchone()[0]

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM applications
                           WHERE recruiter_id=%s
                           """,(user["id"],))
            total_apps = cursor.fetchone()[0]

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM applications
                           WHERE recruiter_id=%s
                           """,(user["id"],))

            shortlisted = cursor.fetchone()[0]

            cursor.execute("""
                           SELECT COUNT(*)
                           FROM applications
                           WHERE recruiter_id=%s
                           AND status='Shortlisted'
                           """,(user["id"],))
            shortlisted = cursor.fetchone()[0]

            conn.close()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class='metric-card'>
                    <h1>{total_jobs}</h1>
                    <p>Total Jobs</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class='metric-card'>
                    <h1>{total_apps}</h1>
                    <p>Total Applications</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class='metric-card'>
                    <h1>{shortlisted}</h1>
                    <p>Shortlisted</p>
                </div>
                """, unsafe_allow_html=True)

        # JOBS

        elif menu == "Jobs":

            st.title("📝 Create Job")

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            company_name = st.text_input(
                "Company Name"
            )

            title = st.text_input("Job Title")

            description = st.text_area(
                "Job Description"
            )

            if st.button("Create Job"):

                conn = connect_db()
                cursor = conn.cursor()

                cursor.execute("""
                               INSERT INTO jobs(
                               recruiter_id,
                               company_name,
                               title,
                               description
                               )
                               VALUES(%s,%s,%s,%s)
                               """,(
                                   user["id"],
                                   company_name,
                                   title,
                                   description
                                   ))

                conn.commit()
                conn.close()

                st.success("✅ Job Created Successfully")

            st.markdown("</div>", unsafe_allow_html=True)

        # APPLICATIONS

        elif menu == "Applications":

            st.title("📂 Applications")

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                           SELECT applicant_name,
                           score,
                           status
                           FROM applications
                           WHERE recruiter_id=%s
                           """,(user["id"],))

            data = cursor.fetchall()

            conn.close()

            if data:

                df = pd.DataFrame(
                    data,
                    columns=[
                        "Applicant",
                        "Score",
                        "Status"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

            else:
                st.warning("No applications found")

        # AI SHORTLISTING

        elif menu == "AI Shortlisting":

            st.title("🤖 AI Resume Shortlisting")

            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("""
                           SELECT id,title
                           FROM jobs
                           WHERE recruiter_id=%s
                           """,(user["id"],))

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

                if st.button("Run AI Screening"):

                    cursor.execute("""
                    SELECT id,
                           applicant_name,
                           resume_text
                    FROM applications
                    WHERE job_id=%s
                    """, (job_id,))

                    applications = cursor.fetchall()

                    cursor.execute("""
                    SELECT description
                    FROM jobs
                    WHERE id=%s
                    """, (job_id,))

                    job_description = cursor.fetchone()[0]

                    ranked_candidates = []

                    progress = st.progress(0)

                    for i, app in enumerate(applications):

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

                        cursor.execute("""
                        UPDATE applications
                        SET score=%s,
                            reasoning=%s,
                            status=%s
                        WHERE id=%s
                        """, (
                            score,
                            reasoning,
                            "Shortlisted" if score >= 60 else "Rejected",
                            app_id
                        ))

                        progress.progress(
                            (i + 1) / len(applications)
                        )

                    conn.commit()
                    conn.close()

                    ranked_candidates.sort(
                        key=lambda x: x["score"],
                        reverse=True
                    )

                    st.success("✅ AI Screening Completed")

                    st.subheader("🏆 Top Candidates")

                    for candidate in ranked_candidates[:10]:

                        st.markdown(f"""
                        <div class='card'>
                            <h2>{candidate['name']}</h2>
                            <h1>Match Score: {candidate['score']}%</h1>
                            <p>{candidate['reasoning']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            else:
                st.warning("No jobs available")

       # =====================================================
       # RESUME ANALYZER
       # =====================================================
                
        elif menu == "Resume Analyzer":
            
            st.title("📄 Resume Analyzer")
            uploaded_resume = st.file_uploader(
                "Upload Resume",
                type=["pdf"]
            )
            
            jd = st.text_area(
                "Paste Job Description"
            )
            if st.button("Analyze Resume"):
                if uploaded_resume and jd:
                    resume_text = extract_text_from_pdf(
                        uploaded_resume
                    )
                    
                    result = analyze_resume(
                        resume_text,
                        jd
                    )

                    st.metric(
                        "Match Score",
                        f"{result['match_score']}%"
                    )
                    
                    st.write(result["reasoning"])

# =====================================================
# APPLICANT PANEL
# =====================================================

    else:
        st.title("👨‍🎓 Applicant Dashboard")
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id,
             company_name,
             title
        FROM jobs
        """)
        jobs = cursor.fetchall()     
        conn.close()

    if jobs:

        job_dict = {
            f"{job[1]} - {job[2]}": job[0]
            for job in jobs
        }

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        apply_mode = st.radio(
            "Application Type",
            [
                "Single Company",
                "All Companies"
            ]
        )

        selected_job = st.selectbox(
            "Select Job",
            list(job_dict.keys())
        )

        uploaded_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

        if st.button("Apply Now"):

            if uploaded_file:

                resume_text = extract_text_from_pdf(
                    uploaded_file
                )

                conn = connect_db()
                cursor = conn.cursor()

                if apply_mode == "Single Company":

                    cursor.execute("""
                    SELECT recruiter_id
                    FROM jobs
                    WHERE id=%s
                    """, (job_dict[selected_job],))

                    recruiter_id = cursor.fetchone()[0]

                    cursor.execute("""
                    INSERT INTO applications(
                        applicant_name,
                        resume_text,
                        job_id,
                        recruiter_id
                    )
                    VALUES(%s,%s,%s,%s)
                    """, (
                        user["username"],
                        resume_text,
                        job_dict[selected_job],
                        recruiter_id
                    ))

                else:

                    cursor.execute("""
                    SELECT id,recruiter_id
                    FROM jobs
                    """)

                    all_jobs = cursor.fetchall()

                    for job in all_jobs:

                        cursor.execute("""
                        INSERT INTO applications(
                            applicant_name,
                            resume_text,
                            job_id,
                            recruiter_id
                        )
                        VALUES(%s,%s,%s,%s)
                        """, (
                            user["username"],
                            resume_text,
                            job[0],
                            job[1]
                        ))

                conn.commit()
                conn.close()

                st.success(
                    "✅ Application Submitted Successfully"
                )

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("No jobs available")