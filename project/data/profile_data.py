import openai
import json
from config import openai, ADZUNA_APP_ID, ADZUNA_APP_KEY, GITHUB_TOKEN, coursera_token
import streamlit as st
import re
import requests
import openai

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
def extract_education(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts education details from a user's resume. "
                "Provide the information in strict JSON format with an object containing an array named 'education'. "
                "Each education entry should include the following keys: Degree, Institution, Years, Details. "
                "If no professional education is found, return an empty array. "
                "Enclose the JSON within a code block with 'json' specified."
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract the education history from the following resume text. Include all relevant education entries.\n\nResume:\n{resume_text}"
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

        education_text = response.choices[0].message['content'].strip()



        # Extract JSON from code block if present
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, education_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            # If no code block, attempt to extract JSON object
            start = education_text.find("{")
            end = education_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = education_text[start:end+1]
            else:
                # If unable to find JSON structure, raise an error
                raise ValueError("No JSON object found in the response.")

        # Attempt to parse JSON
        education_json = json.loads(json_str)

        # Validate and process
        education_list = []
        for edu in education_json.get("education", []):
            degree = edu.get("Degree", "")
            institution = edu.get("Institution", "")
            years = edu.get("Years", "")
            details = edu.get("Details", "")

            # Handle 'Details' being a list or string
            if isinstance(details, list):
                details = "; ".join(details)
            elif isinstance(details, dict):
                # If Details is a dict, convert to string representation
                details = json.dumps(details)
            elif not isinstance(details, str):
                details = str(details)

            # Only add entries with at least Degree and Institution
            if degree and institution:
                education_entry = {
                    "Degree": degree.strip() if isinstance(degree, str) else str(degree),
                    "Institution": institution.strip() if isinstance(institution, str) else str(institution),
                    "Years": years.strip() if isinstance(years, str) else str(years),
                    "Details": details.strip() if isinstance(details, str) else str(details)
                }
                education_list.append(education_entry)



        return education_list

    except json.JSONDecodeError:
        st.error("Failed to parse education information. Please ensure the resume format is consistent and that the response is valid JSON.")
        return []
    except ValueError as ve:
        st.error(f"Parsing Error: {ve}")
        return []
    except Exception as e:
        st.error(f"Error extracting education: {e}")
        return []
# Function to extract professional experience from resume
def extract_experience(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts professional experience from a user's resume. "
                "Provide the information in strict JSON format with an object containing an array named 'experience'. "
                "Each experience entry should include the following keys: Title, Company, Years, Details. "
                "If no professional experience is found, return an empty array. "
                "Enclose the JSON within a code block with 'json' specified."
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract the professional experience from the following resume text. Any type of experience cited in the resume is considered professional experience.\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=700,
            temperature=0.3
        )

        experience_text = response.choices[0].message['content'].strip()

 

        # Extract JSON from code block if present
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, experience_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            # If no code block, attempt to extract JSON object
            # Find the first { and the last }
            start = experience_text.find("{")
            end = experience_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = experience_text[start:end+1]
            else:
                # If unable to find JSON structure, raise an error
                raise ValueError("No JSON object found in the response.")

        # Attempt to parse JSON
        experience_json = json.loads(json_str)

        # Validate and process
        experience_list = []
        for exp in experience_json.get("experience", []):
            title = exp.get("Title", "N/A")
            company = exp.get("Company", "N/A")
            years = exp.get("Years", "N/A")
            details = exp.get("Details", "N/A")

            # If Details is a list, join them into a single string
            if isinstance(details, list):
                details = "; ".join(details)

            # Only add entries with at least Title and Company
            if title != "N/A" and company != "N/A":
                experience_list.append({
                    "Title": title.strip(),
                    "Company": company.strip(),
                    "Years": years.strip(),
                    "Details": details.strip()
                })



        return experience_list

    except json.JSONDecodeError:
        st.error("Failed to parse experience information. Please ensure the resume format is consistent and that the response is valid JSON.")
        return []
    except ValueError as ve:
        st.error(f"Parsing Error: {ve}")
        return []
    except Exception as e:
        st.error(f"Error extracting experience: {e}")
        return []# Function to extract languages from resume
def infer_cv_language(resume_text):
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that detects the primary language of a given text."
        },
        {
            "role": "user",
            "content": (
                f"Detect the primary language of the following resume text. Provide only the language name.\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=10,
            temperature=0.3
        )

        language = response.choices[0].message['content'].strip()
        return language
    except Exception as e:
        st.error(f"Error inferring CV language: {e}")
        return None


def extract_languages(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts language proficiencies from a user's resume. "
                "Provide the information in strict JSON format with an array named 'languages'. "
                "Each language entry should include the following keys: Language, Level. "
                "If no languages are found, return an empty array."
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract the languages and their proficiency levels from the following resume text. "
                f"Do not include languages as skills.\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            temperature=0.3
        )

        languages_text = response.choices[0].message['content'].strip()

        # Ensure the response is enclosed in a JSON object
        if not languages_text.startswith("{") and not languages_text.startswith("[" ):
            languages_text = f"{{\"languages\": {languages_text}}}"

        # Attempt to parse JSON
        languages_json = json.loads(languages_text)

        # Process the languages into a list of dictionaries
        languages_list = []
        for lang in languages_json.get("languages", []):
            language = lang.get("Language", "").strip()
            level = lang.get("Level", "").strip()
            if language:
                languages_list.append({"Language": language, "Level": level})

        # If no languages are extracted, infer the CV language
        if not languages_list:
            inferred_language = infer_cv_language(resume_text)
            if inferred_language:
                languages_list.append({"Language": inferred_language, "Level": "Native/Bilingual"})
                
            
           



        return languages_list

    except json.JSONDecodeError:
        st.error("Failed to parse languages information. Please ensure the resume format is consistent.")
        return []
    except Exception as e:
        st.error(f"Error extracting languages: {e}")
        return []

# Function to extract awards from resume
def extract_awards(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts awards from a user's resume. "
                "Provide the information in strict JSON format with an object containing an array named 'awards'. "
                "Each award entry should be a string. "
                "If no awards are found, return an empty array. "
                "Enclose the JSON within a code block with 'json' specified."
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract any awards or recognitions from the following resume text.\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=200,
            temperature=0.3
        )

        awards_text = response.choices[0].message['content'].strip()



        # Extract JSON from code block if present
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, awards_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            # If no code block, attempt to extract JSON object
            start = awards_text.find("{")
            end = awards_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = awards_text[start:end+1]
            else:
                # If unable to find JSON structure, raise an error
                raise ValueError("No JSON object found in the response.")

        # Attempt to parse JSON
        awards_json = json.loads(json_str)

        # Validate and process
        awards_list = []
        for award in awards_json.get("awards", []):
            if isinstance(award, str):
                award_clean = award.strip()
                if award_clean:
                    awards_list.append(award_clean)
            else:
                # If award is not a string, convert it to string
                award_str = json.dumps(award).strip()
                if award_str:
                    awards_list.append(award_str)



        return awards_list

    except json.JSONDecodeError:
        st.error("Failed to parse awards information. Please ensure the resume format is consistent and that the response is valid JSON.")
        return []
    except ValueError as ve:
        st.error(f"Parsing Error: {ve}")
        return []
    except Exception as e:
        st.error(f"Error extracting awards: {e}")
        return []# Function to extract projects from resume
def extract_projects(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts project information from a user's resume. "
                "Provide the information in strict JSON format with an object containing an array named 'projects'. "
                "Each project entry should include the following keys: Title, Description. "
                "If no projects are found, return an empty array. "
                "Enclose the JSON within a code block with 'json' specified."
            )
        },
        {
            "role": "user",
            "content": (
                f"Extract the projects from the following resume text, including their descriptions. "
                f"Provide the information in JSON format with an array of project entries. "
                f"Each entry should have the keys: Title, Description.\n\nResume:\n{resume_text}"
            )
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.3
        )

        projects_text = response.choices[0].message['content'].strip()

   

        # Extract JSON from code block if present
        json_pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, projects_text, re.DOTALL | re.IGNORECASE)
        if match:
            json_str = match.group(1)
        else:
            # If no code block, attempt to extract JSON object
            start = projects_text.find("{")
            end = projects_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                json_str = projects_text[start:end+1]
            else:
                # If unable to find JSON structure, raise an error
                raise ValueError("No JSON object found in the response.")

        # Attempt to parse JSON
        projects_json = json.loads(json_str)

        # Validate and process
        projects_list = []
        for proj in projects_json.get("projects", []):
            title = proj.get("Title", "")
            description = proj.get("Description", "")

            # Handle 'Description' being a list or string
            if isinstance(description, list):
                description = "; ".join(description)
            elif isinstance(description, dict):
                # If Description is a dict, convert to string representation
                description = json.dumps(description)
            elif not isinstance(description, str):
                description = str(description)

            # Only add entries with at least Title and Description
            if title and description:
                project_entry = {
                    "Title": title.strip() if isinstance(title, str) else str(title),
                    "Description": description.strip() if isinstance(description, str) else str(description)
                }
                projects_list.append(project_entry)



        return projects_list

    except json.JSONDecodeError:
        st.error("Failed to parse project information. Please ensure the resume format is consistent and that the response is valid JSON.")
        return []
    except ValueError as ve:
        st.error(f"Parsing Error: {ve}")
        return []
    except Exception as e:
        st.error(f"Error extracting projects: {e}")
        return []


