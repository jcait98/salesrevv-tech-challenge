import os
import requests
from datetime import datetime, timedelta

class NeetoCalClient:
    def __init__(self, api_key, workspace, meeting_slug):
        self.api_key = api_key
        self.workspace = workspace
        self.meeting_slug = meeting_slug
        self.base_url = f"https://{self.workspace}.neetocal.com/api/external/v1"
        self.time_zone = "America/New_York"

    def _get_headers(self):
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def list_slots(self, year, month):
        url = f"{self.base_url}/slots/{self.meeting_slug}"
        params = {
            "year": year,
            "month": month,
            "time_zone": self.time_zone
        }
        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json()  # List of available slots
        else:
            raise Exception(f"Failed to list slots: {response.json()}")

    def list_next_week_availability(self, root_date):

        for i in range(7):
            day = root_date + timedelta(days=i)
            try:
                slots = self.list_slots(
                    meeting_slug=self.meeting_slug,
                    year=day.year,
                    month=day.month,
                    time_zone=self.time_zone
                )
                #print(f"Available slots on {day.date()}: {slots}")
                return slots
            
            except Exception as e:
                print(f"Error fetching slots for {day.date()}: {e}")
                
    def create_booking(self, name, email, slot_date, slot_start_time, form_responses=None):
        url = f"{self.base_url}/bookings"
        payload = {
            "meeting_slug": self.meeting_slug,
            "name": name,
            "email": email,
            "slot_date": slot_date,
            "slot_start_time": slot_start_time,
            "time_zone": self.time_zone,
            "form_responses": form_responses
        }
        response = requests.post(url, headers=self._get_headers(), json=payload)
        if response.status_code == 200:
            return response.json()  # Booking confirmation details
        else:
            raise Exception(f"Failed to create booking: {response.json()}")

    def list_bookings(self, host_email=None, client_email=None, booking_type=None):
        url = f"{self.base_url}/bookings"
        params = {}
        if host_email:
            params['host_email'] = host_email
        if client_email:
            params['client_email'] = client_email
        if booking_type:
            params['type'] = booking_type

        response = requests.get(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json()  # List of bookings
        else:
            raise Exception(f"Failed to list bookings: {response.json()}")

    def cancel_booking(self, booking_sid, cancel_reason=None):
        url = f"{self.base_url}/bookings/{booking_sid}/cancel"
        params = {}
        if cancel_reason:
            params["cancel_reason"] = cancel_reason
        response = requests.post(url, headers=self._get_headers(), params=params)
        if response.status_code == 200:
            return response.json()  # Cancellation confirmation
        else:
            raise Exception(f"Failed to cancel booking: {response.json()}")
