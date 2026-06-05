# Heroku deployment guide

Deploy Predico for a small friends-only production app (~$12/month):

| Service | Platform | Cost |
|---------|----------|------|
| API + Postgres | Heroku | ~$12/mo (Basic dyno + Essential-0) |
| Frontend | Vercel or Cloudflare Pages | $0 |
| Email | SendGrid (Heroku add-on) | $0 at low volume |

**Staging** stays local via `docker-compose.yml`. There is only one cloud environment.

---

## 1. Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) — install with `winget install Heroku.HerokuCLI`, then **open a new terminal**
- Heroku account with **billing verified** (credit card — required for Postgres, even on cheap plans)
- GitHub repo connected for deploy (recommended)

### First-time: what you do in Heroku (browser + one terminal command)

| Step | Where | Action |
|------|--------|--------|
| 1 | [dashboard.heroku.com/account/billing](https://dashboard.heroku.com/account/billing) | Add a payment method |
| 2 | Terminal | `heroku login` (opens browser to authorize CLI) |
| 3 | Terminal (repo root) | Run `.\scripts\setup-heroku.ps1` (or follow manual steps below) |
| 4 | Heroku app → **Resources** → SendGrid | Open SendGrid, **verify sender email** (required for sign-up emails) |
| 5 | After deploy | `git push heroku main` or connect GitHub in **Deploy** tab |

Optional app name if `predico-ab-api` is taken: `.\scripts\setup-heroku.ps1 -AppName your-unique-name`

---

## 2. Backend on Heroku

Predico is a monorepo; the API lives in `backend/`. Use the subdirectory buildpack so Heroku builds from that folder.

```bash
# From repo root
heroku login
heroku create predico-api --region eu

# Monorepo: build backend/ only
heroku buildpacks:clear -a predico-api
heroku buildpacks:add -a predico-api https://github.com/timanovsky/subdir-heroku-buildpack
heroku buildpacks:add -a predico-api heroku/python
heroku config:set PROJECT_PATH=backend -a predico-api

# Postgres (Essential-0, $5/mo)
heroku addons:create heroku-postgresql:essential-0 -a predico-api

# SendGrid for transactional email (free tier is enough for friends)
heroku addons:create sendgrid:starter -a predico-api

# Basic dyno ($7/mo, always on — use eco only if cold starts are OK)
heroku ps:type basic -a predico-api
```

### Required config vars

Generate a secret key (PowerShell):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set config (replace placeholders after frontend deploy in step 3):

```bash
heroku config:set -a predico-api \
  ENVIRONMENT=production \
  DEBUG=False \
  SECRET_KEY="your-generated-secret" \
  EMAIL_ENABLED=True \
  EMAIL_BACKEND=sendgrid \
  SES_FROM_EMAIL="noreply@yourdomain.com" \
  FRONTEND_URL="https://your-app.vercel.app" \
  CORS_ORIGINS="https://your-app.vercel.app" \
  DB_POOL_SIZE=5 \
  DB_MAX_OVERFLOW=5
```

Notes:

- `DATABASE_URL` is set automatically by Heroku Postgres.
- `SENDGRID_API_KEY` is set automatically by the SendGrid add-on.
- `SES_FROM_EMAIL` is the **From** address — verify it in the [SendGrid sender authentication](https://app.sendgrid.com/settings/sender_auth) dashboard.
- Heroku Postgres Essential-0 allows **20 connections**; keep `DB_POOL_SIZE` at 5.

See `backend/.env.heroku.example` for the full list.

### Deploy the API

```bash
# First time: add Heroku git remote (from repo root)
heroku git:remote -a predico-api

# Deploy (migrations run via Procfile release phase)
git push heroku main
```

If your default branch is not `main`, push that branch instead:

```bash
git push heroku your-branch:main
```

### Verify

```bash
heroku logs --tail -a predico-api
curl https://predico-api.herokuapp.com/health
heroku run alembic current -a predico-api
```

### Populate World Cup data (optional)

```bash
heroku run python scripts/populate_world_cup_data.py -a predico-api
```

---

## 3. Frontend on Vercel (recommended)

The frontend is a static Vite build. Do **not** run it on a second Heroku dyno — host it for free on Vercel.

1. Import the GitHub repo in [Vercel](https://vercel.com/new).
2. Set **Root Directory** to `frontend`.
3. Build settings (auto-detected): `npm run build`, output `dist`.
4. Environment variable:

   | Name | Value |
   |------|-------|
   | `VITE_API_BASE_URL` | `https://predico-api.herokuapp.com` |

5. Deploy.

`frontend/vercel.json` already configures SPA routing (all paths → `index.html`).

After deploy, update Heroku:

```bash
heroku config:set -a predico-api \
  FRONTEND_URL="https://your-app.vercel.app" \
  CORS_ORIGINS="https://your-app.vercel.app"
```

### Alternative: Cloudflare Pages

1. Connect repo → **Root directory**: `frontend`.
2. Build: `npm run build`, output: `dist`.
3. Set `VITE_API_BASE_URL` in Pages environment variables.
4. Add a `_redirects` file in `frontend/public/` with `/* /index.html 200` if you use client-side routing.

---

## 4. Email backend choice

| Backend | When to use | Config |
|---------|-------------|--------|
| **`local`** | Docker / local dev | Default in `.env` — logs to console + `backend/email_logs/` |
| **`sendgrid`** | **Heroku (recommended)** | `EMAIL_BACKEND=sendgrid` + SendGrid add-on |
| **`ses`** | AWS ECS/EC2 deployments | `EMAIL_BACKEND=ses` + IAM/credentials + verified SES domain |

On Heroku, use **SendGrid**:

```bash
heroku addons:create sendgrid:starter -a predico-api
heroku config:set EMAIL_BACKEND=sendgrid SES_FROM_EMAIL=noreply@yourdomain.com -a predico-api
```

Verify your sender in SendGrid before testing sign-up / password reset flows.

---

## 5. Environment variables reference

### Heroku (backend)

| Variable | Required | Source |
|----------|----------|--------|
| `DATABASE_URL` | Yes | Auto (Postgres add-on) |
| `SECRET_KEY` | Yes | You generate |
| `ENVIRONMENT` | Yes | `production` |
| `DEBUG` | Yes | `False` |
| `FRONTEND_URL` | Yes | Vercel/Pages URL |
| `CORS_ORIGINS` | Yes | Same as frontend URL |
| `EMAIL_BACKEND` | Yes | `sendgrid` |
| `SES_FROM_EMAIL` | Yes | Verified SendGrid sender |
| `SENDGRID_API_KEY` | Yes | Auto (SendGrid add-on) |
| `DB_POOL_SIZE` | Recommended | `5` |
| `DB_MAX_OVERFLOW` | Recommended | `5` |

### Vercel (frontend)

| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_BASE_URL` | Yes | `https://predico-api.herokuapp.com` |

### Local (unchanged)

Copy `backend/.env.example` → `backend/.env` and use `docker-compose.yml`.

---

## 6. Branch strategy

| Where | Environment |
|-------|-------------|
| Local + `docker-compose` | Development |
| `main` → `git push heroku main` | Production (Heroku) |
| Vercel connected to `main` | Production frontend |

See `BRANCH_STRATEGY.md` for the updated workflow.

---

## 7. AWS infrastructure (archived)

The `infrastructure/` folder contains an earlier **AWS ECS + RDS + Terraform** design aimed at higher scale and cost (~$130+/month per environment). It is **not used** for the current Heroku deployment.

- **Ignore for now**: `infrastructure/terraform/`, AWS setup guides in `infrastructure/archive/`
- **Active deploy docs**: this file (`docs/HEROKU.md`)
- **CI note**: `.github/workflows/ci-cd.yml` still contains AWS deploy jobs — they no-op until AWS secrets exist; tests still run on PRs

If you outgrow Heroku later, revisit the archived Terraform or simplify to a single AWS Lightsail box.

---

## 8. Troubleshooting

| Issue | Fix |
|-------|-----|
| `Application error` on boot | `heroku logs --tail` — usually missing `SECRET_KEY` or bad `DATABASE_URL` |
| CORS errors in browser | `CORS_ORIGINS` must exactly match frontend origin (no trailing slash) |
| Emails not arriving | Verify sender in SendGrid; check `heroku logs` for SendGrid errors |
| `too many connections` | Lower `DB_POOL_SIZE`; Essential-0 max is 20 |
| Migrations failed | `heroku run alembic upgrade head -a predico-api` |
| Cold starts | Switch from Eco to Basic dyno (`heroku ps:type basic`) |

---

## Cost checklist

```
Heroku Basic dyno          $7/mo
Heroku Postgres Essential-0 $5/mo
SendGrid starter            $0
Vercel hobby                $0
─────────────────────────────────
Total                      ~$12/mo
```
