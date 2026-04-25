# Setup Instructions — Push This Tracker to GitHub

## Step 1 — Initialize git in this folder

```bash
cd /Volumes/SSD-Yogesh/Study-Material-Mac/Yogesh-Projects/ai-engineer/tracker
git init
git add .
git commit -m "Day 0: Tracker scaffolding"
```

## Step 2 — Create GitHub repo

Option A — Web UI:
1. Go to github.com/new
2. Repo name: `ai-engineer-journey`
3. Public ✅
4. Don't initialize w/ README (we have one)
5. Create

Option B — CLI (if `gh` installed):
```bash
gh repo create ai-engineer-journey --public --source=. --remote=origin --push
```

## Step 3 — Push (if used Option A)

```bash
git remote add origin git@github.com:YOUR_USERNAME/ai-engineer-journey.git
git branch -M main
git push -u origin main
```

## Step 4 — Pin the repo on your GitHub profile

GitHub profile → "Customize your pins" → pin `ai-engineer-journey` to top.

## Step 5 — Daily workflow

Each working day:

```bash
cd /path/to/ai-engineer-journey

# Copy template for today's day number
cp templates/daily-log-template.md days/day-NNN.md

# Edit it as you go through the day
cursor days/day-NNN.md

# At end of day, commit
git add days/day-NNN.md
git commit -m "Day NNN: [one-line summary]"
git push
```

## Step 6 — Weekly workflow (Sunday)

```bash
# Create weekly review
cp templates/weekly-review-template.md weekly-reviews/week-NN.md
cursor weekly-reviews/week-NN.md

# Update PROGRESS.md
cursor PROGRESS.md

# Update metrics CSVs
cursor metrics/linkedin.csv
cursor metrics/github.csv
# etc.

git add .
git commit -m "Week NN: review + metrics update"
git push
```

## Step 7 — Project ship workflow

When you ship a project:

1. Create separate repo for the project (e.g., `sec-10k-analyzer`)
2. Update `tracker/projects/README.md` w/ links
3. Update `tracker/PROGRESS.md`
4. Tag the milestone in tracker repo:

```bash
git tag day-37-project-1-shipped
git push --tags
```

## Optional — GitHub Pages

Turn this repo into a website:

1. Settings → Pages → Source: main branch
2. Visit `YOUR_USERNAME.github.io/ai-engineer-journey`
3. Free public progress dashboard

## Optional — Auto-commit script

Create `commit-day.sh`:

```bash
#!/bin/bash
DAY=$1
SUMMARY="$2"
git add days/day-$(printf "%03d" $DAY).md
git commit -m "Day $DAY: $SUMMARY"
git push
```

Usage: `./commit-day.sh 1 "Setup complete, first LLM call"`

## Privacy notes

- Tracker is public — show progress to recruiters/community
- Daily logs are public-safe (no secrets, no salary specifics, no PII)
- For private notes (interview offers, salary numbers): use Notion separately
- `.gitignore` excludes `.env`, secrets, `.private.md` files

## Recommended companion: Notion daily journal

Tracker = public + structured. Notion = private + free-form.

Notion entries can be longer, contain screenshots, salary discussions, etc. Tracker entries should be shareable.
