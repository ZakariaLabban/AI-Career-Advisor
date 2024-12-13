import streamlit as st
import openai
import requests
import pdfplumber
from docx import Document
import textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
import io
import json
import re
import os  # Added for environment variables
import networkx as nx
from pyvis.network import Network
import tempfile

from app.career_advisor_app import career_advisor
from app.cv_builder_app import build_cv
from app.profile_app import my_profile
from app.skill_gap_analysis_app import skill_analysis
from app.career_path_vis_app import career_path_vizualization
from app.chatbot_app import chatbot_page
from app.ideal_job_app import find_ideal_job


from config import openai
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from config import GITHUB_TOKEN
from config import coursera_client_id, coursera_client_secret, coursera_token

st.set_page_config(page_title="AI-Powered Career Advisor", layout="wide")
st.title("🎓 AI-Powered Career Advisor")

# Sidebar Navigation with Updated Layout
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox(
    "Choose the feature:",
    ["Career Advisor", "Build Your CV", "My Profile", "Skill Gap Analysis", "Career Path Visualization","Chat with Career Advisor", "Find your Ideal Job" ]  # Added "Career Path Visualization"
)

# Ensure that data persists across tabs
if 'profile' not in st.session_state:
    st.session_state.profile = {}
if 'job_path' not in st.session_state:
    st.session_state.job_path = []
if 'course_path' not in st.session_state:
    st.session_state.course_path = []
if 'project_path' not in st.session_state:
    st.session_state.project_path = []

# Route to the correct app mode
if app_mode == "Career Advisor":
    career_advisor()
elif app_mode == "Build Your CV":
    build_cv()
elif app_mode == "My Profile":
    my_profile()
elif app_mode == "Skill Gap Analysis":
    skill_analysis()
elif app_mode == "Career Path Visualization":
    career_path_vizualization()
elif app_mode == "Chat with Career Advisor":  # New chatbot option
    chatbot_page()
elif app_mode == "Find your Ideal Job":
    find_ideal_job()