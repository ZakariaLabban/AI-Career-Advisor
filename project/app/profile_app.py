# app/profile_app.py

import streamlit as st
import openai

from utils.resume_utils import (
    determine_user_level,
    get_country_code_and_location,
    extract_personal_info,
    extract_skills,
    categorize_skills  # Import the new categorize_skills function
)
from data.profile_data import (
    extract_education,
    extract_experience,
    extract_languages,
    extract_awards,
    extract_projects,
    generate_job_path,
    generate_course_path,
    generate_project_path,
    generate_course_descriptions
)

import requests
import os

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


# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = {
        "name": "",
        "job_title": "",
        "email": "",
        "phone": "",
        "location": "",
        "dob": "",
        "nationality": "",
        "linkedin": "",
        "skills": [],
        "soft_skills": [],  # Added for soft skills
        "technical_skills": [],  # Added for technical skills
        "languages": [],
        "education": [],
        "experience": [],
        "awards": [],
        "projects": [],
        "summary": ""
    }

if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if 'profile_approved' not in st.session_state:
    st.session_state.profile_approved = False


def edit_profile():
    profile = st.session_state.profile

    st.header("🖊️ Edit Profile")

    # Initialize session state counters for dynamic fields if not already
    for field in ['skills', 'languages', 'education', 'experience', 'awards', 'projects']:
        key = f'edit_{field}_count'
        if key not in st.session_state:
            st.session_state[key] = len(profile.get(field, [])) or 1

    # Personal Information
    st.markdown("### Personal Information")
    name = st.text_input("Name", value=profile.get('name', ''), key="edit_name")
    job_title = st.text_input("Job Title", value=profile.get('job_title', ''), key="edit_job_title")
    email = st.text_input("Email", value=profile.get('email', ''), key="edit_email")
    phone = st.text_input("Phone", value=profile.get('phone', ''), key="edit_phone")
    location = st.text_input("Location", value=profile.get('location', ''), key="edit_location")
    dob = st.text_input("Date of Birth", value=profile.get('dob', ''), key="edit_dob")
    nationality = st.text_input("Nationality", value=profile.get('nationality', ''), key="edit_nationality")
    linkedin = st.text_input("LinkedIn URL", value=profile.get('linkedin', ''), key="edit_linkedin")

    st.markdown("---")

    # Skills Section
    st.markdown("### Skills")
    skill_level_options = ["Beginner", "Amateur", "Competent", "Proficient", "Expert"]

    for idx in range(st.session_state.edit_skills_count):
        st.markdown(f"**Skill {idx + 1}**")
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            skill_name = st.text_input(
                f"Skill Name {idx + 1}",
                value=profile.get('skills', [])[idx]['skill'] if idx < len(profile.get('skills', [])) else '',
                key=f"edit_skill_name_{idx}"
            )
        with col2:
            current_level = profile.get('skills', [])[idx]['level'] if idx < len(profile.get('skills', [])) else "Beginner"
            # Ensure that the current level is within the options
            if current_level not in skill_level_options:
                current_level = "Beginner"
            skill_level = st.selectbox(
                f"Skill Level {idx + 1}",
                skill_level_options,
                index=skill_level_options.index(current_level) if current_level in skill_level_options else 0,
                key=f"edit_skill_level_{idx}"
            )
        with col3:
            remove_btn = st.button("Remove", key=f"remove_skill_{idx}")
            if remove_btn:
                if st.session_state.edit_skills_count > 1:
                    st.session_state.edit_skills_count -= 1
                    if idx < len(profile['skills']):
                        del profile['skills'][idx]
                    # Also remove from soft_skills and technical_skills if present
                    remove_skill_from_categories(profile, f"edit_skill_name_{idx}")
                    ()
        st.markdown("---")

    if st.button("Add Skill"):
        st.session_state.edit_skills_count += 1
        ()

    st.markdown("---")

    # Languages Section
    st.markdown("### Languages")
    language_level_options = ["Basic", "Conversational", "Proficient", "Fluent", "Native/Bilingual"]

    for idx in range(st.session_state.edit_languages_count):
        st.markdown(f"**Language {idx + 1}**")
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            language_name = st.text_input(
                f"Language Name {idx + 1}",
                value=profile.get('languages', [])[idx]['Language'] if idx < len(profile.get('languages', [])) else '',
                key=f"edit_language_name_{idx}"
            )
        with col2:
            current_level = profile.get('languages', [])[idx]['Level'] if idx < len(profile.get('languages', [])) else "Basic"
            # Ensure that the current level is within the options
            if current_level not in language_level_options:
                current_level = "Basic"
            language_level = st.selectbox(
                f"Proficiency Level {idx + 1}",
                language_level_options,
                index=language_level_options.index(current_level) if current_level in language_level_options else 0,
                key=f"edit_language_level_{idx}"
            )
        with col3:
            remove_btn = st.button("Remove", key=f"remove_language_{idx}")
            if remove_btn:
                if st.session_state.edit_languages_count > 1:
                    st.session_state.edit_languages_count -= 1
                    if idx < len(profile['languages']):
                        del profile['languages'][idx]
                    ()
        st.markdown("---")

    if st.button("Add Language"):
        st.session_state.edit_languages_count += 1
        ()

    st.markdown("---")

    # Education Section
    st.markdown("### Education")
    for idx in range(st.session_state.edit_education_count):
        st.markdown(f"**Education Entry {idx + 1}**")
        degree = st.text_input(
            f"Degree {idx + 1}",
            value=profile.get('education', [])[idx]['Degree'] if idx < len(profile.get('education', [])) else '',
            key=f"edit_degree_{idx}"
        )
        institution = st.text_input(
            f"Institution {idx + 1}",
            value=profile.get('education', [])[idx]['Institution'] if idx < len(profile.get('education', [])) else '',
            key=f"edit_institution_{idx}"
        )
        years = st.text_input(
            f"Years {idx + 1}",
            value=profile.get('education', [])[idx]['Years'] if idx < len(profile.get('education', [])) else '',
            key=f"edit_education_years_{idx}"
        )
        details = st.text_input(
            f"Details {idx + 1}",
            value=profile.get('education', [])[idx]['Details'] if idx < len(profile.get('education', [])) else '',
            key=f"edit_education_details_{idx}"
        )
        col3 = st.columns([3, 2, 1])[2]
        with col3:
            remove_btn = st.button("Remove", key=f"remove_education_{idx}")
            if remove_btn:
                if st.session_state.edit_education_count > 1:
                    st.session_state.edit_education_count -= 1
                    if idx < len(profile['education']):
                        del profile['education'][idx]
                    ()
        st.markdown("---")

    if st.button("Add Education Entry"):
        st.session_state.edit_education_count += 1
        ()

    st.markdown("---")

    # Professional Experience Section
    st.markdown("### Professional Experience")
    for idx in range(st.session_state.edit_experience_count):
        st.markdown(f"**Experience Entry {idx + 1}**")
        title = st.text_input(
            f"Title {idx + 1}",
            value=profile.get('experience', [])[idx]['Title'] if idx < len(profile.get('experience', [])) else '',
            key=f"edit_title_{idx}"
        )
        company = st.text_input(
            f"Company {idx + 1}",
            value=profile.get('experience', [])[idx]['Company'] if idx < len(profile.get('experience', [])) else '',
            key=f"edit_company_{idx}"
        )
        years = st.text_input(
            f"Years {idx + 1}",
            value=profile.get('experience', [])[idx]['Years'] if idx < len(profile.get('experience', [])) else '',
            key=f"edit_experience_years_{idx}"
        )
        details = st.text_area(
            f"Details {idx + 1}",
            value=profile.get('experience', [])[idx].get('Details', '') if idx < len(profile.get('experience', [])) else '',
            key=f"edit_details_{idx}"
        )
        col3 = st.columns([3, 2, 1])[2]
        with col3:
            remove_btn = st.button("Remove", key=f"remove_experience_{idx}")
            if remove_btn:
                if st.session_state.edit_experience_count > 1:
                    st.session_state.edit_experience_count -= 1
                    if idx < len(profile['experience']):
                        del profile['experience'][idx]
                    ()
        st.markdown("---")

    if st.button("Add Experience Entry"):
        st.session_state.edit_experience_count += 1
        ()

    st.markdown("---")

    # Awards Section
    st.markdown("### Awards")
    for idx in range(st.session_state.edit_awards_count):
        st.markdown(f"**Award {idx + 1}**")
        award = st.text_input(
            f"Award {idx + 1}",
            value=profile.get('awards', [])[idx] if idx < len(profile.get('awards', [])) else '',
            key=f"edit_award_{idx}"
        )
        col3 = st.columns([3, 2, 1])[2]
        with col3:
            remove_btn = st.button("Remove", key=f"remove_award_{idx}")
            if remove_btn:
                if st.session_state.edit_awards_count > 1:
                    st.session_state.edit_awards_count -= 1
                    if idx < len(profile['awards']):
                        del profile['awards'][idx]
                    ()
        st.markdown("---")

    if st.button("Add Award"):
        st.session_state.edit_awards_count += 1
        ()

    st.markdown("---")

    # Projects Section
    st.markdown("### Projects")
    for idx in range(st.session_state.edit_projects_count):
        st.markdown(f"**Project {idx + 1}**")
        title = st.text_input(
            f"Project Title {idx + 1}",
            value=profile.get('projects', [])[idx]['Title'] if idx < len(profile.get('projects', [])) else '',
            key=f"edit_project_title_{idx}"
        )
        description = st.text_input(
            f"Project Description {idx + 1}",
            value=profile.get('projects', [])[idx].get('Description', '') if idx < len(profile.get('projects', [])) else '',
            key=f"edit_project_description_{idx}"
        )
        col3 = st.columns([3, 2, 1])[2]
        with col3:
            remove_btn = st.button("Remove", key=f"remove_project_{idx}")
            if remove_btn:
                if st.session_state.edit_projects_count > 1:
                    st.session_state.edit_projects_count -= 1
                    if idx < len(profile['projects']):
                        del profile['projects'][idx]
                    ()
        st.markdown("---")

    if st.button("Add Project"):
        st.session_state.edit_projects_count += 1
        ()

    st.markdown("---")

    # Profile Summary Section (Optional)
    st.markdown("### Profile Summary (Optional)")
    summary = st.text_area("Summary",
                           value=profile.get('summary', ''),
                           height=150,
                           key="edit_summary")

    st.markdown("---")

    # Save Changes and Cancel Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        save_btn = st.button("💾 Save Changes")
    with col2:
        cancel_btn = st.button("❌ Cancel")

    if save_btn:
        # Collect Skills
        new_skills = []
        for idx in range(st.session_state.edit_skills_count):
            skill = st.session_state.get(f"edit_skill_name_{idx}", "").strip()
            level = st.session_state.get(f"edit_skill_level_{idx}", "Beginner")
            if skill:
                new_skills.append({"skill": skill, "level": level})

        # Collect Languages
        new_languages = []
        for idx in range(st.session_state.edit_languages_count):
            language = st.session_state.get(f"edit_language_name_{idx}", "").strip()
            level = st.session_state.get(f"edit_language_level_{idx}", "Basic")
            if language:
                new_languages.append({"Language": language, "Level": level})

        # Collect Education
        new_education = []
        for idx in range(st.session_state.edit_education_count):
            degree = st.session_state.get(f"edit_degree_{idx}", "").strip()
            institution = st.session_state.get(f"edit_institution_{idx}", "").strip()
            years = st.session_state.get(f"edit_education_years_{idx}", "").strip()
            details = st.session_state.get(f"edit_education_details_{idx}", "").strip()
            if degree and institution:
                new_education.append({"Degree": degree, "Institution": institution, "Years": years, "Details": details})

        # Collect Experience
        new_experience = []
        for idx in range(st.session_state.edit_experience_count):
            title = st.session_state.get(f"edit_title_{idx}", "").strip()
            company = st.session_state.get(f"edit_company_{idx}", "").strip()
            years = st.session_state.get(f"edit_experience_years_{idx}", "").strip()
            details = st.session_state.get(f"edit_details_{idx}", "").strip()
            if title and company:
                new_experience.append({"Title": title, "Company": company, "Years": years, "Details": details})

        # Collect Awards
        new_awards = []
        for idx in range(st.session_state.edit_awards_count):
            award = st.session_state.get(f"edit_award_{idx}", "").strip()
            if award:
                new_awards.append(award)

        # Collect Projects
        new_projects = []
        for idx in range(st.session_state.edit_projects_count):
            title = st.session_state.get(f"edit_project_title_{idx}", "").strip()
            description = st.session_state.get(f"edit_project_description_{idx}", "").strip()
            if title:
                new_projects.append({"Title": title, "Description": description})

        # Collect Profile Summary
        summary_text = st.session_state.get("edit_summary", "").strip()

        # Update Profile
        updated_profile = {
            "name": name.strip(),
            "job_title": job_title.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "location": location.strip(),
            "dob": dob.strip(),
            "nationality": nationality.strip(),
            "linkedin": linkedin.strip(),
            "skills": new_skills,
            "languages": new_languages,
            "education": new_education,
            "experience": new_experience,
            "awards": new_awards,
            "projects": new_projects,
            "summary": summary_text if summary_text else profile.get('summary', ''),
        }

        # Categorize Skills into Soft and Technical while preserving proficiency levels
        soft_skills, technical_skills = categorize_skills(new_skills)
        updated_profile['soft_skills'] = soft_skills
        updated_profile['technical_skills'] = technical_skills

        st.session_state.profile = updated_profile
        st.session_state.profile_approved = True
        st.session_state.edit_mode = False
        st.success("Profile updated and approved.")
        st.success("Skill Gap Analysis is now accessible from the sidebar.")

        # Generate Profile Summary (Optional)
        if not summary_text:
            summary = generate_profile_summary(updated_profile)
            if summary != "N/A":
                st.session_state.profile['summary'] = summary
                st.success("Profile summary generated.")

        # Save Session State
        ()

    if cancel_btn:
        st.session_state.edit_mode = False
        st.warning("Edit cancelled.")
        # Optionally, you can revert changes or simply exit edit mode
        ()


