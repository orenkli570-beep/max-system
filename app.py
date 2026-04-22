import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- מנוע ניתוח (פרוטוקול אורן) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def deep_analysis(data):
    num = get_num(data['dob'])
    # בדיקת איכות תשובות לפי מילות מפתח
    pos_keywords = ["מאוד", "תמיד", "מצוין", "מלאה", "פורח", "Very", "Always", "Excellent"]
    high_quality_count = sum(1 for a in data['answers'] if any(word in a['a'] for word in pos_keywords))
    
    traits = {
        1: "מנהיגות וביצוע עצמאי", 2: "שירות, הכלה ועבודת צוות", 
        3: "תקשורת בין-אישית ויצירתיות", 4: "סדר, דיוק וארגון מופתי", 
        5: "זריזות, דינמיות והסתגלות", 6: "אחריות וטיפול בלקוחות", 
        7: "ריכוז, עומק ויסודיות", 8: "חוסן מנטלי וניהול לחצים", 
        9: "ראייה רחבה ורצון לעזור", 11: "אינטואיציה והבנת אנשים", 
        22: "יכולת ביצוע פרויקטים מורכבים"
    }
    
    analysis = f"ניתוח עבור {data['firstName']} (תדר {num}):\n"
    analysis += f"על פי התדר האישי, המועמד ניחן ב{traits.get(num, 'יכולות ורסטיליות')}. "
    
    if high_quality_count >= 7:
        analysis += "התשובות מעידות על מוטיבציה גבוהה וחיבור למותג MAX. "
    else:
        analysis += "המועמד מחפש יציבות אך זקוק להנחיה ברורה בתחילת הדרך. "

    # התאמה למחלקות
    if num in [1, 5, 8, 22]:
        analysis += "\nמתאים למחלקות דינמיות ופיזיות (פלסטיקה, עונה). "
    else:
        analysis += "\nמתאים למחלקות אסתטיות ומסודרות (דקורציה, ביוטי, כלי כתיבה). "
        
    return analysis

HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX System - Oren Protocol</title>
    <style>
        :root { --red: #e31e24; --dark: #1e293b; --bg: #f1f5f9; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); margin: 0; direction: rtl; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 4px solid var(--red); box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .container { max-width: 1000px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; }
        .hidden { display: none; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .btn-update { background: #10b981; color: white; border: none; font-weight: bold; cursor: pointer; }
        .analysis-text { background: #fff3f3; padding: 15px; border-radius: 8px; border-right: 5px solid var(--red); line-height: 1.6; font-weight: bold; white-space: pre-wrap; }
        .inter-box { color: #2563eb; font-weight: bold; text-align: center; margin: 10px 0; font-size: 22px; border: 1px dashed #2563eb; padding: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }
        th { background: #f1f5f9; }
        .lang-bar { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; }
        .lang-btn { padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>MAX – ניהול וגיוס</h1></div>
    <div class="container">
        <div id="login-section">
            <input type="text" id="username" placeholder="שם משתמש">
            <input type="password" id="password" placeholder="סיסמה">
            <button class="btn-main" onclick="login()">כניסה</button>
        </div>

        <div id="sec-section" class="hidden">
            <div class="lang-bar">
                <button class="lang-btn" onclick="changeL('he')">Hebrew</button>
                <button class="lang-btn" onclick="changeL('en')">English</button>
            </div>
            <div id="q-container"></div>
            <input type="text" id="firstName" placeholder="שם פרטי">
            <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניתוח ושיבוץ</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                <div style="display:flex; gap:10px;">
                    <select id="editDept"><option>פלסטיקה</option><option>חד פעמי</option><option>דקורציה</option><option>ביוטי</option><option>עונה</option></select>
                    <select id="editJob"><option>סדרן</option><option>קופאית</option><option>אחראי מחלקה</option><option>מנהל</option></select>
                </div>
                <button class="btn-update" onclick="updateAssignment()">עדכן שיבוץ</button>
                <div id="managerInter" class="inter-box"></div>
                <div id="fullAnalysis" class="analysis-text"></div>
            </div>
            <div class="card">
                <h3>רשימת עובדים</h3>
                <table>
                    <thead><tr><th>שם</th><th>תפקיד</th><th>מחלקה</th></tr></thead>
                    <tbody id="staffBody"></tbody>
                </table>
            </div>
            <button onclick="location.reload()">התנתק</button>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const questions = [
            {q: "סבלנות מול לקוחות?", opt: ["סבלני מאוד", "משתדל", "מעדיף פחות"]},
            {q: "עבודה בצוות?", opt: ["פורח בצוות", "בסדר גמור", "מעדיף לבד"]},
            {q: "עמידה בלחץ?", opt: ["מצוין בלחץ", "קצב סביר", "סביבה רגועה"]},
            {q: "סדר וארגון?", opt: ["חייב סדר", "סדר בסיסי", "פחות חשוב"]},
            {q: "זמינות?", opt: ["מלאה", "רוב הזמן", "מוגבלת"]},
            {q: "יוזמה?", opt: ["תמיד מחפש", "מה שמבקשים", "נצמד להגדרות"]},
            {q: "חיוך?", opt: ["טבעי לי", "משתדל", "רציני"]},
            {q: "דייקנות?", opt: ["תמיד לפני", "משתדל", "עיכובים"]},
            {q: "מאמץ פיזי?", opt: ["אין בעיה", "במידה", "עבודה קלה"]},
            {q: "למה MAX?", opt: ["אוהב מותג", "יציבות", "ללמוד"]}
        ];

        function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            if(u==='secretary'&&p==='max123') { document.getElementById('login-section').classList.add('hidden'); document.getElementById('sec-section').classList.remove('hidden'); changeL('he'); }
            else if(u==='manager'&&p==='admin456') { document.getElementById('login-section').classList.add('hidden'); document.getElementById('man-section').classList.remove('hidden'); loadManager(); }
        }

        function changeL(l) {
            document.getElementById('q-container').innerHTML = questions.map((q, i) => `
                <div class="card"><label>${q.q}</label><select id="ans${i}">${q.opt.map(o=>`<option>${o}</option>`).join('')}</select></div>
            `).join('');
        }

        async function submitForm() {
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: questions.map((q, i) => ({q: q.q, a: document.getElementById('ans'+i).value}))
            };
            await fetch('/api/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert("נשמר!"); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            document.getElementById('selCand').innerHTML = data.map((c, i) => `<option value='${i}'>${c.firstName}</option>`).join('');
            document.getElementById('staffBody').innerHTML = data.map(c => `<tr><td>${c.firstName}</td><td>${c.job||'---'}</td><td>${c.dept||'---'}</td></tr>`).join('');
            runAnalysis();
        }

        async function runAnalysis() {
            const idx = document.getElementById('selCand').value;
            const res = await fetch('/api/get');
            const data = await res.json();
            const cand = data[idx];
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (80 + (cand.num % 15)) + "%";
            document.getElementById('fullAnalysis').innerText = cand.analysis;
        }

        async function updateAssignment() {
            const idx = document.getElementById('selCand').value;
            await fetch('/api/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
                index: idx, dept: document.getElementById('editDept').value, job: document.getElementById('editJob').value
            })});
            alert("עודכן!"); loadManager();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['num'] = get_num(d['dob'])
    d['analysis'] = deep_analysis(d)
    d['dept'] = "טרם שובץ"; d['job'] = "טרם שובץ"
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = []
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/update', methods=['POST'])
def update():
    req = request.json
    with open('data.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    db[int(req['index'])]['dept'] = req['dept']
    db[int(req['index'])]['job'] = req['job']
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
