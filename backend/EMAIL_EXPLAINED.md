# Email Sending Explained

## Current Setup: Local Development Mode

When `EMAIL_BACKEND=local` (which is what you have now), **emails are NOT actually sent**. Instead:

1. **Console Logging**: The email content is printed to the backend logs
2. **File Saving**: The email is saved as an HTML file in `backend/email_logs/`

This is a **development-only** feature to:
- Test email templates without needing AWS credentials
- Avoid accidentally sending test emails to real addresses
- Speed up development (no network calls)

## Why You're Not Receiving Emails

You're not receiving emails because **no email is actually being sent**. The local backend is just simulating email sending for development purposes.

## How Real Email Sending Works

To actually send emails that reach inboxes, you need:

### 1. An Email Service Provider

**AWS SES (Simple Email Service)** - What we're using for production:
- Requires AWS account and credentials
- Needs domain verification
- Has sending limits (initially in "sandbox" mode)
- Requires SPF, DKIM, and DMARC records

**Other Options:**
- SendGrid
- Mailgun
- Postmark
- Gmail SMTP (for personal use, not production)

### 2. Domain Authentication

Email providers (Gmail, Outlook, etc.) verify emails using:

**SPF (Sender Policy Framework)**
- DNS record that lists which servers can send emails for your domain
- Example: `v=spf1 include:amazonses.com ~all`

**DKIM (DomainKeys Identified Mail)**
- Cryptographic signature that proves the email came from your domain
- Prevents email spoofing

**DMARC (Domain-based Message Authentication)**
- Policy that tells email providers what to do with unauthenticated emails
- Can reject, quarantine, or allow emails that fail SPF/DKIM

### 3. IP Reputation

Email providers track:
- **IP Address Reputation**: Is your server IP known for spam?
- **Domain Reputation**: Has your domain sent spam before?
- **Volume**: Sending too many emails too quickly = spam flag

## How Email Providers Prevent Spam

### Gmail's Spam Prevention:

1. **Authentication Checks**
   - Verifies SPF, DKIM, DMARC records
   - Rejects emails that fail authentication

2. **Content Filtering**
   - Analyzes email content for spam patterns
   - Checks for suspicious links, attachments
   - Uses machine learning to detect spam

3. **Reputation System**
   - Tracks sender reputation over time
   - New senders start with low reputation
   - Good senders gradually build reputation

4. **Rate Limiting**
   - Limits how many emails you can send per day/hour
   - Prevents spam floods

5. **Blacklists**
   - Maintains lists of known spam IPs/domains
   - Blocks emails from blacklisted sources

6. **User Feedback**
   - When users mark emails as spam, it affects sender reputation
   - Too many spam reports = blacklist

## Why You Can't Just Send Emails from Any Server

If anyone could send emails from any server:

1. **Spam would be everywhere** - No way to stop it
2. **Phishing attacks** - Easy to impersonate companies
3. **Email would be unusable** - Inboxes flooded with spam

That's why email providers require:
- **Authentication** (SPF/DKIM/DMARC)
- **Verification** (prove you own the domain)
- **Reputation** (build trust over time)

## AWS SES Sandbox Mode

When you first set up AWS SES, you're in **"sandbox" mode**:
- Can only send to verified email addresses
- Limited sending volume
- Must request production access to send to any address

This prevents abuse and spam.

## For Your Project

Configuration is driven by **`ENVIRONMENT`** and **`EMAIL_BACKEND`** (see `app/core/config.py`).

| Environment | Typical `EMAIL_BACKEND` | Behavior |
|-------------|-------------------------|----------|
| `local` (default) | `local` | Console + `backend/email_logs/` — signup flow unchanged |
| `staging` | `ses` (default if unset) | Real emails via AWS SES |
| `production` | `ses` (default if unset) | Real emails via AWS SES |

Example files:

- `backend/.env.example` — local Docker / dev
- `backend/.env.staging.example` — staging ECS secrets template
- `backend/.env.production.example` — production ECS secrets template

### Local Development (Current)
- `ENVIRONMENT=local` + `EMAIL_BACKEND=local` → Emails logged to console/files
- No actual sending
- Perfect for testing templates
- Signup UI can still mention verification; links appear in logs/files

### Staging / Production (When Ready)
- Set `ENVIRONMENT=staging` or `production`
- Set `EMAIL_BACKEND=ses` (auto-default when `ENVIRONMENT` is staging/prod and `EMAIL_BACKEND` is not set)
- Requires:
  1. AWS SES setup
  2. Domain verification
  3. SPF/DKIM/DMARC DNS records
  4. Production access request (move out of SES sandbox)
  5. IAM permission `ses:SendEmail` on the ECS task role
  6. `FRONTEND_URL` pointing at your real app URL (for links in emails)

No code changes are required to switch — only environment variables in your deployment.

## Viewing Local Emails

You can view the saved email files:

```bash
# List saved emails
ls backend/email_logs/

# Open in browser (macOS)
open backend/email_logs/email_*.html
```

The HTML files contain the full email content, so you can see exactly what users will receive.

## Summary

- **Local mode** = No actual sending, just logging (what you have now)
- **SES mode** = Real email sending (for production)
- **Email providers** use authentication, reputation, and filtering to prevent spam
- **You can't spam** because providers verify and rate-limit senders

