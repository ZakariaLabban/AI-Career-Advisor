import streamlit as st
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector

openai.api_key = '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'


# Your existing database settings and vectorstore initialization
CONNECTION_STRING = "postgresql+psycopg2://postgres:test@vector_db_instance:5432/vector_db"

COLLECTION_NAME = 'state_of_union_vectors'

# Initialize the vector store with the same syntax you used
embedding_model = OpenAIEmbeddings(openai_api_key=openai.api_key)
db = PGVector(
    connection_string=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_model
)

def generate_embedding(text):
    """
    Generate embeddings for a given text using OpenAI's text-embedding-ada-002 model.
    """
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

def combine_skills_from_json(soft_skills, technical_skills):
    """
    Combines soft skills and technical skills into a single comma-separated string.
    """
    soft_skills_list = [skill['skill'] for skill in soft_skills]
    technical_skills_list = [skill['skill'] for skill in technical_skills]
    return ", ".join(soft_skills_list + technical_skills_list)

def process_combined_skills(combined_skills_string):
    """
    Process the combined skills string:
    - Generate its embedding
    - Use PGVector's similarity_search_with_score_by_vector to find top matches
    - Return the matches with their similarity scores and document metadata/content
    """
    query_embedding = generate_embedding(combined_skills_string)

    # Get top 10 matches, then we will filter to top 3 distinct categories
    closest_matches = db.similarity_search_with_score_by_vector(query_embedding, k=10)
    
    # Convert to a structured list
    results = []
    for doc, similarity_score in closest_matches:
        category = doc.metadata.get('category', 'Unknown')
        results.append({
            "similarity": similarity_score,
            "category": category,
            "content": doc.page_content
        })
    
    # Filter to get only top 3 distinct categories
    distinct_categories = set()
    filtered_results = []
    for result in results:
        if result['category'] not in distinct_categories:
            distinct_categories.add(result['category'])
            filtered_results.append(result)
        if len(filtered_results) == 3:
            break

    return filtered_results

def find_ideal_job():
    """
    This function will:
    - Combine skills from session state
    - Process them
    - Display the top 3 closest distinct matches
    """
    st.title("Find Your Ideal Job")
    st.header("Skill Combination Tool")

    # Get the skills from session state
    soft_skills = st.session_state.get('soft_skills', [])
    technical_skills = st.session_state.get('technical_skills', [])

    # Combine them
    combined_skills_string = combine_skills_from_json(soft_skills, technical_skills)
    st.header("Combined Skills")
    st.write(combined_skills_string)

    # Process and retrieve closest matches
    results = process_combined_skills(combined_skills_string)

    if results and combined_skills_string:
        st.header("Closest Matches")
        for i, result in enumerate(results, start=1):
            st.subheader(f"Match {i}")
            #st.write(f"**Similarity:** {result['similarity']}")
            st.write(f"**Category:** {result['category']}")
            st.write(f"**Content:** {result['content']}")
            st.markdown("---")
    else:
        st.warning("No matches found.")

###########################
# Example of calling it (in main.py or wherever you handle navigation):
# if app_mode == "Find your Ideal Job":
#     find_ideal_job()
###########################