def remove_skill_from_categories(profile, skill_key_prefix):
    """
    Removes a skill from soft_skills and technical_skills based on the skill name.

    Parameters:
        profile (dict): The user's profile.
        skill_key_prefix (str): The prefix of the skill key in session state.
    """
    # Extract the skill name from the session state key
    skill_name = st.session_state.get(skill_key_prefix, "").strip().lower()

    # Remove from soft_skills
    profile['soft_skills'] = [skill for skill in profile['soft_skills'] if skill['skill'].lower() != skill_name]

    # Remove from technical_skills
    profile['technical_skills'] = [skill for skill in profile['technical_skills'] if skill['skill'].lower() != skill_name]


def update_profile_from_career_advisor(user_level, location, country_code, personal_info, skills,
                                      education, experience, languages, awards, projects):
    """
    Updates the session state profile with data extracted from the career advisor.

    Parameters:
        user_level (str): The user's career level.
        location (str): The user's location.
        country_code (str): The two-letter country code.
        personal_info (dict): Extracted personal information.
        skills (list): List of extracted skills with standardized levels.
        education (list): List of extracted education details.
        experience (list): List of extracted professional experiences.
        languages (list): List of extracted languages.
        awards (list): List of extracted awards.
        projects (list): List of extracted projects.
    """
    if 'profile' not in st.session_state:
        st.session_state.profile = {}

    # Update profile with existing data
    st.session_state.profile['user_level'] = user_level
    st.session_state.profile['location'] = location
    st.session_state.profile['country_code'] = country_code

    # Update personal information
    st.session_state.profile['name'] = personal_info.get("Name", "N/A")
    st.session_state.profile['email'] = personal_info.get("Email", "N/A")
    st.session_state.profile['phone'] = personal_info.get("Phone", "N/A")
    st.session_state.profile['dob'] = personal_info.get("Date of Birth", "N/A")
    st.session_state.profile['nationality'] = personal_info.get("Nationality", "N/A")
    st.session_state.profile['linkedin'] = personal_info.get("LinkedIn", "N/A")

    # Update skills
    existing_skills = st.session_state.profile.get('skills', [])
    combined_skills = existing_skills + skills
    # Remove duplicate skills based on 'skill' name (case-insensitive)
    unique_skills = {}
    for skill in combined_skills:
        skill_name = skill['skill'].lower()
        if skill_name not in unique_skills:
            unique_skills[skill_name] = skill
    st.session_state.profile['skills'] = list(unique_skills.values())

    # Categorize Skills into Soft and Technical while preserving proficiency levels
    soft_skills, technical_skills = categorize_skills(st.session_state.profile['skills'])
    st.session_state.profile['soft_skills'] = soft_skills
    st.session_state.profile['technical_skills'] = technical_skills

    # Update education
    existing_education = st.session_state.profile.get('education', [])
    combined_education = existing_education + education
    # Remove duplicate education entries based on Degree and Institution (case-insensitive)
    unique_education = {}
    for edu in combined_education:
        key = f"{edu['Degree'].lower()}_{edu['Institution'].lower()}"
        if key not in unique_education:
            unique_education[key] = edu
    st.session_state.profile['education'] = list(unique_education.values())

    # Update experience
    existing_experience = st.session_state.profile.get('experience', [])
    combined_experience = existing_experience + experience
    unique_experience = {}
    for exp in combined_experience:
        key = f"{exp['Title'].lower()}_{exp['Company'].lower()}"
        if key not in unique_experience:
            unique_experience[key] = exp
    st.session_state.profile['experience'] = list(unique_experience.values())

    # Update languages
    existing_languages = st.session_state.profile.get('languages', [])
    combined_languages = existing_languages + languages
    unique_languages = {}
    for lang in combined_languages:
        lang_name = lang['Language'].lower()
        if lang_name not in unique_languages:
            unique_languages[lang_name] = lang
    st.session_state.profile['languages'] = list(unique_languages.values())

    # Update awards
    existing_awards = st.session_state.profile.get('awards', [])
    combined_awards = existing_awards + awards
    unique_awards = set()
    filtered_awards = []
    for award in combined_awards:
        award_lower = award.lower()
        if award_lower not in unique_awards:
            unique_awards.add(award_lower)
            filtered_awards.append(award)
    st.session_state.profile['awards'] = filtered_awards

    # Update projects
    existing_projects = st.session_state.profile.get('projects', [])
    combined_projects = existing_projects + projects
    unique_projects = {}
    for proj in combined_projects:
        proj_title = proj['Title'].lower()
        if proj_title not in unique_projects:
            unique_projects[proj_title] = proj
    st.session_state.profile['projects'] = list(unique_projects.values())


