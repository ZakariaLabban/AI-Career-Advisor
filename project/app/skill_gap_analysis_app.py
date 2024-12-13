# app/skill_gap_analysis_app.py


import requests
import streamlit as st
import openai
import plotly.graph_objects as go
import plotly.express as px
import os
import logging

# Initialize logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Initialize OpenAI API securely using environment variables
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

def skill_analysis():
    st.header("📈 Skill Gap Analysis")
    
    # Check if 'profile' exists in session state
    if 'profile' not in st.session_state or not st.session_state.profile:
        st.info("Your profile is empty. Please use the **Career Advisor** or **Build Your CV** features to populate your profile before accessing the Skill Gap Analysis.")
        return

    # Check if profile is approved
    if not st.session_state.get('profile_approved', False):
        st.info("Please approve your profile before accessing the Skill Gap Analysis.")
        return

    profile = st.session_state.profile
    st.subheader("Skill Gap Analysis Overview")
    perform_skill_gap_analysis(profile)

def perform_skill_gap_analysis(profile):
    """
    Performs skill gap analysis based on the user's profile.

    Args:
        profile (dict): The user's profile data.
    """
    if not profile:
        st.write("No profile data available.")
        return

    # Extract user level and define thresholds
    user_level = profile.get('user_level', 'student').lower()

    # Define maximum percentage based on user level
    level_thresholds = {
        'undergraduate student': 60,
        'entry-level professional': 70,
        'mid-level professional': 80,
        'experienced professional': 85,
        'masters student': 65,
        'phd student': 70,
	'5+ years experience':80,
        '10+ years experience': 90,
        '20+ years experience': 100
    }

    max_percentage = level_thresholds.get(user_level, 100)
    if user_level not in level_thresholds:
        logging.warning(f"Unrecognized user level '{user_level}'. Defaulting max_percentage to 100.")
    
    logging.info(f"User level: {user_level}, Max Percentage: {max_percentage}")

    # Extract technical skills
    skills = profile.get('technical_skills', [])

    if not skills:
        st.warning("No technical skills available for analysis.")
        return

    # Define skill levels with relative weights
    # These weights represent the percentage of max_percentage each level contributes
    skill_level_weights = {
        'Beginner': 0.2,
        'Amateur': 0.4,
        'Competent': 0.6,
        'Proficient': 0.8,
        'Expert': 1.0,
    }

    # Prepare data for Radar Chart
    skill_names = [skill.get('skill', 'N/A') for skill in skills]
    # Calculate skill values relative to max_percentage
    skill_values = [
        skill_level_weights.get(skill.get('level', 'Beginner'), 0.2) * max_percentage 
        for skill in skills
    ]

    # Ensure the radar chart is a closed loop
    if len(skill_names) > 0:
        skill_names += [skill_names[0]]
        skill_values += [skill_values[0]]

    # Create Radar Chart using Plotly
    radar = go.Figure(
        data=go.Scatterpolar(
            r=skill_values,
            theta=skill_names,
            fill='toself',
            name='Your Skills'
        )
    )

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_percentage]
            )
        ),
        showlegend=False,
        title="🔍 Skill Gap Analysis Radar Chart"
    )

    # Prepare data for Interactive Bar Chart
    bar_data = {
        'Skill': [skill.get('skill', 'N/A') for skill in skills],
        'Proficiency': [
            skill_level_weights.get(skill.get('level', 'Beginner'), 0.2) * max_percentage 
            for skill in skills
        ]
    }

    bar_df = {
        'Skill': bar_data['Skill'],
        'Proficiency': bar_data['Proficiency']
    }

    # Create Interactive Bar Chart using Plotly Express
    bar = px.bar(
        bar_df,
        x='Proficiency',
        y='Skill',
        orientation='h',
        range_x=[0, max_percentage],
        color='Proficiency',
        color_continuous_scale='Viridis',
        title='📊 Skill Proficiency Bar Chart',
        labels={'Proficiency': 'Proficiency (%)', 'Skill': 'Skill'}
    )

    bar.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)

    # Display Radar and Bar Charts Side by Side
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(radar, use_container_width=True)

    with col2:
        st.plotly_chart(bar, use_container_width=True)

    # Calculate Overall Skill Completion
    if skills:
        average_skill_percentage = sum(bar_data['Proficiency']) / len(skills)
    else:
        average_skill_percentage = 0

    logging.info(f"Average Skill Percentage: {average_skill_percentage}")

    # Total completion based solely on technical skills
    total_completion = average_skill_percentage
    logging.info(f"Total Completion (Technical Skills Only): {total_completion}")

    # Store total_completion and max_percentage in session state for report generation
    st.session_state.total_completion = total_completion
    st.session_state.max_percentage = max_percentage

    # Overall Skill Completion Visualization
    st.subheader("Overall Skill Completion")
    overall_completion = total_completion / max_percentage if max_percentage else 0

    st.progress(overall_completion)
    st.write(f"**Total Skill Completion:** {total_completion:.2f}% / {max_percentage}%")

    # Analysis Summary
    st.markdown(f"""
    **Analysis Summary:**
    Based on your current technical skill set and career level as a **{user_level.capitalize()}**, your overall skill completion stands at **{total_completion:.2f}%** out of a maximum of **{max_percentage}%**. This analysis considers your proficiency in each technical skill. To further enhance your profile, consider focusing on areas where your skill levels are below the threshold.
    """)

    
    # Save Session State
    ()