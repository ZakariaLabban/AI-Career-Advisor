# career_advisor_app.py

from utils.file_utils import extract_text
from data.profile_data import (
    extract_education,
    extract_experience,
    extract_languages,
    extract_awards,
    extract_projects
)
from utils.resume_utils import (
    determine_user_level,
    get_country_code_and_location,
    extract_personal_info,
    extract_skills
)

from app.profile_app import update_profile_from_career_advisor
from data.profile_data import (
    generate_job_path,
    generate_course_path,
    generate_project_path
)
import streamlit as st
from data.api_data import (
    search_courses_on_coursera,
    search_jobs_on_adzuna,
    search_github_projects
)

import textwrap
import requests
import openai
import json

# **Security Note:** It's highly recommended to store API keys securely using Streamlit's Secrets Management.
# However, as per your request, the keys are included directly here.
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

def display_recommendations(job_path, course_details, project_path, location, country_code):
    """Displays the recommendations."""
    st.subheader("📈 Suggested Career Path")
    for i in range(4):
        if i >= len(job_path):
            continue
        job_title = job_path[i]
        with st.expander(f"📌 **Stage {i+1}: {job_title}**"):
            tab1, tab2, tab3 = st.tabs(["💼 Jobs", "📚 Courses", "💻 Projects"])

            with tab1:
                st.markdown("**🔍 Job Listings:**")
                job_results = search_jobs_on_adzuna(
                    job_title,
                    location,
                    country_code
                )
                if job_results:
                    for job in job_results:
                        st.markdown(f"### {job.get('title', 'N/A')}")
                        st.markdown(f"- **🏢 Company:** {job.get('company', {}).get('display_name', 'N/A')}")
                        st.markdown(f"- **📍 Location:** {job.get('location', {}).get('display_name', 'N/A')}")
                        st.markdown(f"- **📝 Description:** {textwrap.fill(job.get('description', 'N/A'), width=80)}")
                        st.markdown(f"- **💰 Salary Min:** {job.get('salary_min', 'N/A')}")
                        st.markdown(f"- **💰 Salary Max:** {job.get('salary_max', 'N/A')}")
                        st.markdown(f"- **🔗 URL:** [Link]({job.get('redirect_url', '#')})")
                        st.markdown("---")
                else:
                    st.markdown("❌ No job listings found.")

            with tab2:
                st.markdown("**📚 Recommended Courses:**")
                if i < len(course_details):
                    course = course_details[i]
                    if course.get('url', "#") != "#":
                        st.markdown(f"### {course.get('title', 'N/A')}")
                        st.markdown(f"- **🔗 URL:** [Link]({course.get('url')})")
                        st.markdown(f"- **📝 Description:** {textwrap.fill(course.get('description', 'N/A'), width=80)}")
                        st.markdown("---")
                    else:
                        st.markdown(f"### {course.get('title', 'N/A')}")
                        st.markdown(f"- **🔗 URL:** Not Available")
                        st.markdown(f"- **📝 Description:** {textwrap.fill(course.get('description', 'N/A'), width=80)}")
                        st.markdown("---")
                else:
                    st.markdown("❌ No courses found.")

            with tab3:
                st.markdown("**💻 Related GitHub Projects:**")
                projects_list = search_github_projects(job_title, GITHUB_TOKEN)
                if projects_list:
                    for project in projects_list:
                        st.markdown(f"### {project.get('name', 'N/A')}")
                        st.markdown(f"- **⭐ Stars:** {project.get('stargazers_count', 'N/A')}")
                        st.markdown(f"- **🔗 URL:** [Link]({project.get('html_url', '#')})")
                        description = project.get('description', 'No description available')
                        st.markdown(f"- **📝 Description:** {textwrap.fill(description or 'No description available', width=80)}")
                        st.markdown("---")
                else:
                    st.markdown("❌ No related GitHub projects found.")

def regenerate_recommendations(resume_text, current_feedback):
    """Regenerate recommendations based on feedback and store them in session state."""
    with st.spinner("🔄 Regenerating career recommendations based on your feedback..."):
        job_path = generate_job_path(resume_text, current_feedback)
        course_path = generate_course_path(resume_text, current_feedback)
        project_path = generate_project_path(resume_text, current_feedback)
        course_details = search_courses_on_coursera(course_path)
        
        # Store in session_state
        st.session_state.job_path = job_path
        st.session_state.course_path = course_path
        st.session_state.project_path = project_path
        st.session_state.course_details = course_details
        
        # Update profile dictionary
        if "profile" not in st.session_state:
            st.session_state.profile = {}
        st.session_state.profile["job_path"] = job_path
        st.session_state.profile["course_path"] = course_path
        st.session_state.profile["project_path"] = project_path
        st.session_state.profile["course_details"] = course_details
    
    return job_path, course_path, project_path, course_details

def generate_initial_recommendations(resume_text, current_feedback):
    """Generate initial recommendations and store them in session state."""
    with st.spinner("🔄 Generating career recommendations..."):
        job_path = generate_job_path(resume_text, current_feedback)
        course_path = generate_course_path(resume_text, current_feedback)
        project_path = generate_project_path(resume_text, current_feedback)
        course_details = search_courses_on_coursera(course_path)
        
        # Store in session_state
        st.session_state.job_path = job_path
        st.session_state.course_path = course_path
        st.session_state.project_path = project_path
        st.session_state.course_details = course_details
        
        # Update profile dictionary
        if "profile" not in st.session_state:
            st.session_state.profile = {}
        st.session_state.profile["job_path"] = job_path
        st.session_state.profile["course_path"] = course_path
        st.session_state.profile["project_path"] = project_path
        st.session_state.profile["course_details"] = course_details
    
    return job_path, course_path, project_path, course_details

