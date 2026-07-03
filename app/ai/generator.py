"""
app/ai/generator.py - Claude-powered Hameçon content generator.
Generates email phish, SMS phish, and beginner-friendly teachable lessons.
Tuned for the Cameroonian threat landscape (MTN MoMo, Orange Money, local banks).
"""

import os
import re
from dotenv import load_dotenv
import anthropic

load_dotenv()
_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
_MODEL = "claude-sonnet-4-5"

_CAMEROON_CONTEXT = """
CAMEROONIAN PHISHING THREAT LANDSCAPE — REALISTIC PATTERNS TO MIMIC

LANGUAGE & REGISTER:
- 90% of phishing in Cameroon arrives in French; some in English (NW/SW regions); often code-switches.
- Casual tone (no excessive "vous"), urgent imperative verbs, generic greeting ("Cher client"/"Madame/Monsieur").
- Mobile money texts feel rushed and abbreviated: "URGENT", "MAINTENANT", "AVANT 18H".

REAL MTN MoMo TRANSACTION SHAPE (anonymised):
  "Vous avez recu 10.000 FCFA de [NOM] (677123456). Solde: 12.500 FCFA. ID: PP123ABC. *126# pour confirmer."

REAL ORANGE MONEY SHAPE:
  "Transfert de 5.000 FCFA recu de 690000000. Frais: 0 FCFA. Solde: 8.500 FCFA. Tapez *144# pour gerer."

REAL BANK EMAIL SHAPE (Afriland, BICEC, SGC, UBA, Ecobank):
- Formal French with "Cher(e) client(e)" or "Madame, Monsieur".
- Always signs with a contact block: Direction, address, phone, website (the legitimate one).
- Never asks for password BY EMAIL. (Phish emails will ask anyway — that is the trick.)

REAL SCAM PATTERNS OBSERVED IN CAMEROON 2024-2026:
- "Notification d'arrivee conteneur PADC-CM-XXXXXX au Port Autonome de Douala" — shipping scam.
- "Confirmation paiement MoMo de XX.XXX FCFA" with a click-to-confirm link that leads nowhere.
- "Alerte transaction UBA" with phone number "677..." to call.
- "Bourse universitaire — confirmer votre dossier" from a fake Yaoundé I email.
- "Votre commande Jumia/Glovo est prete" — package delivery requiring "frais d'expedition".
- "Eneo coupure programmee" — power utility maintenance phishing.

URGENCY TRIGGERS COMMONLY USED:
- "avant 24 heures" / "avant minuit"
- "votre compte sera suspendu"
- "derniere chance"
- "valider maintenant"
- "MTN appelle a confirmer" (impersonating telecom outreach)

BRAND VOICE PER SCENARIO:
- mobile_money: short, transactional, FCFA amounts, USSD codes (*126#, *144#).
- banking: formal, complete sentences, signed by a fake "service client".
- university: bureaucratic, mentions document numbers, deadline of 48h.

PHONE NUMBER FORMAT (Cameroonian mobile):
- 6XX XXX XXX with MTN starting 67X/68X, Orange starting 69X/65X.

CURRENCY: Always FCFA (never Euros or USD). Realistic amounts: 1.000 to 250.000 FCFA range.
"""

_BRAND_RULES = """
STRICT BRAND-SCENARIO MAPPING — YOU MUST OBEY THIS:

If scenario == "mobile_money":
  - The impersonated brand MUST be ONE of: MTN Mobile Money, Orange Money.
  - You may NOT use any bank name (UBA, Afriland, BICEC, Ecobank, Société Générale, etc.).
  - Subject line and body must reference MoMo / Orange Money / USSD codes (*126# or *144#).
  - Phone number format: 6XX XXX XXX (MTN: 67X/68X, Orange: 69X/65X).

If scenario == "banking":
  - The impersonated brand MUST be ONE of: Afriland First Bank, BICEC, UBA Cameroun, Ecobank, Société Générale Cameroun.
  - You may NOT impersonate MTN, Orange, or any telecom.
  - Use formal French banking tone, signed by "Service Client".

If scenario == "university":
  - The impersonated brand MUST be ONE of: Université de Yaoundé I, Université de Douala, Université de Buea, Université Catholique d'Afrique Centrale.
  - You may NOT use telecom or bank brands.
  - Use bureaucratic academic tone (mention matricule, dossier, scolarité).

DOUBLE-CHECK BEFORE RESPONDING:
- Does my subject line use a brand from the correct list for this scenario?
- Does the body use the SAME brand throughout? (No mixing MTN and UBA in one email.)
- Does the signature match the brand I chose?
"""

_DIFFICULTY_RULES = {
    "easy": (
        "OBVIOUS TYPOS in brand name (MNT instead of MTN). Generic greeting. "
        "Suspicious URL like xn-mtn-mobile.tk. Bad grammar. Should fool "
        "only the most distracted reader."
    ),
    "medium": (
        "Correct brand name. Plausible urgency. URL on a clearly third-party "
        "domain (e.g. mtn-verify-secure.com). Reasonable grammar with one "
        "small slip. Should fool a typical reader who is not paying attention."
    ),
    "hard": (
        "Perfect spelling and grammar. Plausible sender email or short code. "
        "URL uses a homograph or close lookalike (mtn-cameroon.com vs mtn.cm). "
        "Personalised tone. Should fool an average professional."
    ),
}


