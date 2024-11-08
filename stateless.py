import streamlit as st
from datetime import datetime
from session_manager import SessionManager
from ai_appointment_scheduler import AIAppointmentScheduler
from neetocal_client import NeetoCalClient  # Assuming a separate client to interact with NeetoCal
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
neeto_cal_api_key = os.getenv("NEETO_CAL_API_KEY")
workspace = "salesrevv-challenge"
meeting_slug = "personal-training-session"

# Initialize NeetoCal and OpenAI clients
neeto_client = NeetoCalClient(api_key=neeto_cal_api_key, workspace=workspace, meeting_slug=meeting_slug)
openai_client = OpenAI(api_key=openai_api_key)

# Initialize SessionManager in session state if it doesn't exist
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager(neeto_client, openai_client)

# Access the session_manager from session state
session_manager = st.session_state.session_manager

# Set up Streamlit UI
st.title("AI-Powered Appointment Scheduler")

# Main function
def main():
    # Create a text box for user input
    user_input = st.text_input("Enter your message:", "")

    # Create a submit button
    if st.button("Submit") and user_input:

        # If a scheduling intent is detected, proceed with scheduling functionality
        if 'triggering_message' in st.session_state and st.session_state.triggering_message:            
            st.session_state.scheduling_triggered = True
            #session_manager.manage_scheduling(user_input)

            # Display available time slots and allow user to select one
            if session_manager.available_slots: 
                selected = st.selectbox("Choose an available time slot:", [slot['display'] for slot in session_manager.available_slots])
                session_manager.set_selected_slot(selected)

                print("setting slot", session_manager.selected_slot)
                session_manager.book_appointment()
                st.success(f"Appointment confirmed for {session_manager.selected_slot}")

        else:
            # Get AI response and check for scheduling intent
            ai_response = session_manager.get_ai_response(user_input)
            
            # Check if the response or user's input indicates a scheduling intent
            triggering_message = None
            if session_manager.detect_scheduling_intent(user_input):
                triggering_message = user_input
            elif session_manager.detect_scheduling_intent(ai_response):
                triggering_message = ai_response

            st.session_state.triggering_message = triggering_message

    st.subheader("Conversation History")

    # Display the conversation history
    conversation = session_manager.get_conversation()
    for message in conversation:
        if message["role"] == "user":
            st.write(f"**You:** {message['content']}")
        else:
            st.write(f"**Sam:** {message['content']}")


# Run the app
if __name__ == "__main__":
    main()
