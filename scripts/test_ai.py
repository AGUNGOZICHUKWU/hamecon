import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

"""Smoke test for the updated generator."""

from app.ai.generator import generate_phish_email, generate_phish_sms, generate_lesson

print("=== EMAIL: MTN MoMo, French, medium ===\n")
e = generate_phish_email("MTN MoMo deposit confirmation needed", "fr", "medium")
print("Subject:", e["subject"])
print(e["body_html"][:400], "...\n")

print("=== SMS: Orange Money, French, easy ===\n")
sms = generate_phish_sms("Orange Money cashout reversal", "fr", "easy")
print(sms, "\n")

print("=== SMS: Fake bank virtual card, French, hard ===\n")
sms2 = generate_phish_sms("Afriland virtual card activation", "fr", "hard")
print(sms2, "\n")

print("=== LESSON (for the Orange SMS) ===\n")
print(generate_lesson("(SMS, no subject)", sms, channel="sms", language="fr"))
