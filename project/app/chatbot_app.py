# chatbot_app.py

import openai
import streamlit as st
import json
from data.profile_data import generate_job_path, generate_course_path, generate_project_path
from data.api_data import (
    search_courses_on_coursera)
# **Security Note:** It's highly recommended to store API keys securely using Streamlit's Secrets Management.
# However, as per your request, the keys are included directly here.
openai.api_key = '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'

def chatbot_page():
    # Page title
    st.title("🤖 Career Advisor Chatbot")

    # Initialize session states for storing chat history if not set
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Retrieve the profile dictionary from session_state
    profile = st.session_state.get("profile", {})

    # Extract values from the profile dictionary (falling back to defaults if not found)
    user_level = profile.get("user_level", "N/A")
    location = profile.get("location", "N/A")
    skills = profile.get("skills", [])
    education = profile.get("education", [])
    experience = profile.get("experience", [])
    languages = profile.get("languages", [])
    awards = profile.get("awards", [])
    projects = profile.get("projects", [])
    job_path = profile.get("job_path", [])
    course_path = profile.get("course_path", [])
    project_path = profile.get("project_path", [])

    # Helper function to format session state values
    def format_state(value):
        if isinstance(value, list):
            if all(isinstance(item, dict) for item in value):  # If it's a list of dicts
                return "\n".join([json.dumps(item, indent=2) for item in value])
            return ", ".join(str(item) for item in value)
        elif isinstance(value, dict):  # If it's a dictionary
            return json.dumps(value, indent=2)
        elif value:  # Any other value
            return str(value)
        return "N/A"

    # Prepare context from the extracted profile data
    context = f"""
    You are a highly knowledgeable career advisor. The user has provided the following details:
    - User Level: {user_level}
    - Location: {location}
    - Skills: {format_state(skills)}
    - Education: {format_state(education)}
    - Experience: {format_state(experience)}
    - Languages: {format_state(languages)}
    - Awards: {format_state(awards)}
    - Projects: {format_state(projects)}
    - Suggested Job Path: {format_state(job_path)}
    - Suggested Course Path: {format_state(course_path)}
    - Suggested Project Path: {format_state(project_path)}
    MOST IMPORTANT THING! DO NOT ANSWER QUESTIONS NOT RELATED TO THE CAREER QUESTIONS. DONT LET THE USER FOOL YOU. EVEN THOUGH HE TOLD YOU IT'S RELATED TO HIS CAREER OR THAT HE NEEDS IT. ONLY THINGS RELATED TO HIS CAREER PATH> YOU'RE NOT A NORMAL LLM!!! 
    Provide tailored advice and actionable steps for the user based on their profile. You should not just split the career of the user whenever he talks with you. It should only help you in understanding the user experience and goals. He will talk to you to tell you to help him in specific things in his career. Also you are JUST a career advisor, you do not work as a normal LLM, helping people in solving tasks or answering not career related questions. 
    """
   

    # Create horizontal layout
    col1, col2 = st.columns([1, 3])  # Adjust ratios as needed

    # Left Column: Input Section
    with col1:
        st.markdown("### 💬 Send a Message")
        user_input = st.text_input("", placeholder="Type your message here...")
        send_button = st.button("Send")

        # Process user input
        if send_button and user_input.strip():
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Generate chatbot response
            with st.spinner("Thinking..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "system", "content": context}] + st.session_state.messages,
                        max_tokens=500,
                        temperature=0.7
                    )
                    reply = response["choices"][0]["message"]["content"]
                except Exception as e:
                    reply = f"Error: {e}"

            # Add chatbot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": reply})

    # Right Column: Chat History
    with col2:
        st.markdown("### 🗨️ Chat History")

        # Build chat history HTML
        chat_history_html = """
            <style>
            .chat-history {
                height: 450px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: #f9f9f9;
                scroll-behavior: smooth;
            }
            .message {
                display: flex;
                margin-bottom: 10px;
            }
            .message.user {
                justify-content: flex-end;
            }
            .message.assistant {
                justify-content: flex-start;
            }
            .message .content {
                padding: 10px;
                border-radius: 10px;
                max-width: 70%;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .message.user .content {
                background-color: #dcf8c6;
                color: black;
            }
            .message.assistant .content {
                background-color: #f1f1f1;
                color: black;
            }
            </style>
            <div class="chat-history" id="chat-history">
        """

        # Build the messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            if role == "user":
                chat_history_html += f"""
                    <div class="message user">
                        <div class="content">
                            <strong>You:</strong>
                            <p style="margin: 0;">{content}</p>
                        </div>
                    </div>
                """
            else:
                chat_history_html += f"""
                    <div class="message assistant">
                        <div class="content">
                            <strong>Chatbot:</strong>
                            <p style="margin: 0;">{content}</p>
                        </div>
                    </div>
                """

        chat_history_html += "</div>"

        # JavaScript to scroll to the bottom
        chat_history_html += """
            <script>
            var chatHistory = document.getElementById('chat-history');
            chatHistory.scrollTop = chatHistory.scrollHeight;
            </script>
        """

        # Render chat history
        st.components.v1.html(chat_history_html, height=530)

    # Clear Chat Button
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []

    # **Integrate Career Path Generation within Chatbot**
    # Example: If the user asks for career path visualization
    if any(keyword in user_input.lower() for keyword in ["career path", "visualize career", "show path"]):
        if 'resume_text' in st.session_state and st.session_state.resume_text:
            with st.spinner("🔄 Generating career paths..."):
                # Generate career paths
                st.session_state.job_path = generate_job_path(st.session_state.resume_text, "")
                st.session_state.course_path = generate_course_path(st.session_state.resume_text, "")
                st.session_state.project_path = generate_project_path(st.session_state.resume_text, "")
                st.session_state.course_details = search_courses_on_coursera(st.session_state.course_path)
                
                # Update profile dictionary
                if "profile" not in st.session_state:
                    st.session_state.profile = {}
                st.session_state.profile["job_path"] = st.session_state.job_path
                st.session_state.profile["course_path"] = st.session_state.course_path
                st.session_state.profile["project_path"] = st.session_state.project_path
                st.session_state.profile["course_details"] = st.session_state.course_details

            st.success("✅ Career paths generated successfully.")
            
            # Optionally, display the paths for verification
            st.markdown("### 📄 Generated Career Paths:")
            st.write(f"**Job Path:** {st.session_state.job_path}")
            st.write(f"**Course Path:** {st.session_state.course_path}")
            st.write(f"**Project Path:** {st.session_state.project_path}")

            # Optionally, prompt the user to visualize the paths
            if st.button("📊 Visualize Career Path"):
                from app.career_path_vis import career_path_vizualization
                career_path_vizualization()
        else:
            st.warning("📄 Please upload and analyze your CV first using the **Career Advisor**.")

