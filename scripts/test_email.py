import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.email.sender import send_email

send_email("laflam984@gmail.com", "Hamecon SMTP test",
           "<p>If you can read this, Gmail SMTP works.</p>")
print("Sent. Check your inbox.")
