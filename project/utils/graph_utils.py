import requests
import os
import openai
from pyvis.network import Network

openai.api_key = ""
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
# Function to generate a career path graph (job, course, project mapping) with pyvis
def generate_career_path_graph(job_path, course_path, project_path):
    # Create a network object
    net = Network(height="800px", width="100%", directed=True)

    # Add nodes for jobs, courses, and projects for each stage
    for i in range(len(job_path)):
        job_node = f"Job: {job_path[i]}"
        course_node = f"Course: {course_path[i]}"
        project_node = f"Project: {project_path[i]}"
        
        # Add nodes with specific colors for each category
        net.add_node(job_node, label=job_node, color="lightcoral", title=job_node, size=20)
        net.add_node(course_node, label=course_node, color="lightblue", title=course_node, size=20)
        net.add_node(project_node, label=project_node, color="lightgreen", title=project_node, size=20)

        # Add edges connecting Job, Course, and Project for each stage
        net.add_edge(job_node, course_node, color="blue")
        net.add_edge(job_node, project_node, color="green")
    
    # Add edges connecting jobs in order (career progression)
    for i in range(len(job_path) - 1):
        net.add_edge(f"Job: {job_path[i]}", f"Job: {job_path[i+1]}", color="gray", width=2)

    # Set the physics of the network to make it more interactive (dynamic layout)
    net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=300, damping=0.4)

    return net