def update_profile_from_cv(data):
    if 'profile' not in st.session_state:
        st.session_state.profile = {}
    # Merge data into profile without overwriting existing keys unless necessary
    for key, value in data.items():
        if key == 'skills':
            existing_skills = st.session_state.profile.get('skills', [])
            combined_skills = existing_skills + value
            unique_skills = {skill['skill'].lower(): skill for skill in combined_skills if 'skill' in skill and 'level' in skill}
            st.session_state.profile['skills'] = list(unique_skills.values())
            # Categorize Skills into Soft and Technical while preserving proficiency levels
            soft_skills, technical_skills = categorize_skills(st.session_state.profile['skills'])
            st.session_state.profile['soft_skills'] = soft_skills
            st.session_state.profile['technical_skills'] = technical_skills
        elif key == 'languages':
            existing_languages = st.session_state.profile.get('languages', [])
            combined_languages = existing_languages + value
            unique_languages = {lang['Language'].lower(): lang for lang in combined_languages if 'Language' in lang and 'Level' in lang}
            st.session_state.profile['languages'] = list(unique_languages.values())
        elif key == 'education':
            existing_education = st.session_state.profile.get('education', [])
            combined_education = existing_education + value
            unique_education = {f"{edu['Degree'].lower()}_{edu['Institution'].lower()}": edu for edu in combined_education if 'Degree' in edu and 'Institution' in edu}
            st.session_state.profile['education'] = list(unique_education.values())
        elif key == 'experience':
            existing_experience = st.session_state.profile.get('experience', [])
            combined_experience = existing_experience + value
            unique_experience = {f"{exp['Title'].lower()}_{exp['Company'].lower()}": exp for exp in combined_experience if 'Title' in exp and 'Company' in exp}
            st.session_state.profile['experience'] = list(unique_experience.values())
        elif key == 'awards':
            existing_awards = st.session_state.profile.get('awards', [])
            combined_awards = existing_awards + value
            unique_awards = set()
            filtered_awards = []
            for award in combined_awards:
                award_lower = award.lower()
                if award_lower not in unique_awards:
                    unique_awards.add(award_lower)
                    filtered_awards.append(award)
            st.session_state.profile['awards'] = filtered_awards
        elif key == 'projects':
            existing_projects = st.session_state.profile.get('projects', [])
            combined_projects = existing_projects + value
            unique_projects = {}
            for proj in combined_projects:
                proj_title = proj['Title'].lower()
                if proj_title not in unique_projects:
                    unique_projects[proj_title] = proj
            st.session_state.profile['projects'] = list(unique_projects.values())
        else:
            st.session_state.profile[key] = value


