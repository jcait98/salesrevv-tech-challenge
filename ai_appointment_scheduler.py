from openai import OpenAI
from datetime import datetime, timedelta
import os
import regex as re

class AIAppointmentScheduler:
    def __init__(self, neeto_client, openai_api_key, system_prompt_path="fitness_prompt1.txt", scheduling_prompt_path="scheduling_prompt1.txt"):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.neeto_client = neeto_client
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.system_prompt = self._load_system_prompt(system_prompt_path)
        self.scheduling_prompt = self._load_system_prompt(scheduling_prompt_path)
        self.meeting_slug = "personal-training-session"

    def _load_system_prompt(self, path):
        """
        Loads the system prompt from a file to provide context for the AI model.
        """
        with open(path, 'r') as file:
            return file.read().strip()
        
    def interpret_user_message(self, message, prompt=None):
        """
        Uses OpenAI API to interpret the user's message and provide a response, 
        including the system prompt for context.
        """

        if prompt=="scheduling":
            system_prompt = self.scheduling_prompt
        else:
            system_prompt=self.system_prompt

        # Create a conversation history with the system prompt and user input
        conversation_context = [
            {"role": "system", "content": system_prompt}
        ]
        conversation_context.extend(message)

        # Call OpenAI API to generate a response
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=conversation_context
        )
        
        # Extract and return the AI's response
        reply_content = response.choices[0].message.content.strip()
        return reply_content

    def get_available_slots(self, start_date, end_date):
        """
        This method fetches available slots for appointments from the NeetoCal API.
        """
        slots = []
        current_date = start_date
        while current_date <= end_date:
            month_slots = self.neeto_client.list_slots(
                year=current_date.year,
                month=current_date.month
            )
            slots += month_slots
            current_date += timedelta(days=30)  # Move to the next month
        return slots

    def get_ai_response(self, user_message):
        """
        Calls OpenAI API to generate a response for the assistant based on the user's message.
        """
        return self.interpret_user_message(user_message)

    def confirm_booking(self, user_name, user_email, selected_slot):
        """
        Confirms a booking by making a call to NeetoCal's booking API with the user's info.
        """
        booking_confirmation = self.neeto_client.create_booking(
            meeting_slug=self.meeting_slug,
            name=user_name,
            email=user_email,
            slot_date=selected_slot['date'],
            slot_start_time=selected_slot['start_time'],
            time_zone="America/New_York"
        )
        return booking_confirmation
    
    def detect_scheduling_intent(self, message):
        prompt=f"Parse the following message for any references to scheduling or finding a time. Reply only with yes or no. Do not reply yes to requests for confirmation it is currently a good time to talk, such as 'is now a good time to discuss this?'. Only respond yes when it seems someone is suggesting or requesting to schedule a future appointment:\n\n\"{message}\""
        
        print(prompt)
        # Use OpenAI to parse the message for scheduling intent
        response = self.openai_client.chat.completions.create(model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}], max_tokens=50)

        print("detect", response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()

    def extract_time_from_user_response(self, user_response):
        """
        Parses the user response to extract any time information.
        """
        # Use OpenAI API or regex to detect times mentioned in user input
        # Example regex to detect times (adjust as needed for reliability)
        match = re.search(r'\b([1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)\b', user_response, re.IGNORECASE)
        if match:
            # Parse and return datetime object of extracted time
            return datetime.strptime(match.group(), "%I:%M %p")
        return None