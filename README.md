# Hameçon

**AI-native, consent-driven phishing awareness training for African small and medium enterprises.**

Hameçon is a Master's research project turned deployable platform that delivers phishing simulation training to Cameroonian and West African SMEs at one-thirteenth the cost of commercial alternatives.

## Highlights

- All 8 applicable OWASP Top 10 (2021) categories pass
- AI content generation via Anthropic Claude Sonnet 4.5, 4.7 to 5.2 seconds mean latency
- 100 percent consent gate enforcement in automated tests
- Runs on a single Raspberry Pi 3B+
- Annual operating cost: 83,000 FCFA for a 50-person SME
- Bilingual: French and English
- Aligned with Cameroon's Law No. 2010/012 on Cybersecurity and Cybercriminality

## Architecture

Three-tier Flask application running end-to-end on a Raspberry Pi behind a Cloudflare Tunnel:

- **Presentation:** Jinja templates for operator console, landing pages, teachable moment
- **Application:** Flask + Gunicorn, campaign dispatcher, AI generator, tracking, authentication
- **Data:** SQLite with append-only audit log

## Consent-Driven Dispatch (Five Gates)

Consent check → AI generation → Operator review → Signed token → SMTP send

Break any gate and no message leaves the platform. Every action is recorded in the audit log.

## Tech Stack

- Python 3.11, Flask 3.0, SQLite, Jinja2, bcrypt
- Anthropic Claude Sonnet 4.5 for AI content
- Flask-Login, Flask-WTF, Flask-Limiter for security
- Nginx, Cloudflare Tunnel, Gmail SMTP, Systemd, Gunicorn

## Two Production Scenarios

- **Mobile money:** MTN Mobile Money and Orange Money impersonation
- **Banking:** Impersonation of the five main Cameroonian banks (Afriland First Bank, UBA Cameroun, BICEC, Ecobank, Société Générale Cameroun)

## Security Rules

Five non-negotiable rules applied from Day 1 and enforced at both the code and database level:

1. No recipient receives a simulated phish without a timestamped, written consent record
2. Submitted credentials are NEVER stored, only integer lengths are recorded
3. The admin console requires authentication with bcrypt, rate limiting, and role-based access control
4. All operator actions are written to an append-only audit log
5. Landing pages live on a clearly identified subdomain, no lookalike domain registration

## Research Context

Master's thesis defended at the College of Technology (COLTECH), University of Bamenda, Cameroon, in August 2026, with an Excellent mark.

## Product Page

Hameçon on Notion: https://peat-pudding-ffd.notion.site/Hame-on-3c67fb05145180649b78e5e680e32f13

## Author

Ngozichukwu Florencia Agu
laflam984@gmail.com
Cameroon

## Licence

Currently proprietary. Contact the author for research or partnership use.
