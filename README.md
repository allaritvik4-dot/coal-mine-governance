# Coal Mine Smart Governance & Compliance Monitoring System

> **SIH26024** — AI-Based Smart Governance and Compliance Monitoring System for Coal Mines

A desktop application that leverages AI and a knowledge-base–driven approach to streamline governance, safety inspections, hazard tracking, and regulatory compliance across coal mining operations in India.

---

## Features

- **Dashboard Analytics** — Real-time overview of mine safety metrics, compliance status, and operational KPIs with interactive charts.
- **Trained Machine Learning Model (SIH Core)** — Scikit-Learn TF-IDF + Logistic Regression & Gradient Boosting model for automatic hazard categorization (9 hazard types) and statutory severity ranking (Critical, High, Medium, Low) with automated DGMS safety advisory generation.
- **Statutory Regulatory RAG Assistant** — Ingests Coal Mines Regulations (CMR 2017) and DGMS Technical Circulars into a hybrid retrieval store (ChromaDB vector embeddings + BM25 lexical ranking), returning source-grounded answers with regulatory citations.
- **Intelligent Conversational Engine** — Handles natural human greetings, small talk, identity, and system help warmly, while enforcing domain-boundary guardrails to reject off-topic inquiries outside colliery operations and compliance.
- **Floating AI Assistant (All Pages)** — Prominent circular floating AI widget docked in the bottom-right corner of every page, offering instant chat access anywhere in the platform.
- **Inspection Management** — Schedule, track, and complete safety inspections with findings, statutory violations, and risk assessments.
- **Hazard Tracking** — Report, classify, and monitor hazards by severity with full lifecycle tracking (reported → mitigated → closed).
- **Incident Reporting** — Log incidents with casualty/injury counts, root-cause analysis, and resolution workflows.
- **Equipment & Maintenance** — Track equipment status, schedule preventive maintenance, and log FLP (flameproof) electrical tolerances.
- **Training Records (VTR)** — Monitor worker certifications, refresher courses under Vocational Training Rules (VTR 1966), and statutory expirations.
- **Compliance Engine** — Automated statutory compliance scanning with configurable threshold rules, alert generation, and corrective actions.
- **Role-Based Access Control** — Six roles (Admin, Mine Manager, Safety Officer, DGMS Inspector, Overman/Supervisor, Viewer) with secure bcrypt hashing and JWT authentication.
- **Audit Logging** — Every create/update/delete action is immutably logged with timestamp, user ID, entity type, and before/after values.

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop Shell | Electron 35 |
| Frontend | React 18 + TypeScript, Vite, Industrial Dark/Light CSS |
| Backend | Flask 3.1, Flask-JWT-Extended, Flask-CORS |
| Database | SQLite 3 (14 normalized relational tables) |
| Machine Learning | Scikit-learn, NumPy, TF-IDF Vectorizer, GradientBoosting |
| Vector Store | ChromaDB + Sentence Transformers (`all-MiniLM-L6-v2`) |
| Search | Hybrid Dense Vector + BM25 with Reciprocal Rank Fusion (RRF) |
| Icons | Lucide React |

## Prerequisites

- **Python** 3.10 to 3.13
- **Node.js** 18 or later (with npm)
- **Git**

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/allaritvik4-dot/coal-mine-governance.git
cd coal-mine-governance

# 2. Install backend Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# 3. Install frontend dependencies and build SPA
cd frontend
npm install
npm run build
cd ..

# 4. Optional: Install root Electron dependencies
npm install
```

## Running the Application

### Option A: 1-Click Launch (Recommended)
Double-click `launch_app.bat` or run the desktop shortcut in your Downloads folder:
- **Coal Mine Governance App.bat** (starts backend and launches browser to `http://127.0.0.1:5000`)

### Option B: Manual Startup
```bash
# Start Flask backend (serves both API and built React SPA):
cd backend
python app.py
```
Then visit **`http://127.0.0.1:5000`** in your web browser.