def _difficulty_block(difficulty: str) -> str:
    rule = _DIFFICULTY_RULES.get(difficulty, _DIFFICULTY_RULES["medium"])
    return f"DIFFICULTY = {difficulty}\nRULES FOR THIS DIFFICULTY:\n{rule}"


def _language_block(language: str) -> str:
    if language == "fr":
        return "LANGUAGE: French (français du Cameroun). Respond ENTIRELY in French. No English."
    if language == "en":
        return "LANGUAGE: English (Cameroonian English). Respond ENTIRELY in English. No French."
    return "LANGUAGE: bilingual — French primary, with one or two English code-switches as Cameroonians do."


def _enforce_tracking_link(text: str) -> str:
    """Replace any http(s) link Claude invented with the placeholder, just in case."""
    return re.sub(r"https?://\S+", "{{TRACKING_LINK}}", text)


def generate_phish_email(brief: str, language: str = "fr", difficulty: str = "medium") -> dict:
    """Return {'subject': ..., 'body_html': ...} for a simulated phishing EMAIL."""
    system = (
        "You generate REALISTIC simulated phishing emails for Hameçon, an ETHICAL "
        "consented security-awareness platform for Cameroon. NEVER include a real URL; "
        "use the literal placeholder {{TRACKING_LINK}} where a link should be. "
        "Output ONLY: first line 'Subject: <subject>', blank line, then HTML body.\n\n"
        + _CAMEROON_CONTEXT 
        +_BRAND_RULES
    )
    user = f"{_language_block(language)}\n{_difficulty_block(difficulty)}\nBRIEF: {brief}\n\nGenerate now."
    msg = _client.messages.create(
        model=_MODEL, max_tokens=900, system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = _enforce_tracking_link(msg.content[0].text.strip())
    lines = text.split("\n", 2)
    subject = lines[0].replace("Subject:", "").strip()
    body = lines[2].strip() if len(lines) > 2 else ""
    return {"subject": subject, "body_html": body}

def generate_phish_sms(brief: str, language: str = "fr", difficulty: str = "medium") -> str:
    """Return a single SMS-length string for a simulated phishing SMS (under 160 chars)."""
    system = (
        "You generate REALISTIC simulated phishing SMS messages for Hameçon. Format: "
        "a single SMS under 160 characters. No greeting. Use {{TRACKING_LINK}} where a link "
        "should be. Output ONLY the SMS text, nothing else.\n\n" + _CAMEROON_CONTEXT
        + _BRAND_RULES
    )
    user = f"{_language_block(language)}\n{_difficulty_block(difficulty)}\nBRIEF: {brief}\n\nGenerate now."
    msg = _client.messages.create(
        model=_MODEL, max_tokens=200, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _enforce_tracking_link(msg.content[0].text.strip())


def generate_lesson(message_subject: str, message_body: str, channel: str = "email", language: str = "fr") -> str:
    """
    Beginner-friendly teachable moment.
    Returns a JSON string: {brand, red_flags:[{title,detail}×3], tip}
    Falls back to plain text if JSON parsing fails on the caller side.
    """
    lang_label = "French (Cameroon)" if language == "fr" else "English (Cameroon)"
    system = (
        "You are a warm Cameroonian security trainer. The reader just clicked a simulated "
        "phishing message as part of a consented training programme. They may have NEVER "
        "heard of phishing. Be warm, never shame.\n\n"
        "Output ONLY a valid JSON object — no markdown fences, no extra text — with EXACTLY "
        "these keys:\n"
        '{\n'
        '  "brand": "<name of the brand impersonated in the message>",\n'
        '  "red_flags": [\n'
        '    {"title": "<max 5 words>", "detail": "<1–2 sentences specific to this message>"},\n'
        '    {"title": "<max 5 words>", "detail": "<1–2 sentences specific to this message>"},\n'
        '    {"title": "<max 5 words>", "detail": "<1–2 sentences specific to this message>"}\n'
        '  ],\n'
        '  "tip": "<one concrete protective action, 1 sentence>"\n'
        '}\n\n'
        "Rules:\n"
        "- red_flags MUST have EXACTLY 3 items.\n"
        "- Each clue MUST reference something specific in the exact message provided.\n"
        "- tip must be a single actionable sentence (e.g. 'Composez *126# vous-même...').\n"
        "- Never instruct the reader to share their PIN.\n"
        f"- ALL text values must be in {lang_label}.\n"
    )
    user = (
        f"LANGUAGE: {lang_label}\n"
        f"CHANNEL: {channel}\n"
        f"SUBJECT (if email): {message_subject}\n"
        f"MESSAGE BODY:\n{message_body}\n\n"
        "Output the JSON object now."
    )
    msg = _client.messages.create(
        model=_MODEL, max_tokens=800, system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = msg.content[0].text.strip()
    # Strip accidental markdown fences if Claude adds them
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
    return raw


# Backwards-compat shim so existing scripts keep working
def generate_phish(brief: str, language: str = "fr", difficulty: str = "medium") -> dict:
    return generate_phish_email(brief, language, difficulty)
