import openai
import json
import streamlit as st

import requests
import os
import logging

# Initialize logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Initialize OpenAI API key securely using environment variables
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

# Function to determine user level
import openai
import logging
import streamlit as st

def determine_user_level(resume_text):
    """
    Determines the user's career level based on their resume text.

    Args:
        resume_text (str): The text content of the resume.

    Returns:
        str: The classified user level.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an assistant analyzing a resume to determine the user's career level."
        },
        {
            "role": "user",
            "content": (
                f"Based on the following resume, classify the user as one of the following without using quotes: "
                f"'undergraduate student', 'master's student', 'phd student', 'entry-level professional', 'mid-level professional', "
                f"'experienced professional', '10+ years experience', '20+ years experience'. "
                f"Provide only the classification as plain text without any additional text.\n\n"
                f"Resume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=10,
            temperature=0.5
        )

        user_level = response.choices[0].message['content'].strip()

        # Remove any surrounding quotes or extra characters
        user_level = user_level.strip().strip('"').strip("'").lower()

        logging.info(f"Determined user level: {user_level}")
        return user_level
    except Exception as e:
        logging.error(f"Error determining user level: {e}")
        st.error(f"An error occurred while determining user level: {e}")
        return "N/A"

# Function to get country code and location
def get_country_code_and_location(resume_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant that extracts the location from a user's resume and identifies its country."},
        {"role": "user", "content": (
            f"Please extract the main location or city from the following resume and determine the country it belongs to. "
            f"Return only the location followed by the two-letter country code, separated by a comma.\n\nResume:\n{resume_text}"
        )}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=50,
            temperature=0.5
        )

        detected_location = response.choices[0].message['content'].strip()
        logging.info(f"Detected location: {detected_location}")

        if ',' in detected_location:
            location, country_code = map(str.strip, detected_location.split(',', 1))
        else:
            location = ""
            country_code = detected_location.lower()

        location_to_country = {
            "australia": "au", "austria": "at", "belgium": "be", "brazil": "br",
            "canada": "ca", "france": "fr", "germany": "de", "india": "in",
            "italy": "it", "mexico": "mx", "netherlands": "nl", "new zealand": "nz",
            "poland": "pl", "russia": "ru", "singapore": "sg", "south africa": "za",
            "spain": "es", "sweden": "se", "switzerland": "ch", "united arab emirates": "ae",
            "united kingdom": "gb", "uk": "gb", "united states": "us", "usa": "us",
            "us": "us", "argentina": "ar", "ireland": "ie", "denmark": "dk",
            "norway": "no", "japan": "jp"
        }

        if country_code not in location_to_country.values():
            return "", "us"

        return location, country_code
    except Exception as e:
        logging.error(f"Error extracting location and country code: {e}")
        st.error(f"An error occurred while extracting location and country code: {e}")
        return "", "us"

# Function to extract personal information from resume
def extract_personal_info(resume_text):
    messages = [
        {"role": "system", "content": "You are an assistant that extracts personal information from a user's resume."},
        {"role": "user", "content": (
            f"Extract the following personal information from the resume text below. "
            f"Provide the information in a JSON format with the keys: Name, Email, Phone, Location, Date of Birth, Nationality, LinkedIn.\n\nResume:\n{resume_text}"
        )}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.3
        )

        personal_info_json = response.choices[0].message['content'].strip()
        logging.info(f"Extracted personal info JSON: {personal_info_json}")

        try:
            personal_info_dict = json.loads(personal_info_json)
        except json.JSONDecodeError:
            logging.warning("Failed to parse personal info JSON. Using fallback values.")
            personal_info_dict = {
                "Name": "N/A",
                "Email": "N/A",
                "Phone": "N/A",
                "Location": "",
                "Date of Birth": "N/A",
                "Nationality": "N/A",
                "LinkedIn": "N/A"
            }
            st.warning("Failed to parse personal information. Using default values.")

        return personal_info_dict
    except Exception as e:
        logging.error(f"Error extracting personal information: {e}")
        st.error(f"An error occurred while extracting personal information: {e}")
        return {
            "Name": "N/A",
            "Email": "N/A",
            "Phone": "N/A",
            "Location": "",
            "Date of Birth": "N/A",
            "Nationality": "N/A",
            "LinkedIn": "N/A"
        }

# Function to extract skills from resume
def extract_skills(resume_text):
    """
    Extracts skills and their proficiency levels from the given resume text.
    Ensures that any non-standard proficiency levels are mapped to the closest standard level: Beginner, Amateur, Competent, Proficient, Expert.

    Args:
        resume_text (str): The text content of the resume.

    Returns:
        list of dict: A list where each dictionary contains a 'skill' and its 'level'.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that extracts skills from a user's resume."
        },
        {
            "role": "user",
            "content": (
                f"Extract all relevant skills from the following resume text, including programming languages and software/tools, without including spoken languages as skills. "
                f"Each skill should be matched with its proficiency level where in some cases the level isn't directly next to the skill so you need to match the first skill you find with the first proficiency level you find. "
                f"Proficiency levels related to spoken languages should be ignored at all times such as Fluent, Native, Bilingual, Conversational. "
                f"In case there are no proficiency levels, deduce them based on the resume. Take into consideration education and projects and experience"
                f"In case the resume contains proficiency levels other than Beginner, Amateur, Competent, Proficient, Expert, map them to the closest of these five levels by deducing it from the resume. Take into consideration the user level of experience in the field (the years of experience, the projects, the job title). "
                f"Ensure that all proficiency levels in the output are only among these five levels. "
                f"Provide the skills in a clear, line-by-line format with each skill followed by its level of expertise, separated by a colon.\n\n"
                f"Example:\nPython: Expert\nCommunication: Proficient\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )

        skills_text = response.choices[0].message['content'].strip()
        logging.info(f"Extracted skills text: {skills_text}")

        # Process the skills into a list of dictionaries
        skills_list = []
        for line in skills_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                skill, level = line.split(':', 1)
                skills_list.append({"skill": skill.strip(), "level": level.strip()})
            else:
                # If no level is provided, assign a default level
                skills_list.append({"skill": line.strip(), "level": "Beginner"})


        return skills_list

    except Exception as e:
        logging.error(f"Error extracting skills: {e}")
        st.error(f"An error occurred while extracting skills: {e}")
        return []

# Enhanced Function to Categorize Skills into Soft and Technical while preserving proficiency levels
def categorize_skills(skills_list, retries=3):
    """
    Categorizes a list of skills into soft skills and technical skills using GPT-4.
    Preserves the proficiency levels.

    Parameters:
        skills_list (list): A list of dictionaries with 'skill' and 'level' keys.
        retries (int): Number of retry attempts in case of failure.

    Returns:
        tuple: Two lists containing soft skills and technical skills respectively, each as dictionaries with 'skill' and 'level'.
    """
    if not skills_list:
        return [], []

    skills_text = "\n".join([f"{skill['skill']}: {skill['level']}" for skill in skills_list])

    messages = [
        {"role": "system", "content": "You are an assistant that categorizes skills into soft skills and technical skills."},
        {"role": "user", "content": (
            "Please categorize the following skills into soft skills and technical skills. "
            "Maintain the proficiency levels as provided. "
            "Return the result in a valid JSON format with two keys: 'soft_skills' and 'technical_skills'. "
            "Each key should map to a list of objects, where each object has 'skill' and 'level'. "
            "Ensure that the JSON is properly formatted and complete. Do not include any additional text or explanations.\n\n"
            "Skills:\n" + skills_text
        )}
    ]

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,  # Increased tokens to accommodate larger skill lists
                temperature=0.3
            )

            categorized = response.choices[0].message['content'].strip()
            logging.info(f"Categorized skills response: {categorized}")

            # Basic validation to check if JSON is complete
            if not (categorized.startswith("{") and categorized.endswith("}")):
                raise json.JSONDecodeError("Incomplete JSON", categorized, len(categorized))

            # Attempt to parse the JSON response
            categorized_dict = json.loads(categorized)

            soft_skills = categorized_dict.get('soft_skills', [])
            technical_skills = categorized_dict.get('technical_skills', [])

            # Validate that both keys exist
            if 'soft_skills' not in categorized_dict or 'technical_skills' not in categorized_dict:
                raise json.JSONDecodeError("Missing keys in JSON", categorized, len(categorized))

            # Save to session state
            if 'soft_skills' not in st.session_state:
                st.session_state.soft_skills = []

            if 'technical_skills' not in st.session_state:
                st.session_state.technical_skills = []
            st.session_state.soft_skills = soft_skills
            st.session_state.technical_skills = technical_skills
            
            return soft_skills, technical_skills

        except json.JSONDecodeError as e:
            logging.warning(f"Attempt {attempt + 1} - JSON decoding failed: {e}")
            st.warning(f"Attempt {attempt + 1} - Failed to parse JSON. Retrying...")
            continue  # Retry

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} - Error categorizing skills: {e}")
            st.error(f"Attempt {attempt + 1} - An error occurred while categorizing skills: {e}")
            break  # Exit retry loop

    # After retries, return empty lists
    st.error("Failed to categorize skills after multiple attempts.")
    st.text(f"Last raw response:\n{categorized if 'categorized' in locals() else 'No response received.'}")
    return [], []
