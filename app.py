from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
import uuid
import base64

from datetime import datetime

app = Flask(__name__)
app.secret_key = "civic_secret_key_2024"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DATA_FILE = 'data/reports.json'
ADMIN_PASSWORD = "admin123"

os.makedirs('data', exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CATEGORY_KEYWORDS = {
    'pothole': ['pothole', 'hole', 'crater', 'road damage', 'broken road', 'asphalt'],
    'garbage': ['garbage', 'trash', 'waste', 'litter', 'dump', 'rubbish', 'debris'],
    'streetlight': ['light', 'streetlight', 'lamp', 'dark', 'lighting', 'bulb'],
    'flooding': ['flood', 'water', 'drain', 'waterlogging', 'puddle', 'sewage'],
    'graffiti': ['graffiti', 'vandalism', 'spray paint', 'defaced', 'writing'],
    'broken_sidewalk': ['sidewalk', 'footpath', 'pavement', 'walkway', 'broken'],
    'tree_fallen': ['tree', 'fallen', 'branch', 'obstruction', 'blocked'],
    'other': []
}

CATEGORY_ICONS = {
    'pothole': '🕳️',
    'garbage': '🗑️',
    'streetlight': '💡',
    'flooding': '🌊',
    'graffiti': '🎨',
    'broken_sidewalk': '🚶',
    'tree_fallen': '🌳',
    'other': '⚠️'
}

CATEGORY_COLORS = {
    'pothole': '#ef4444',
    'garbage': '#f97316',
    'streetlight': '#eab308',
    'flooding': '#3b82f6',
    'graffiti': '#a855f7',
    'broken_sidewalk': '#6b7280',
    'tree_fallen': '#22c55e',
    'other': '#64748b'
}

STATUS_FLOW = ['reported', 'under_review', 'in_progress', 'resolved']


def load_reports():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_reports(reports):
    with open(DATA_FILE, 'w') as f:
        json.dump(reports, f, indent=2)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_image_with_claude(image_path, description=""):
    """Use Claude API to analyze image and detect category"""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        ext = image_path.rsplit('.', 1)[1].lower()
        media_type_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}
        media_type = media_type_map.get(ext, 'image/jpeg')

        prompt = f"""Analyze this civic issue image and respond with JSON only.
User description: "{description}"

Classify into one category: pothole, garbage, streetlight, flooding, graffiti, broken_sidewalk, tree_fallen, other

Respond ONLY with valid JSON, no markdown:
{{
  "category": "category_name",
  "confidence": 0.0-1.0,
  "tags": ["tag1", "tag2", "tag3"],
  "severity": "low|medium|high",
  "ai_description": "Brief description of the issue seen"
}}"""

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            text = data['content'][0]['text'].strip()
            # Strip markdown if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            return json.loads(text)
    except Exception as e:
        print(f"AI analysis error: {e}")

    # Fallback: keyword-based detection
    return fallback_categorize(description)


