import os
import datetime
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
CALENDAR_ID = os.getenv("calander_api")
SERVICE_ACCOUNT_FILE = 'service-account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Define the admin's working hours in local time (e.g., India Standard Time)
LOCAL_TIMEZONE = pytz.timezone('Asia/Kolkata')
WORK_START_HOUR = 10  # 10:00 AM
WORK_END_HOUR = 16    # 4:00 PM (16:00)
SLOT_DURATION_MINUTES = 15

# --- 1. AUTHENTICATE ---
def get_calendar_service():
    """Authenticates with the Google Calendar API using a service account."""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except FileNotFoundError:
        print(f"Error: {SERVICE_ACCOUNT_FILE} not found.")
        return None
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None

# --- 2. FIND NEXT AVAILABLE SLOT ---
def find_next_slot(service):
    """
    Finds the next available 15-minute slot within working hours.
    This is complex "calendar math".
    """
    if not CALENDAR_ID:
        print("Error: CALENDAR_ID not set in .env file.")
        return None

    # Get 'now' and 'end_date' (e.g., 7 days from now) in the correct timezone
    now = LOCAL_TIMEZONE.localize(datetime.datetime.now())
    end_date = now + datetime.timedelta(days=7)
    
    # Get all busy events from now until end_date
    print("Finding next slot... Fetching busy events...")
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        busy_events = events_result.get('items', [])
    except Exception as e:
        print(f"Error fetching events: {e}")
        return None

    # Start checking from 'now', but round up to the next 15-min interval
    start_time = now
    if start_time.minute % 15 != 0:
        start_time = start_time.replace(
            minute=(start_time.minute // 15 + 1) * 15, 
            second=0, 
            microsecond=0
        )
    
    # Loop day by day, then slot by slot
    current_time = start_time
    while current_time < end_date:
        # Is this slot within working hours?
        if WORK_START_HOUR <= current_time.hour < WORK_END_HOUR:
            
            # Define the 15-minute slot we want to check
            slot_start = current_time
            slot_end = current_time + datetime.timedelta(minutes=SLOT_DURATION_MINUTES)
            
            # Check if this slot overlaps with any busy event
            is_free = True
            for event in busy_events:
                event_start_str = event['start'].get('dateTime', event['start'].get('date'))
                event_end_str = event['end'].get('dateTime', event['end'].get('date'))
                
                # Convert event times to datetime objects (handling all-day events)
                if 'T' in event_start_str:
                    event_start = datetime.datetime.fromisoformat(event_start_str)
                else: # All-day event
                    event_start = LOCAL_TIMEZONE.localize(datetime.datetime.fromisoformat(event_start_str))

                if 'T' in event_end_str:
                    event_end = datetime.datetime.fromisoformat(event_end_str)
                else: # All-day event
                    event_end = LOCAL_TIMEZONE.localize(datetime.datetime.fromisoformat(event_end_str))

                # Simple overlap check
                if max(slot_start, event_start) < min(slot_end, event_end):
                    is_free = False
                    # This slot is busy. Fast-forward our check to the end of this busy event.
                    current_time = event_end
                    if current_time.minute % 15 != 0:
                         current_time = current_time.replace(
                            minute=(current_time.minute // 15 + 1) * 15, 
                            second=0, 
                            microsecond=0
                        )
                    break # Stop checking other events, move to next slot
            
            if is_free:
                # Found a free slot!
                return {"start": slot_start, "end": slot_end}
        
        # If not in working hours or slot was busy, move to the next 15-min slot
        if not is_free:
            continue # The loop will advance 'current_time' from the event_end
        
        current_time += datetime.timedelta(minutes=SLOT_DURATION_MINUTES)
        
        # If end of day, jump to next day's start
        if current_time.hour >= WORK_END_HOUR:
            current_time = current_time.replace(
                hour=WORK_START_HOUR, minute=0, second=0
            ) + datetime.timedelta(days=1)

    return None # No free slot found in the next 7 days

# --- 3. BOOK THE SLOT ---
def book_slot(service, slot, student_id="Test Student 001"):
    """Creates a new event on the calendar to "book" the slot."""
    print(f"Booking slot: {slot['start']} to {slot['end']}...")
    
    event = {
        'summary': f'Booked - {student_id}',
        'description': f'Appointment for {student_id} (via Admin Bot)',
        'start': {
            'dateTime': slot['start'].isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': slot['end'].isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
    }
    
    try:
        created_event = service.events().insert(
            calendarId=CALENDAR_ID, body=event).execute()
        print(f"Success! Slot booked. Event ID: {created_event['id']}")
        return created_event
    except Exception as e:
        print(f"Error booking slot: {e}")
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    service = get_calendar_service()
    if service:
        # First, add a fake "busy" event (e.g. Lunch) for testing
        # You can comment this out later
        # print("Adding a 'Lunch' block for testing...")
        # book_slot(service, {
        #     "start": LOCAL_TIMEZONE.localize(datetime.datetime.now().replace(hour=13, minute=0, second=0)),
        #     "end": LOCAL_TIMEZONE.localize(datetime.datetime.now().replace(hour=14, minute=0, second=0))
        # }, "ADMIN LUNCH")

        # 1. Find the next slot
        available_slot = find_next_slot(service)
        
        if available_slot:
            print(f"\nFound available slot: {available_slot['start']}")
            
            # 2. Book it
            book_slot(service, available_slot, "Student_RollNo_12345")
        else:
            print("\nNo available slots found in the next 7 days.")