def career_advisor():
    st.header("🔍 AI-Powered Career Advisor")

    st.markdown("""
    **Instructions:**
    1. 📄 Upload your CV in PDF or DOCX format.
    2. 🤖 The AI will analyze your resume to determine your career level, location, and extract your personal information, skills, education, experience, languages, awards, and projects.
    3. 🔍 Browse through recommended jobs, courses, and GitHub projects to advance your career.
    4. 📝 Provide feedback to refine the recommendations.
    """)

    # Initialize session state variables if not already set
    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""
    if 'job_path' not in st.session_state:
        st.session_state.job_path = []
    if 'course_path' not in st.session_state:
        st.session_state.course_path = []
    if 'project_path' not in st.session_state:
        st.session_state.project_path = []
    if 'course_details' not in st.session_state:
        st.session_state.course_details = []
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None
    if 'user_level' not in st.session_state:
        st.session_state.user_level = None
    if 'location' not in st.session_state:
        st.session_state.location = None
    if 'country_code' not in st.session_state:
        st.session_state.country_code = None
    if 'personal_info' not in st.session_state:
        st.session_state.personal_info = None
    if 'skills' not in st.session_state:
        st.session_state.skills = None
    if 'education' not in st.session_state:
        st.session_state.education = None
    if 'experience' not in st.session_state:
        st.session_state.experience = None
    if 'languages' not in st.session_state:
        st.session_state.languages = None
    if 'awards' not in st.session_state:
        st.session_state.awards = None
    if 'projects' not in st.session_state:
        st.session_state.projects = None

    current_feedback = st.session_state.get('feedback', "")
    # Feedback Section (only shown if we have resume_text and job_path)
    if st.session_state.resume_text and st.session_state.job_path:
        st.markdown("## 📢 Provide Feedback to Refine Recommendations")
        with st.form(key='feedback_form'):
            st.write("If you're not satisfied with the recommendations, please provide your feedback below:")
            question1 = st.text_input("1. ❓ Which aspect of the recommendations did you find most useful (e.g., jobs, courses, or projects)?")
            question2 = st.text_input("2. 🎯 Are there any specific industries, skills, or roles you'd like to see more focus on?")
            question3 = st.text_input("3. 🔧 Is there anything you'd like to remove or adjust in the current recommendations?")
            submit_feedback = st.form_submit_button(label='📝 Submit Feedback')

            if submit_feedback:
                feedback = f"Most useful aspect: {question1}\nFocus on: {question2}\nAdjustments: {question3}"
                st.session_state.feedback = feedback
                current_feedback = feedback

                # Regenerate recommendations
                job_path, course_path, project_path, course_details = regenerate_recommendations(st.session_state.resume_text, current_feedback)
                st.success("✅ Feedback submitted successfully. Recommendations have been updated.")

                # Update the profile with the new paths
                if "profile" not in st.session_state:
                    st.session_state.profile = {}
                st.session_state.profile["job_path"] = job_path
                st.session_state.profile["course_path"] = course_path
                st.session_state.profile["project_path"] = project_path
                st.session_state.profile["course_details"] = course_details

                

    # **Ensure that display_recommendations is called only once after recommendations are generated**
    if st.session_state.resume_text and st.session_state.job_path:
        # User returned after leaving tab or initial recommendations
   
        # Display recommendations based on session_state
        display_recommendations(
            st.session_state.job_path,
            st.session_state.course_details,
            st.session_state.project_path,
            st.session_state.location,
            st.session_state.country_code
        )
    else:
        # Otherwise, allow user to upload CV
        uploaded_file = st.file_uploader("📂 Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            try:
                resume_text = extract_text(uploaded_file, file_type)
                
                st.success("✅ CV successfully uploaded and text extracted.")
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
                st.stop()

            with st.spinner("🧠 Analyzing your resume..."):
                user_level = determine_user_level(resume_text)
                location, country_code = get_country_code_and_location(resume_text)
                personal_info = extract_personal_info(resume_text)
                skills = extract_skills(resume_text)
                education = extract_education(resume_text)
                experience = extract_experience(resume_text)
                languages = extract_languages(resume_text)
                awards = extract_awards(resume_text)
                projects = extract_projects(resume_text)

            # Store all extracted info in session state
            st.session_state.resume_text = resume_text
            st.session_state.user_level = user_level
            st.session_state.location = location
            st.session_state.country_code = country_code
            st.session_state.personal_info = personal_info
            st.session_state.skills = skills
            st.session_state.education = education
            st.session_state.experience = experience
            st.session_state.languages = languages
            st.session_state.awards = awards
            st.session_state.projects = projects



            # Update profile
            update_profile_from_career_advisor(
                user_level,
                location,
                country_code,
                personal_info,
                skills,
                education,
                experience,
                languages,
                awards,
                projects
            )

            # Add job_path, course_path, project_path to profile
            st.session_state.profile["job_path"] = st.session_state.job_path
            st.session_state.profile["course_path"] = st.session_state.course_path
            st.session_state.profile["project_path"] = st.session_state.project_path
            st.session_state.profile["course_details"] = st.session_state.course_details



            # Generate initial recommendations and capture them
            job_path, course_path, project_path, course_details = generate_initial_recommendations(resume_text, current_feedback)

            # Display recommendations immediately
            display_recommendations(job_path, course_details, project_path, location, country_code)

        else:
            # If no file uploaded and no session data:
            if not st.session_state.resume_text:
                st.info("📄 Please upload your CV to get started.")