from datetime import datetime, timedelta
from ai_appointment_scheduler import AIAppointmentScheduler  # This module uses OpenAI for AI-driven responses

class SessionManager:
    def __init__(self, neeto_client, openai_client):
        self.conversation_history = []
        self.selected_slot = None
        self.neeto_client = neeto_client
        self.available_slots = self.fetch_slots()
        self.ai_scheduler = AIAppointmentScheduler(neeto_client, openai_client)

    def add_message(self, role, content):
        self.conversation_history.append({"role": role, "content": content})

    def get_conversation(self):
        return self.conversation_history

    def detect_scheduling_intent(self, message):
        response = self.ai_scheduler.detect_scheduling_intent(message)
        return "yes" in response.lower()

    def get_ai_response(self, user_input):
        self.add_message("user", user_input)
        ai_response = self.ai_scheduler.interpret_user_message(self.get_conversation())
        self.add_message("assistant", ai_response)
        return ai_response

    def parse_available_slots(self, available_slots):
        slot_options = []
        for date_entry in available_slots['slots']:
            date_str = date_entry['date']
            for time_range, slot_info in date_entry['slots'].items():
                if slot_info['is_available']:
                    formatted_slot = f"{date_str}: {slot_info['start_time']} - {slot_info['end_time']}"
                    slot_options.append({
                        "display": formatted_slot,
                        "date": date_str,
                        "time_range": time_range
                    })
        return slot_options

    def fetch_slots(self):
        today = datetime.now()
        for i in range(7):
            day = today + timedelta(days=i)
            try:
                slots = self.neeto_client.list_slots(year=day.year, month=day.month)
                return self.parse_available_slots(slots)
            except Exception as e:
                print(f"Error fetching slots for {day.date()}: {e}")
        return []

    def set_selected_slot(self, slot):
        self.selected_slot = slot

    def book_appointment(self):
        if not self.selected_slot:
            return None
        
        # Parse the selected slot to get date and time
        slot_details = self.selected_slot.split(": ")
        slot_date = slot_details[0].strip()  # "2024-11-11"
        slot_time_range = slot_details[1].strip()  # "10:30 AM - 11:00 AM"
        slot_start_time = slot_time_range.split(" - ")[0]  # "10:30 AM"

        # Call create_booking with the parsed details
        self.neeto_client.create_booking(
            name="Placeholder Name",
            email="placeholder@example.com",
            slot_date=slot_date,
            slot_start_time=slot_start_time
        )