### Option C: Desktop Shell (Electron)
```bash
npm start
```

### Seeded Demo Accounts (Password for all: `demo123`)

| Username | Role | Description |
|---|---|---|
| `admin` | Administrator | Full platform control & user management |
| `mgr_jharia` | Mine Manager | Jharia Underground Colliery Operations |
| `mgr_singrauli` | Mine Manager | Singrauli Opencast Project Operations |
| `safety_jharia` | Safety Officer | Underground Safety, Gas Surveys & VTR |
| `safety_korba` | Safety Officer | Korba West Colliery Safety & Equipment |
| `insp_dgms` | DGMS Inspector | Statutory Inspection Audits & CMR Compliance |

## Building for Production

```bash
# Build the frontend
npm run build:frontend

# Package the Electron app
npm run package
```

The packaged installer will be output to the `dist/` directory.

## Project Structure

```
coal-mine-governance/
├── electron/
│   ├── main.js              # Electron main process
│   └── preload.js           # Context bridge (IPC)
├── backend/
│   ├── app.py               # Flask application entry point
│   ├── config.py            # Configuration
│   ├── database/
│   │   ├── db.py            # Database helpers
│   │   ├── schema.sql       # Table definitions
│   │   └── seed_data.sql    # Sample data
│   ├── routes/              # API route blueprints
│   ├── services/            # Business logic
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page-level views
│   │   ├── services/        # API client
│   │   ├── context/         # React context (auth)
│   │   └── types/           # TypeScript interfaces
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── package.json              # Root config (Electron + scripts)
├── .gitignore
└── README.md
```

## Database Schema

The SQLite database includes 15 tables:

| Table | Purpose |
|---|---|
| `users` | User accounts with role-based access |
| `mines` | Registered coal mines |
| `sections` | Mine sections/areas |
| `inspections` | Safety inspection records |
| `hazards` | Reported hazards with severity |
| `incidents` | Incident reports |
| `equipment` | Equipment inventory |
| `maintenance_activities` | Maintenance logs |
| `training_records` | Worker training & certifications |
| `compliance_rules` | Configurable compliance rules |
| `compliance_alerts` | Auto-generated compliance alerts |
| `corrective_actions` | Remedial action tracking |
| `audit_log` | Full audit trail |
| `knowledge_documents` | Uploaded regulatory documents |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate user |
| `GET` | `/api/auth/me` | Get current user profile |
| `GET/POST` | `/api/mines` | List / create mines |
| `GET/POST` | `/api/inspections` | List / create inspections |
| `GET/POST` | `/api/hazards` | List / create hazards |
| `GET/POST` | `/api/incidents` | List / create incidents |
| `GET/POST` | `/api/equipment` | List / create equipment |
| `GET/POST` | `/api/maintenance` | List / create maintenance records |
| `GET/POST` | `/api/training` | List / create training records |
| `GET/POST` | `/api/compliance/rules` | List / create compliance rules |
| `GET/POST` | `/api/compliance/alerts` | List / manage alerts |
| `GET/POST` | `/api/compliance/actions` | List / manage corrective actions |
| `POST` | `/api/knowledge/upload` | Upload document to knowledge base |
| `POST` | `/api/knowledge/query` | Query the knowledge base (RAG) |
| `GET` | `/api/dashboard/stats` | Dashboard statistics |
| `GET` | `/api/dashboard/charts/*` | Chart data endpoints |
| `GET` | `/api/audit-log` | Audit trail |

## License

MIT License — see [LICENSE](LICENSE) for details.

---

> [!WARNING]
> **Disclaimer:** This application is a **decision-support prototype** developed for academic and demonstration purposes (Smart India Hackathon 2026). It **does not replace** statutory inspections, competent safety judgement, or official regulatory decisions mandated by the Directorate General of Mines Safety (DGMS) or any other regulatory authority. Always defer to qualified professionals and applicable law for mine safety and governance.
