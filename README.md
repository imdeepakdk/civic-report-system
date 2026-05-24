#  CivicFix — Crowdsourced Civic Issue Reporting System

A full-stack Flask web app for reporting and tracking civic issues (potholes, garbage, broken lights) with AI image classification using Claude API.

---

## Quick Start

### 1. Install Dependencies
```bash
cd civic_report
pip install -r requirements.txt
```

### 2. Set Anthropic API Key
```bash
# Linux/Mac
export ANTHROPIC_API_KEY="your_api_key_here"

# Windows
set ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run the App
```bash
python app.py
```

Visit: `http://localhost:5000`

---

##  Project Structure

```
civic_report/
├── app.py                  # Main Flask app
├── requirements.txt
├── data/
│   └── reports.json        # Auto-created, stores all reports
├── static/
│   ├── css/main.css
│   ├── js/main.js
│   └── uploads/            # Uploaded images
└── templates/
    ├── base.html
    ├── index.html          # Homepage with stats
    ├── report.html         # Submit new report
    ├── map.html            # Interactive map view
    ├── track.html          # Track a report
    ├── admin_login.html
    ├── admin_dashboard.html
    └── 404.html
```

---

##  Features

| Feature | Description |
|---|---|
|  Photo Upload | Upload image of civic issue |
|  AI Classification | Claude AI auto-detects category & severity |
|  Map View | Leaflet.js map showing all issues with filters |
|  Report Tracking | Unique ID to track status (Reported → Resolved) |
|  Admin Dashboard | Manage reports, update status, add comments |
|  Stats | Live counter of total/resolved/pending issues |
|  AI Tags | Smart tags generated from image analysis |

---

##  AI Detection Categories

- 🕳️ Pothole
- 🗑️ Garbage / Trash
- 💡 Broken Streetlight
- 🌊 Flooding / Waterlogging
- 🎨 Graffiti / Vandalism
- 🚶 Broken Sidewalk
- 🌳 Fallen Tree
- ⚠️ Other

---

##  Admin Access

URL: `http://localhost:5000/admin`  
Default Password: `admin123`  
Change in `app.py` → `ADMIN_PASSWORD`

---

##  Tech Stack

- **Backend**: Flask (Python)
- **AI**: Claude claude-sonnet-4-20250514 via Anthropic API
- **Maps**: Leaflet.js + OpenStreetMap
- **Storage**: JSON file (easily swap to SQLite/PostgreSQL)
- **Frontend**: Vanilla HTML/CSS/JS, Google Fonts

---

##  Customization

- **Change city default**: Edit map coordinates in `map.html` and `report.html`
- **Add departments**: Extend `CATEGORY_KEYWORDS` in `app.py`
- **Database**: Replace JSON with SQLite using Flask-SQLAlchemy
- **Auth**: Add Flask-Login for proper user accounts
- **Email alerts**: Add Flask-Mail for status update emails
