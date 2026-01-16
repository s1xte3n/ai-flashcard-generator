# 🧠 Vibe Coder Template

> A clean, modern GitHub template for building, reviewing, shipping, and scaling software **the right way**.

This is not just a starter repo. It is a **workflow-enforcing template** designed to teach and reinforce real-world GitHub, CI/CD, and engineering best practices.

## ✨ Philosophy
- Clarity over cleverness
- Small commits, steady progress
- Automation over discipline
- Readable > smart
- If deploying feels scary, fix the pipeline

## ⚙️ Tech Stack
- **Runtime:** Node.js
- **Frontend:** React (Vite)
- **Backend:** Node.js (API-ready)
- **Tooling:** ESLint, Prettier, Husky
- **CI:** GitHub Actions
- **Infra-ready:** AWS / Serverless / Terraform friendly
- **Repo Style:** Monorepo

## 🚀 One-Click Repository Setup (Required)

After creating a repository from this template, run:

```bash
chmod +x scripts/bootstrap-repo.sh
./scripts/bootstrap-repo.sh
```

### What the bootstrap script does

The script automatically and safely configures:

- Creates and pushes a `develop` branch
- Sets `develop` as the default branch
- Enables repository features (issues, projects)
- Enables security features (Dependabot, vulnerability alerts)
- Adds CI, license, and branding badges to the README
- Applies branch protection to `develop` and `main`
- Requires the `ci` status check before merges

**Important:**
The script commits and pushes README changes *before* branch protection is enabled.
After bootstrap completes, all changes must go through pull requests.

## 🔐 What This Template Enforces

Once bootstrapped, the repository enforces:
- No direct commits to `main` or `develop`
- Feature branches only
- Pull requests for all changes
- CI must pass before merge
- Linting and formatting enforced by CI
- Pre-commit checks via Husky
- Security-first defaults

This applies even to solo projects.

## 🔁 Required GitHub Workflow

### 1. Create a feature branch
```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

### 2. Commit small, meaningful changes
```bash
git add .
git commit -m "feat: add your feature"
git push -u origin feature/your-feature-name
```

### 3. Open a pull request → `develop`
- CI runs automatically
- Review your own changes
- Fix failures until green

### 4. Merge when green
- CI must pass
- Merge via GitHub UI
- No direct pushes to protected branches

### 5. Release to production
- Open a PR from `develop` → `main`
- This represents a release candidate
- Merging to `main` is a production event

## 🤖 Automation & CI

GitHub Actions is used to:
- Install dependencies
- Lint JavaScript / JSX
- Run tests
- Enforce consistent quality gates

All workflows live in:
```
.github/workflows/
```

### CI enforcement details

Both `develop` and `main` require the `ci` check to pass before merges.

If CI is missing or misconfigured, merges are blocked.

**"ci — Expected — Waiting for status" means:**
- The workflow name or trigger does not match the required check
- Or CI has never run on that branch yet

**This is intentional. CI must be real, not assumed.**

## 🔍 Security & Quality

Compatible with GitHub security tooling:
- Dependency Graph
- Dependabot alerts
- Dependabot version updates
- Secret scanning
- Code scanning (CodeQL-ready)

The bootstrap script enables vulnerability alerts and automated fixes where available.

## 📦 Releases & Versioning

Supported flows:
- Feature branches → `develop`
- Release PRs → `main`
- Tagged releases
- Hotfix branches (if needed)

**Branch intent:**
- `develop` → active development
- `main` → production-ready code

Releases should be intentional and documented.

## 🚀 Getting Started

### Install dependencies

```bash
npm install
```

### Run frontend
```bash
npm run dev
```

### Run backend

```bash
npm run dev:backend
```

### Run tests
```bash
npm test
```

Tests are expected for:
- Critical logic
- Bug fixes
- New features

## 📁 Repository Structure

```
vibe-coder-template/
├── .github/              # CI workflows, PR templates
├── .husky/               # Git hooks
├── apps/
│   ├── frontend/         # React app
│   └── backend/          # API / server
├── packages/             # Shared libraries
├── infra/                # Infrastructure definitions
├── docs/                 # Architecture, decisions, roadmap
├── scripts/              # Repo automation (bootstrap lives here)
├── .editorconfig
├── .env.example
├── eslint.config.mjs
├── .prettierrc
└── README.md
```

See `/docs/architecture.md` for deeper details.

## 🗺 Roadmap

- Core setup
- Features
- Tests
- CI/CD
- Production hardening

## 🧠 Rules of the Repo

- No secrets in code — ever
- Every change goes through a PR (except initial bootstrap)
- CI must pass before merge
- Automation is mandatory
- Quality is enforced, not hoped for
- If something hurts, automate it

## 💡 What You Practice With This Template

Using this template trains you in:
- Professional GitHub workflows
- Branching strategies
- Pull request discipline
- CI/CD troubleshooting
- Merge conflict resolution
- Release hygiene
- Security-aware development
- Production-ready repo structure

## 🏁 Final Note

This template is opinionated by design.

Follow it, and you won't just ship projects — you'll build engineering discipline that scales with you.

**Treat solo work like team work.**  
**Future you will thank you.**

Happy shipping 🚀

![CI](https://github.com/s1xte3n/ai-flashcard-generator/actions/workflows/ci.yml/badge.svg)

![Vibe Coder Banner](https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif)