def generate_job_path(resume_text, feedback):
    combined_input = resume_text + "\nUser Feedback:\n" + feedback
    messages = [
        {"role": "system", "content": "You are a career advisor creating a four-step career path for a user based on their resume and feedback. Each step should include a clear and widely recognized job title that is likely to appear as a listing on Adzuna. Each job title should represent a common career level progression, from entry-level to advanced roles. Provide only the job title for each step. If the user feedback has is not related to his career path (like I love Paris or give me a sandwich) then don't take it into consideration. IMPORTANT: Also make sure you allign them with the experience of the user. So if the user for example is a professor with 20 years of experience, you cannot give him a job as a associate professor for example. BE LOGICAL.THINK WELL. "},
        {"role": "user", "content": f"Generate a four-step career path for job positions the user can find on Adzuna, based on the following resume and feedback.\n\n{combined_input}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )

    steps = response.choices[0].message['content'].strip().split("\n")
    steps = [step.strip().lstrip("1. ").lstrip("2. ").lstrip("3. ").lstrip("4. ") for step in steps if step.strip()]
    return steps[:4]

def generate_course_path(resume_text, feedback):
    # First, generate the job path
    job_steps = st.session_state.job_path
    
    combined_input = resume_text + "\nUser Feedback:\n" + feedback + "\nJob Path:\n" + "\n".join(job_steps)
    messages = [
        {"role": "system", "content": "You are a career advisor creating a four-step learning and development path of courses a user should take based on their career path, resume, and feedback. Each step should include a course title that aligns with the corresponding job step and represents progressive learning in standard career paths and is likely to be found on Coursera. Provide only the course title for each step in this path, without any additional information."},
        {"role": "user", "content": f"Generate a clear four-step learning and development path of courses for the user to progress in their career, based on the following resume, feedback, and job path.\n\n{combined_input}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )

    steps = response.choices[0].message['content'].strip().split("\n")
    steps = [step.strip().lstrip("1. ").lstrip("2. ").lstrip("3. ").lstrip("4. ") for step in steps if step.strip()]
    return steps[:4]

def generate_project_path(resume_text, feedback):
    # First, generate the job path
    job_steps = st.session_state.job_path
    
    combined_input = resume_text + "\nUser Feedback:\n" + feedback + "\nJob Path:\n" + "\n".join(job_steps)
    messages = [
        {"role": "system", "content": "You are a career advisor creating a four-step development path of open-source project titles that a user should work on based on their career path, resume, and feedback. Each step should include a project title related to the corresponding job step and commonly searched repositories on GitHub, helping the user build skills progressively. Provide only the project title for each step, without any additional information."},
        {"role": "user", "content": f"Generate a four-step project path for the user to follow, based on the following resume, feedback, and job path. The project titles should be findable on GitHub.\n\n{combined_input}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )

    steps = response.choices[0].message['content'].strip().split("\n")
    steps = [step.strip().lstrip("1. ").lstrip("2. ").lstrip("3. ").lstrip("4. ") for step in steps if step.strip()]
    return steps[:4]


# Function to generate course descriptions
def generate_course_descriptions(course_details):
    descriptions = []
    for course in course_details:
        title = course['title']
        url = course['url']
        description = course.get("description", "")
        if not description or description == "No description available.":
            # Generate description using GPT
            messages = [
                {"role": "system", "content": "You are an assistant that generates concise and informative course descriptions."},
                {"role": "user", "content": f"Generate a concise and informative description for the following course title:\n\nCourse Title: {title}"}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )

            generated_description = response.choices[0].message['content'].strip()
            descriptions.append(generated_description)
        else:
            descriptions.append(description)
    return descriptions