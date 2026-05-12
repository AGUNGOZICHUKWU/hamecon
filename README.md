  GNU nano 8.4                          README.md *
# Hameçon

**AI-powered phishing-awareness training for under-served markets.**

Demonstrated and validated in the Cameroonian context. Built to be affordable, local>

---
## The problem

Phishing is the number-one intial-access attack vector in modern breaches. The globa>

Open-source alternatives like Gophish are free but ship generic American and Europea>

The result: the people most vulnerable to phishing are the ones with the fewest tool>

---

## The solution


Hameçon is a self-hosted phishing-awareness platform that:

- Generates fresh, AI-written phishing emailson demand using Anthropic Claude
- Speaks French and English fluently, with Cameroonian cultural context built in
- Delivers a personalised teachable moment the instant a user clicks
- Tracks per-user vulnerability and adapts difficulty over time
- Runs on a US$35 Raspberry pi for under US$20 per month of operating cost
- Operates on consent-first principles - no recipient is ever sent a simulated phish>

It is designed as the open-source phishing-awareness platform a small Cameroonian or>

---

## Architecture
                    Admin Dashboard
                    (Flask + Jinja2)
                          |
                          v
                 Anthropic Claude API
        (generates emails + teachable lessons)
                          |
                          v
                     Mailgun API
        (dispatches emails with tracking tokens)
                          |
                  user clicks the link
                          v
                  Fake landing page
        (records click + submit attempt; no creds stored)
                          |
                          v
              Teachable Moment Page
        (Claude personalises the lesson)
                          |
                          v
                  SQLite Database
        (users, consent, campaigns, events, audit_log)

---

## Five differentiators

1. **AI-generated content** - every campaign is freshly written, so no two recipients see identical text. Static template libraries go stale; AI keeps content fresh.
2. **Personalised teachable moment** - the lesson is generated for the user, in their language, based on exactly what tricked them.
3. **Adaptive difficulty** - Hameçon learns each user's blind spots and increases challenge over time.
4. **Security-first end-to-end** - UFW, Fail2Ban, key-only SSH, TLS, bcrypt, RBAC, audit log, written consent workflow.
5. **Open-source and affordable** - runs on a Raspberry Pi for under US$20 per month of total operating cost.

---

## Five non-negotiable security rules

These are applied from Day 1. Any future change must respect them:

1. No recipient is sent a simulated phish without a timestamped, written consent record in the database.
2. Submitted credentials are never stored. Only the fact that a submit happened (and the input length) is recorded.
3. The admin dashboards requires authentication. No public access. Bcrypt, RBAC, session timeout, login rate limiting.
4. All admin actions are written to an immutable audit log.
5. Fake landing pages live on a clearly identified subdomain under our control. We imitiate brands; we never register lookalike domains.

---

## In scope for v1.0 (20-day build)

- Bilingual (FR + EN) AI-generated phishing emails
- Three core phishing scenarios: mobile money, banking, university portal
- Consent-first recipient management 
- Click and submit tracking  (no credential storage)
- AI-personalised teachable moment
- Adaptive difficulty (basic implementation)
- Admin dashboard with metrics and audit log viewer
- Hardened production deployment (Nginx + TLS + UFW + Fail2Ban)


## Deferred to v2

- Multi-organisation tenancy
- Mobile (SMS / Whatsapp)  simulated phishing
- LMS and HR-system intergrations
- Advanced gamification and leaderboards
- a native mobile app

---

## Technology stack

- Hardware: Raspberry pi 3B+
- OS: Debian Trixie (64-bit) 
- Backend: Python 3.13 with flask
- Database: SQLite
- AI: Anthropic Claude
- Email: Mailgun (free tier)
- Web server: Gunicorn behind Nginx
- Authentication: bcrypt with Flask-login

---

## Current status

Day 1 of 20 - pivoted from a URL-detector concept (PhishGuard) to the AI-driven awareness platform (Hameçon).

---

## Author

Florencia AGUNGOZICHUKWU - Master's project in Cybersecurity Defence.

---

## License and ethics

Source code: MIT (to be finalised).

**Ethical use:** Hameçon is a training tool. Using it to send simulated phishing to recipients without their written, informed consent is unethical and may be illegal in your jurisdiction. The codebase enforces a hard consent gate. Do not bypass it.

