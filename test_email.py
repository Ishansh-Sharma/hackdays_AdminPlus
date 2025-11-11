import os
import textwrap
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# --- 1. CONFIGURATION & VALIDATION ---
load_dotenv()

# Make sure this matches your .env file key name EXACTLY
SENDGRID_API_KEY = os.getenv("send_grid_key") 

# This is your verified sender email. This is correct.
YOUR_VERIFIED_SENDER = "ishanshsharma43@gmail.com"

# --- Failsafe check ---
if not SENDGRID_API_KEY:
    print("Fatal Error: SENDGRID_API_KEY not set in .env file.")
    print("Please check your .env file and SendGrid API key.")
    print(f"Looking for key: 'send_grid_key'")
    exit() # Stop the script if the key is missing

# (I have REMOVED the incorrect check that was here)

# --- 2. THE EMAIL FUNCTION ---
def send_confirmation_email(student_email, student_name, slot_time_str):
    """
    Sends a formatted, styled confirmation email to the student.
    """
    
    # Create the email content.
    subject = "Appointment Confirmed: DTU Admin"
    html_content = textwrap.dedent(f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ width: 90%; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            h2 {{ color: #333; }}
            p {{ margin-bottom: 10px; }}
            b {{ color: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>DTU Admin Appointment Confirmation</h2>
            <p>Hello {student_name},</p>
            <p>Your appointment with the DTU Admin office has been confirmed.</p>
            <p><b>Date and Time:</b> {slot_time_str}</p>
            <p>Please be on time. If you need to reschedule, please contact the admin office.</p>
            <br>
            <p>Thank you,</p>
            <p>DTU Admin Automation Bot</p>
        </div>
    </body>
    </html>
    """)
    
    # Create the Mail object
    message = Mail(
        from_email=YOUR_VERIFIED_SENDER,
        to_emails=student_email,
        subject=subject,
        html_content=html_content
    )
    
    # Send the email
    try:
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        
        if response.status_code == 202:
            print(f"Email sent successfully to {student_email}!")
            print(f"Status Code: {response.status_code}")
            return True
        else:
            print(f"Error sending email. SendGrid returned code: {response.status_code}")
            print(f"Response Body: {response.body}")
            return False
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# --- 3. MAIN EXECUTION ---
if __name__ == "__main__":
    print("Sending a test email...")
    
    # --- !! CHANGE THESE FOR YOUR TEST !! ---
    test_student_email = "drdk1088@gmail.com"  # Send to yourself for testing
    test_student_name = "Ishansh Sharma"
    test_slot = "November 10, 2025 at 10:15 AM"
    # -----------------------------------------

    send_confirmation_email(
        test_student_email, 
        test_student_name, 
        test_slot
    )

    #time stamp - 3:38 Sending a test email...
#An unexpected error occurred: HTTP Error 403: Forbidden