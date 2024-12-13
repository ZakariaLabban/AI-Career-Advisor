# File: data/api_data.py

import requests
from data.profile_data import generate_course_descriptions

import streamlit as st

import os
import openai
import textwrap

# OpenAI API Key
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

# Function to search jobs on Adzuna
def search_jobs_on_adzuna(main_job_title, location, country_code):
    base_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 5,
        "what": main_job_title,
        "where": location,
        "content-type": "application/json",
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        jobs = response.json().get("results", [])
        related_jobs = []
        for job in jobs:
            current_job_title = job.get("title", "")
            if not current_job_title:
                continue

            prompt = (
                f"Is the following job title related to '{main_job_title}'?\n"
                f"Job Title: '{current_job_title}'\n"
                f"Answer 'yes' or 'no'."
            )

            try:
                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=5,
                    temperature=0.0,
                )
                answer = gpt_response.choices[0].message['content'].strip().lower()
                if answer == "yes":
                    # Truncate description to 300 characters if necessary
                    description = job.get("description", "")
                    if len(description) > 300:
                        job["description"] = description[:300] + "..."
                    related_jobs.append(job)
            except Exception as e:
                st.error(f"OpenAI API Error: {e}")
                continue

        return related_jobs
    else:
        st.error(f"Adzuna API Error: {response.status_code} - {response.text}")
        return []

# Function to search courses on Coursera
def search_courses_on_coursera(course_titles):
    course_details = []
    base_url = "https://api.coursera.org/api/courses.v1"
    headers = {
        "Authorization": f"Bearer {coursera_token}"
    }

    for title in course_titles:
        params = {
            "q": "search",
            "query": title,
            "limit": 3
        }
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            courses = response.json().get("elements", [])
            if courses:
                # Use the first matching course
                course = courses[0]
                course_details.append({
                    "title": course.get("name", "N/A"),
                    "url": f"https://www.coursera.org/learn/{course.get('slug', '')}",
                    "description": course.get("description", "No description available.")
                })
            else:
                # If no course found, append placeholders
                course_details.append({
                    "title": title,
                    "url": "#",
                    "description": "No description available."
                })
        else:
            st.error(f"Coursera API Error: {response.status_code} - {response.text}")
            course_details.append({
                "title": title,
                "url": "#",
                "description": "No description available."
            })

    # Generate descriptions where missing using GPT
    descriptions = generate_course_descriptions(course_details)
    for i, desc in enumerate(descriptions):
        course_details[i]['description'] = desc

    return course_details

# Function to search GitHub projects
def search_github_projects(query, language="python", sort="stars", order="desc"):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = "https://api.github.com/search/repositories"
    enhanced_query = f"{query} in:readme in:description language:{language}"

    params = {
        "q": enhanced_query,
        "sort": sort,
        "order": order,
        "per_page": 5
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        items = response.json()["items"]
        for item in items:
            description = item.get("description") or ""
            if len(description) > 300:
                item["description"] = description[:300] + "..."
        return items
    else:
        st.error(f"GitHub API Error: {response.status_code} - {response.text}")
        return []
