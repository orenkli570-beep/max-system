import os
from flask import Flask, request, jsonify, render_template_string, session
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- הגדרות קבועות לפי פרוטוקול אורן ---
DEPARTMENTS = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"]
JOBS = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"]

def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System</title>
    <style>
        :root { --red: #e31e24; --dark: #1e293b; --bg: #f1f5f9; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); margin: 0; direction: rtl; }
        .header { background: white; padding: 20px; text-align: center; border-bottom: 4px solid var(--red); box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { color: var(--red); margin: 0; font-size: 28px; }
        .header h2 { color: var(--dark); margin: 5px 0 0; font-size: 18px; font-weight: normal; }
        .container { max-width: 800px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-main:hover { opacity: 0.9; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
        .lang-btn { background: #f8fafc; border: 1px solid #cbd5e1; padding: 6px 12px; cursor: pointer; border-radius: 6px; font-size: 14px; }
        .question-card { background: #f9fafb; padding: 12px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #f1f5f9; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #edf2f7; padding: 10px; text-align: center; }
        th { background: var(--dark); color: white; }
        .logout-btn { background: none; border: none; color: #64748b; cursor: pointer; text-decoration: underline; font-size: 14px; margin-top: 20px; width: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MAX – כאן קונים בכיף</h1>
        <h2>מערכת סינון וגיוס חכמה</h2>
    </div>

    <div class="container">
        <div id="login-section">
            <input type="text" id="username" placeholder="שם משתמש">
            <input type="password" id="password" placeholder="סיסמה">
            <button class="btn-main" onclick="login()">כניסה למערכת</button>
        </div>

        <div id="sec-section" class="hidden">
            <div class="lang-bar">
                <button class="lang-btn" onclick="changeL('he')">עברית</button>
                <button class="lang-btn" onclick="changeL('th')">ไทย</button>
                <button class="lang-btn" onclick="changeL('en')">English</button>
                <button class="lang-btn" onclick="changeL('ru')">Русский</button>
                <button class="lang-btn" onclick="changeL('ar')">العربية</button>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="firstName" placeholder="שם פרטי">
                <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <div id="questions-container"></div>
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
            <center><button class="logout-btn" onclick="logout()">יציאה מהמערכת</button></center>
        </div>

        <div id="man-section" class="hidden">
            <h3>לוח בקרה - מנהל</h3>
            <div style="background:#fff1f2; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #fecaca;">
                <label>סימולטור התאמה מול מחלקות ותפקידים:</label>
                <select id="selCand"></select>
                <select id="selDept"></select>
                <select id="selJob"></select>
                <button class="btn-main" style="background:var(--dark);" onclick="runAnalysis()">בצע ניתוח משימות וסינרגיה</button>
                <div id="simResult" style="text-align:center; font-size:22px; font-weight:bold; color:var(--red); margin-top:10px;"></div>
            </div>
            <table id="mTable">
                <thead><tr><th>שם פרטי</th><th>תאריך לידה</th><th>התאמה</th></tr></thead>
                <tbody></tbody>
            </table>
            <center><button class="logout-btn" onclick="logout()">התנתק</button></center>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const translations = {
            he: { 
                q: [
                    "האם יש לך סבלנות לעבודה ממושכת מול לקוחות?", 
                    "האם את/ה מעדיף/ה לעבוד בצוות או לבד?", 
                    "איך התפקוד שלך במצבי לחץ ועומס בחנות?", 
                    "האם סדר וארגון הם חלק בלתי נפרד מצורת העבודה שלך?", 
                    "האם יש לך נכונות מלאה לעבודה במשמרות?", 
                    "האם את/ה נוהג/ה להגדיל ראש ולקחת יוזמה?", 
                    "עד כמה חשוב לך לתת שירות אדיב וחייכני?", 
                    "האם את/ה מקפיד/ה על דייקנות בזמני ההגעה?", 
                    "האם יש לך מגבלה כלשהי לביצוע עבודה פיזית?", 
                    "למה לדעתך את/ה הכי מתאים/ה לעבוד ב-MAX?"
                ],
                opt: [
                    ["סבלני מאוד", "סבלני במידה מסוימת", "מאבד סבלנות מהר"],
                    ["אוהב צוות", "גם וגם", "מעדיף לעבוד לבד"],
                    ["מתפקד מעולה", "משתדל לעמוד בקצב", "נלחץ בקלות"],
                    ["מאורגן מאוד", "משתדל לשמור על סדר", "פחות מאורגן"],
                    ["זמין תמיד", "זמין חלקית", "מוגבל בשעות"],
                    ["יוזם תמיד", "מבצע מה שמבקשים", "רק מה שצריך"],
                    ["חשוב מאוד", "חשוב במידה סבירה", "פחות קריטי"],
                    ["מדייק תמיד", "משתדל לדייק", "לפעמים מאחר"],
                    ["אין מגבלה", "מגבלה קלה", "יש מגבלה משמעותית"],
                    ["מוטיבציה גבוהה", "חיפוש עבודה יציבה", "סקרנות למותג"]
                ],
                success: "תודה רבה! התשובות שלך הוגשו בהצלחה למנהל הסניף. הנתונים נשמרו במערכת העסקית. מאחלים לך המון בהצלחה בתהליך הגיוס!" 
            }
            // (תרגומים נוספים לשפות אחרות יוכנסו כאן באותו מבנה)
        };

        const depts = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"];
        const jobs = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"];

        async function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            const res = await fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u, p}) });
            if(res.ok) { checkStatus(); } else { alert("פרטי גישה שגויים"); }
        }

        async function checkStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            if(data.logged_in) {
                document.getElementById('login-section').classList.add('hidden');
                if(data.role === 'manager') {
                    document.getElementById('man-section').classList.remove('hidden');
                    loadManager();
                } else {
                    document.getElementById('sec-section').classList.remove('hidden');
                    renderQs();
                }
            }
        }

        function renderQs() {
            const container = document.getElementById('questions-container');
            const lang = translations[currentLang] || translations['he'];
            container.innerHTML = lang.q.map((q, i) => `
                <div class="question-card">
                    <p style="margin:0 0 8px 0; font-weight:bold;">${q}</p>
                    <select id="ans${i}">
                        ${lang.opt[i].map(o => `<option>${o}</option>`).join('')}
                    </select>
                </div>
            `).join('');
        }

        function changeL(l) { currentLang = l; renderQs(); }

        async function submitForm() {
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: Array.from({length:10}, (_, i) => document.getElementById('ans'+i).value)
            };
            if(!data.firstName || !data.dob) return alert("נא למלא שם ותאריך לידה");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(translations[currentLang]?.success || translations['he'].success);
            currentLang = 'he';
            document.getElementById('firstName').value = '';
            document.getElementById('dob').value = '';
            renderQs();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            document.querySelector('#mTable tbody').innerHTML = data.reverse().map(c => `
                <tr><td>${c.firstName}</td><td>${c.dob}</td><td style="color:red; font-weight:bold;">${c.score}%</td></tr>
            `).join('');
            document.getElementById('selCand').innerHTML = data.map(c => `<option value="${c.score}">${c.firstName}</option>`).join('');
            document.getElementById('selDept').innerHTML = depts.map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = jobs.map(j => `<option>${j}</option>`).join('');
        }

        function runAnalysis() {
            const s = parseInt(document.getElementById('selCand').value);
            document.getElementById('simResult').innerHTML = `התאמה למשימות: ${s + (Math.floor(Math.random()*9)-4)}%`;
        }

        async function logout() { await fetch('/api/logout'); location.reload(); }
        checkStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    USERS = {"secretary": "max123", "manager": "admin456"}
    if d['u'] in USERS and USERS[d['u']] == d['p']:
        session['user'] = d['u']
        session['role'] = 'manager' if d['u'] == 'manager' else 'secretary'
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401

@app.route('/api/status')
def status():
    return jsonify({"logged_in": 'user' in session, "role": session.get('role')})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['score'] = 72 + (get_num(d['dob']) % 22)
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: db = json.load(f)
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if session.get('role') == 'manager' and os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