def fallback_categorize(description):
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return {
                "category": category,
                "confidence": 0.7,
                "tags": [category, "civic issue"],
                "severity": "medium",
                "ai_description": f"Detected as {category} based on description keywords."
            }
    return {
        "category": "other",
        "confidence": 0.5,
        "tags": ["civic issue", "unclassified"],
        "severity": "medium",
        "ai_description": "Could not auto-classify. Marked for manual review."
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    reports = load_reports()
    stats = {
        'total': len(reports),
        'resolved': sum(1 for r in reports if r['status'] == 'resolved'),
        'pending': sum(1 for r in reports if r['status'] == 'reported'),
        'in_progress': sum(1 for r in reports if r['status'] == 'in_progress'),
    }
    category_counts = {}
    for r in reports:
        cat = r.get('category', 'other')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return render_template('index.html', reports=reports[:10], stats=stats,
                           category_counts=category_counts,
                           category_icons=CATEGORY_ICONS,
                           category_colors=CATEGORY_COLORS)


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'GET':
        return render_template('report.html', category_icons=CATEGORY_ICONS)

    # Handle POST
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    location_name = request.form.get('location_name', '').strip()
    lat = request.form.get('lat', '')
    lng = request.form.get('lng', '')
    reporter_name = request.form.get('reporter_name', 'Anonymous').strip()
    reporter_email = request.form.get('reporter_email', '').strip()

    if not title or not location_name:
        return jsonify({'error': 'Title and location are required'}), 400

    image_filename = None
    ai_result = None

    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_filename = filename
            ai_result = analyze_image_with_claude(filepath, description)

    if not ai_result:
        ai_result = fallback_categorize(description)

    report_id = str(uuid.uuid4())[:8].upper()
    report_data = {
        'id': report_id,
        'title': title,
        'description': description,
        'location_name': location_name,
        'lat': float(lat) if lat else None,
        'lng': float(lng) if lng else None,
        'reporter_name': reporter_name,
        'reporter_email': reporter_email,
        'image': image_filename,
        'category': ai_result['category'],
        'ai_confidence': ai_result['confidence'],
        'ai_tags': ai_result['tags'],
        'severity': ai_result['severity'],
        'ai_description': ai_result['ai_description'],
        'status': 'reported',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'comments': []
    }

    reports = load_reports()
    reports.insert(0, report_data)
    save_reports(reports)

    return jsonify({'success': True, 'report_id': report_id, 'category': ai_result['category'],
                    'ai_result': ai_result})


@app.route('/map')
def map_view():
    reports = load_reports()
    geo_reports = [r for r in reports if r.get('lat') and r.get('lng')]
    return render_template('map.html', reports=geo_reports,
                           category_colors=CATEGORY_COLORS,
                           category_icons=CATEGORY_ICONS)


@app.route('/track/<report_id>')
def track(report_id):
    reports = load_reports()
    report = next((r for r in reports if r['id'] == report_id), None)
    if not report:
        return render_template('404.html'), 404
    return render_template('track.html', report=report,
                           category_icons=CATEGORY_ICONS,
                           category_colors=CATEGORY_COLORS,
                           status_flow=STATUS_FLOW)


@app.route('/api/reports')
def api_reports():
    reports = load_reports()
    category = request.args.get('category')
    status = request.args.get('status')
    if category:
        reports = [r for r in reports if r.get('category') == category]
    if status:
        reports = [r for r in reports if r.get('status') == status]
    return jsonify(reports)


@app.route('/api/report/<report_id>')
def api_report(report_id):
    reports = load_reports()
    report = next((r for r in reports if r['id'] == report_id), None)
    if not report:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(report)


# ─── Admin Routes ──────────────────────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Wrong password")
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    reports = load_reports()
    stats = {
        'total': len(reports),
        'reported': sum(1 for r in reports if r['status'] == 'reported'),
        'under_review': sum(1 for r in reports if r['status'] == 'under_review'),
        'in_progress': sum(1 for r in reports if r['status'] == 'in_progress'),
        'resolved': sum(1 for r in reports if r['status'] == 'resolved'),
    }
    by_category = {}
    for r in reports:
        cat = r.get('category', 'other')
        by_category[cat] = by_category.get(cat, 0) + 1

    return render_template('admin_dashboard.html', reports=reports, stats=stats,
                           by_category=by_category,
                           category_icons=CATEGORY_ICONS,
                           category_colors=CATEGORY_COLORS,
                           status_flow=STATUS_FLOW)


@app.route('/admin/update/<report_id>', methods=['POST'])
def admin_update(report_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401

    reports = load_reports()
    for r in reports:
        if r['id'] == report_id:
            new_status = request.form.get('status')
            comment = request.form.get('comment', '').strip()
            if new_status in STATUS_FLOW:
                r['status'] = new_status
                r['updated_at'] = datetime.now().isoformat()
            if comment:
                r.setdefault('comments', []).append({
                    'text': comment,
                    'by': 'Admin',
                    'at': datetime.now().isoformat()
                })
            break
    save_reports(reports)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
