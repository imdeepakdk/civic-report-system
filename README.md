# Civic Report System

A Flask-based web application where users can report civic issues like potholes, garbage, broken roads, and water leakage by uploading images and location details.

The system uses AI image classification to automatically detect issue categories and provides complaint tracking with an admin dashboard.

---

## Features

- Upload civic issue photos
- AI-based issue detection
- Interactive issue map
- Complaint tracking system
- Admin dashboard
- Status updates
- Responsive dark-themed UI

---

## Tech Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- JavaScript

### AI & Tools
- OpenCV
- Leaflet.js
- JSON Storage

---

## How It Works

1. User uploads an image of a civic issue
2. AI detects the issue category
3. Complaint gets stored in the system
4. Admin reviews and updates complaint status
5. User can track complaint progress

---

## Project Structure

```bash
civic_report/
├── app.py
├── requirements.txt
├── data/
├── static/
├── templates/
└── README.md
```

---

## Future Improvements

- Mobile app support
- Better AI accuracy
- Email notifications
- Government API integration

---

## What I Learned

While building this project, I learned:
- Flask backend development
- File upload handling
- AI image classification basics
- Map integration
- Admin dashboard creation
- Full-stack project structure

---

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

---

## Author

Deepak Kumar  
BS in Data Science – IIT Madras