def generate_profile_summary(data):
    required_fields = ['name', 'job_title', 'skills', 'experience', 'education', 'languages']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        st.warning(f"Cannot generate summary. Missing fields: {', '.join(missing_fields)}")
        return "N/A"

    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates professional summaries for CVs."},
        {"role": "user", "content": (
            f"Write a professional first-person profile summary for a CV based on the following details:\n\n"
            f"Name: {data.get('name')}\n"
            f"Job Title/Major: {data.get('job_title')}\n"
            f"Skills: {', '.join([skill['skill'] for skill in data.get('skills', []) if 'skill' in skill])}\n"
            f"Experience: {'; '.join([exp['Title'] for exp in data.get('experience', []) if 'Title' in exp])}\n"
            f"Education: {'; '.join([edu['Degree'] for edu in data.get('education', []) if 'Degree' in edu])}\n"
            f"Languages: {', '.join([lang['Language'] for lang in data.get('languages', []) if 'Language' in lang])}\n\n"
            f"The summary should be concise, highlight key strengths, and be no more than 150 words."
        )}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Ensure the correct model name
            messages=messages,
            max_tokens=300,  # Increased tokens to accommodate up to 150 words
            temperature=0.7,
        )

        profile_summary = response.choices[0].message['content'].strip()
        return profile_summary
    except Exception as e:
        st.error(f"An error occurred while generating the profile summary: {e}")
        return "N/A"

