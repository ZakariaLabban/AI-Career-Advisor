from app.profile_app import generate_profile_summary
from utils.cv_utils import create_cv_pdf
from app.profile_app import update_profile_from_cv

import streamlit as st
import requests
import os
import openai

# OpenAI API Key
openai.api_key = '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'

# Adzuna API Credentials
ADZUNA_APP_ID = "97cb022e"
ADZUNA_APP_KEY = "b74ceb936268f0f7b8309d6f9f26728a"

# GitHub Token
GITHUB_TOKEN = "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"

# Coursera Credentials
coursera_auth_url = "https://api.coursera.com/oauth2/client_credentials/token"
coursera_payload = {
    'client_id': 'EWMCX9yMt2EolnvVHbmUrOPXgsHo1qlyj9RsACMbF6d4oJBI',
    'client_secret': 'uIPaYe2rlMt9cZ3RLHSTlqMTGu95KCy1PDJapNH6UgiKrmhtiZCESasbeWmNHC2z',
    'grant_type': 'client_credentials'
}
coursera_response = requests.post(coursera_auth_url, data=coursera_payload)
coursera_token = coursera_response.json().get("access_token") if coursera_response.status_code == 200 else ""

def build_cv():
    st.markdown("""
    <style>
    .header {
        font-size: 2.5em;
        text-align: center;
        color: #4B8BBE;
    }
    .subheader {
        font-size: 1.5em;
        color: #2E86AB;
    }
    .button {
        background-color: #4B8BBE;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border: none;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header">Create a Professional CV in Minutes</div>
    <hr>
    <div style="text-align: center;">
        <p>Follow the steps below to build and download your personalized CV.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for dynamic fields
    for key, default in {
        'language_count': 1,
        'skill_count': 1,
        'education_count': 1,
        'experience_count': 1,
        'award_count': 1,
        'project_count': 1
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    with st.form(key='cv_form'):
        tab1, tab2, tab3 = st.tabs(["Basic Info", "Skills & Languages", "Experience"])

        with tab1:
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", "")
                job_title = st.text_input("Job Title or Major", "")
                email = st.text_input("Email Address", "")
            with col2:
                phone = st.text_input("Phone Number", "")
                location = st.text_input("Location", "")
                dob = st.text_input("Date of Birth (e.g., 8th September 2004)", "")
                nationality = st.text_input("Nationality", "")
                linkedin = st.text_input("LinkedIn Profile URL (optional)", "")

        with tab2:
            st.subheader("Languages")
            languages = []
            for i in range(1, st.session_state.language_count + 1):
                lang_col1, lang_col2 = st.columns([3, 2])
                with lang_col1:
                    lang_name = st.text_input(f"Language {i}", key=f'lang_name_{i}')
                with lang_col2:
                    lang_level = st.selectbox(f"Level {i}", ["Basic", "Conversational", "Proficient", "Fluent", "Native/Bilingual"], key=f'lang_level_{i}')
                if lang_name and lang_level:
                    languages.append({"Language": lang_name, "Level": lang_level})
            add_language = st.form_submit_button("➕ Add Another Language")
            if add_language:
                st.session_state.language_count += 1

            st.markdown("---")

            st.subheader("Skills")
            skills = []
            for i in range(1, st.session_state.skill_count + 1):
                skill_col1, skill_col2 = st.columns([3, 2])
                with skill_col1:
                    skill_name = st.text_input(f"Skill {i}", key=f'skill_name_{i}')
                with skill_col2:
                    skill_level = st.selectbox(f"Level {i}", ["Beginner", "Amateur", "Competent", "Proficient", "Expert"], key=f'skill_level_{i}')
                if skill_name and skill_level:
                    skills.append({"skill": skill_name, "level": skill_level})
            add_skill = st.form_submit_button("➕ Add Another Skill")
            if add_skill:
                st.session_state.skill_count += 1

        with tab3:
            st.subheader("Education")
            education = []
            for i in range(1, st.session_state.education_count + 1):
                edu_col1, edu_col2 = st.columns(2)
                with edu_col1:
                    degree = st.text_input(f"Degree {i}", key=f'edu_degree_{i}')
                    institution = st.text_input(f"Institution {i}", key=f'edu_institution_{i}')
                with edu_col2:
                    years = st.text_input(f"Years Attended {i} (e.g., '2020 - 2024')", key=f'edu_years_{i}')
                    details = st.text_input(f"Details {i} (optional)", key=f'edu_details_{i}')
                if degree and institution and years:
                    education.append({
                        "Degree": degree,
                        "Institution": institution,
                        "Years": years,
                        "Details": details
                    })
            add_education = st.form_submit_button("➕ Add Another Education")
            if add_education:
                st.session_state.education_count += 1

            st.markdown("---")

            st.subheader("Professional Experience")
            experience = []
            for i in range(1, st.session_state.experience_count + 1):
                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    exp_title = st.text_input(f"Job Title {i}", key=f'exp_title_{i}')
                    exp_company = st.text_input(f"Company {i}", key=f'exp_company_{i}')
                with exp_col2:
                    exp_years = st.text_input(f"Years {i} (e.g., '2022 - 2023')", key=f'exp_years_{i}')
                exp_details = st.text_area(f"Responsibilities {i}", key=f'exp_details_{i}')
                if exp_title and exp_company and exp_years:
                    experience.append({
                        "Title": exp_title,
                        "Company": exp_company,
                        "Years": exp_years,
                        "Details": exp_details
                    })
            add_experience = st.form_submit_button("➕ Add Another Experience")
            if add_experience:
                st.session_state.experience_count += 1

            st.markdown("---")

            st.subheader("Awards & Projects")
            st.markdown("### Awards")
            awards = []
            for i in range(1, st.session_state.award_count + 1):
                award = st.text_input(f"Award {i}", key=f'award_{i}')
                if award:
                    awards.append(award)
            add_award = st.form_submit_button("➕ Add Another Award")
            if add_award:
                st.session_state.award_count += 1

            st.markdown("### Projects")
            projects = []
            for i in range(1, st.session_state.project_count + 1):
                proj_col1, proj_col2 = st.columns([3, 2])
                with proj_col1:
                    proj_title = st.text_input(f"Project Title {i}", key=f'proj_title_{i}')
                with proj_col2:
                    proj_description = st.text_area(f"Description {i}", key=f'proj_description_{i}')
                if proj_title and proj_description:
                    projects.append({
                        "Title": proj_title,
                        "Description": proj_description
                    })
            add_project = st.form_submit_button("➕ Add Another Project")
            if add_project:
                st.session_state.project_count += 1

        st.markdown("---")
        generate_cv = st.form_submit_button("🚀 Generate CV")

    if generate_cv:
        data = {
            "name": name,
            "job_title": job_title,
            "email": email,
            "phone": phone,
            "location": location,
            "dob": dob,
            "nationality": nationality,
            "linkedin": linkedin,
            "languages": languages,
            "skills": skills,
            "education": education,
            "experience": experience,
            "awards": awards,
            "projects": projects
        }

        with st.spinner("🧠 Generating profile summary..."):
            profile_summary = generate_profile_summary(data)

        with st.spinner("📄 Creating CV PDF..."):
            pdf_buffer = create_cv_pdf(data, profile_summary)

        update_profile_from_cv(data)

        st.success("✅ CV successfully generated.")
        st.download_button(
            label="📥 Download Your CV",
            data=pdf_buffer,
            file_name=f"{data['name'].replace(' ', '_')}_CV.pdf",
            mime="application/pdf"
        )
