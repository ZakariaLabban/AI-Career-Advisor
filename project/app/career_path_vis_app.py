from utils.graph_utils import generate_career_path_graph


import tempfile
import streamlit as st
import requests
import os
import openai

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

def career_path_vizualization():
    st.header("📊 Career Path Visualization")
    st.markdown("""
    Visualize your career progression by mapping your **job titles**, **recommended courses**, and **related GitHub projects** on an interactive graph. 
    The graph will show the connections between your career stages.
    """)

    if 'job_path' in st.session_state and 'course_path' in st.session_state and 'project_path' in st.session_state:
        job_path = st.session_state.job_path
        course_path = st.session_state.course_path
        project_path = st.session_state.project_path

        # Ensure there is data for the career path
        if job_path and course_path and project_path:
            # Generate the career path graph
            net = generate_career_path_graph(job_path, course_path, project_path)

            # Save the network graph to a temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                tmp_file_path = tmp_file.name
                net.save_graph(tmp_file_path)

            # Read the saved HTML file
            with open(tmp_file_path, 'r') as file:
                html_content = file.read()

            # Display the HTML content (interactive graph) in Streamlit
            st.components.v1.html(html_content, height=600, width=800)

            # Personalized Summary
            st.subheader("Your Personalized Career Path Summary")

            current_role = job_path[0]
            next_role = job_path[1] if len(job_path) > 1 else None

            st.markdown(f"### Your First Role: **{current_role}**")
            st.markdown(f"You should start working as a **{current_role}**. To further progress in your career, you should focus on mastering advanced topics and hands-on projects related to this role.")

            if next_role:
                st.markdown(f"### Next Career Step: **{next_role}**")
                st.markdown(f"To move to the **{next_role}** position, consider improving your skills in the following areas:")
                st.markdown(f"1. **Skills to Learn**: {course_path[1]}")
                st.markdown(f"2. **Project to Work On**: {project_path[1]}")
                st.markdown(f"Start by gaining experience in {project_path[1]} and refining your understanding of {course_path[1]}. This will prepare you for the next role in your career journey.")

        else:
            st.info("Career paths (Job, Course, Project) are not available. Please use the **Career Advisor** to generate them first.")
    else:
        st.info("Career paths (Job, Course, Project) are not available. Please use the **Career Advisor** to generate them first.")

    # Add descriptive text for the reader
    st.subheader("How to Read the Career Path Visualization")
    st.markdown("""
    This interactive graph visualizes a potential career progression in the industry.

    **Nodes** represent different stages in the career path:
    - **Job**: The job titles at various stages of career progression.
    - **Course**: Recommended courses or skills needed for a specific job role.
    - **Project**: Suggested hands-on projects that align with the job and course for real-world experience.

    **Arrows (Edges)** represent the connections between jobs, courses, and projects:
    - **Job -> Course**: This indicates which course or skills are needed to progress to the next job role.
    - **Job -> Project**: This suggests which types of projects can help you gain experience for that job.
    - **Job -> Job**: These edges show how one job can naturally lead to another in a career progression.

    **Use this visualization as a guide** for your career development. Start with foundational skills and projects, and keep progressing toward advanced roles!
    """)
    