# =========================
# Main Profile Function
# =========================

def my_profile():
    st.header("👤 My Profile")

    profile = st.session_state.profile

    # Check if profile is empty
    is_empty = (
        not any([profile.get('name'), profile.get('job_title'), profile.get('email'),
                 profile.get('phone'), profile.get('location'), profile.get('dob'),
                 profile.get('nationality'), profile.get('linkedin')]) and
        not any([profile.get('skills'), profile.get('soft_skills'), profile.get('technical_skills'), profile.get('languages'), profile.get('education'),
                 profile.get('experience'), profile.get('awards'), profile.get('projects')])
    )

    if is_empty:
        st.info("Your profile is empty. Please use the **Career Advisor** or **Build Your CV** features to populate your profile.")
        return

    if st.session_state.edit_mode:
        # In edit mode
        edit_profile()
    else:
        # Display the Edit Profile button at the top
        if st.button("✏️ Edit Profile"):
            st.session_state.edit_mode = True
            ()
            # No need to call st.experimental_rerun()

        # Display profile
        # Personal Information Section
        with st.container():
            st.subheader("Personal Information")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Name:** {profile.get('name', 'N/A')}")
                st.markdown(f"**Job Title:** {profile.get('job_title', 'N/A')}")
                st.markdown(f"**Email:** {profile.get('email', 'N/A')}")
                st.markdown(f"**Phone:** {profile.get('phone', 'N/A')}")

            with col2:
                st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                st.markdown(f"**Date of Birth:** {profile.get('dob', 'N/A')}")
                st.markdown(f"**Nationality:** {profile.get('nationality', 'N/A')}")
                linkedin = profile.get('linkedin', 'N/A')
                if linkedin != "N/A" and linkedin:
                    st.markdown(f"**LinkedIn:** [Profile]({linkedin})")
                else:
                    st.markdown(f"**LinkedIn:** {linkedin}")

        st.markdown("---")

        # Skills Section
        with st.expander("🔧 TECHNICAL SKILLS", expanded=True):
            technical_skills = profile.get("technical_skills", [])
            if technical_skills:
                for skill in technical_skills:
                    st.markdown(f"- **{skill['skill']}**: {skill['level']}")
            else:
                st.write("No technical skills available.")

        with st.expander("💡 SOFT SKILLS", expanded=True):
            soft_skills = profile.get("soft_skills", [])
            if soft_skills:
                for skill in soft_skills:
                    st.markdown(f"- **{skill['skill']}**: {skill['level']}")
            else:
                st.write("No soft skills available.")

        # Languages Section
        with st.expander("🗣️ LANGUAGES", expanded=True):
            languages = profile.get("languages", [])
            if languages:
                for lang in languages:
                    st.markdown(f"- **{lang.get('Language', 'N/A')}**: {lang.get('Level', 'N/A')}")
            else:
                st.write("No languages available.")

        # Education Section
        with st.expander("🎓 EDUCATION", expanded=True):
            education = profile.get("education", [])
            if education:
                for edu in education:
                    st.markdown(f"**{edu.get('Degree', 'N/A')}**, {edu.get('Institution', 'N/A')} ({edu.get('Years', 'N/A')})")
                    details = edu.get("Details", "")
                    if details and details != "N/A":
                        st.markdown(f"  - **Details:** {details}")
            else:
                st.write("No education details available.")

        # Professional Experience Section
        with st.expander("💼 PROFESSIONAL EXPERIENCE", expanded=True):
            experience = profile.get("experience", [])
            if experience:
                for exp in experience:
                    st.markdown(f"**{exp.get('Title', 'N/A')}** at **{exp.get('Company', 'N/A')}** ({exp.get('Years', 'N/A')})")
                    st.markdown(f"{exp.get('Details', 'No details provided.')}")
            else:
                st.write("No professional experience available.")

        # Awards Section
        with st.expander("🏆 AWARDS", expanded=True):
            awards = profile.get("awards", [])
            if awards:
                for award in awards:
                    st.markdown(f"- {award}")
            else:
                st.write("No awards available.")

        # Projects Section
        with st.expander("🚀 PROJECTS", expanded=True):
            projects = profile.get("projects", [])
            if projects:
                for proj in projects:
                    st.markdown(f"- **{proj.get('Title', 'N/A')}**: {proj.get('Description', 'No description available.')}")
            else:
                st.write("No projects available.")



        st.markdown("---")

        # Approval Options
        if st.button("✅ Approve Data"):
            st.session_state.profile_approved = True
            st.success("Profile data approved.")
            st.success("Skill Gap Analysis is now accessible from the sidebar.")
            ()
