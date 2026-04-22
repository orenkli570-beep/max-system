import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def analyze_candidate(data):
    num = get_num(data['dob'])
    pos_answers = sum(1 for a in data['answers'] if any(x in a['a'] for x in ["מאוד", "תמיד", "מצוין", "מלאה"]))
    
    analysis = ""
    if num in [1, 8, 22]: analysis = "מועמד בעל עוצמה פנימית וכושר ביצוע גבוה. מתאים לעבודה תובענית ומשימתית. "
    elif num in [2, 6, 9]: analysis = "מועמד בעל אוריינטציה שירותית חזקה וסבלנות גבוהה ללקוחות. נכס לעבודת צוות. "
    elif num in [3, 5]: analysis = "בעל יכולת ורסאטילית, תפיסה מהירה ותקשורת מעולה במחלקות דינמיות. "
    else: analysis = "מועמד יציב, דייקן, מחפש סדר וארגון במקום העבודה. "
    
    if pos_answers > 7: analysis += "השאלון מעיד על רמת מוטיבציה ומוכנות לעבודה פיזית קשה."
    else: analysis += "השאלון מראה העדפה לסביבה מאורגנת וקצבית פחות."
    
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
        .header { background: white; padding: 15px; text-align: center; border-bottom: 4px solid var(--red); }
        .container { max-width: 900px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0; }
        .score-box { text-align: center; padding: 15px; background: white; border-radius: 10px; border: 1px solid #ddd; }
        .score-val { font-size: 32px; font-weight: bold; color: var(--red); }
        .analysis-text { background: #fff; padding: 15px; border-radius: 8px; border-right: 4px solid var(--red); margin-top:10px; line-height:1.6; }
        .inter-box { color: #2563eb; font-weight: bold; text-align: center; margin: 10px 0; font-size: 18px; }
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
            <button class="btn-main" onclick="login()">כניסה</button>
        </div>

        <div id="sec-section" class="hidden">
            <div id="q-container"></div>
            <input type="text" id="firstName" placeholder="שם פרטי">
            <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניתוח מנהל - שקלול אופי ומחלקות</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <select id="selDept" onchange="runAnalysis()" onmouseover="runAnalysis()"></select>
                    <select id="selJob" onchange="runAnalysis()" onmouseover="runAnalysis()"></select>
                </div>

                <div class="score-grid">
                    <div class="score-box">
                        <div style="font-size:12px; color:#64748b;">התאמה למחלקה</div>
                        <div id="deptScore" class="score-val">--%</div>
                    </div>
                    <div class="score-box">
                        <div style="font-size:12px; color:#64748b;">התאמה לתפקיד</div>
                        <div id="jobScore" class="score-val">--%</div>
                    </div>
                </div>

                <div id="managerInter" class="inter-box"></div>
                <div id="fullAnalysis" class="analysis-text">בחר מועמד לקבלת ניתוח...</div>
            </div>

            <div class="card">
                <h3>סנכרון בין עובדים (Team Sync)</h3>
                <div style="display:flex; gap:10px;">
                    <select id="workerA" onchange="checkSync()"></select>
                    <select id="workerB" onchange="checkSync()"></select>
                </div>
                <div id="syncResult" style="text-align:center; font-weight:bold; margin-top:10px; font-size:18px;"></div>
            </div>
            
            <button onclick="location.reload()" style="background:none; color:gray; border:none; text-decoration:underline; cursor:pointer;">התנתק</button>
        </div>
    </div>

    <script>
        const intenseDepts = ["פלסטיקה", "חד פעמי", "עונה", "צעצועים", "יצירה"];
        const depts = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"];
        const jobs = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"];

        function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            if(u === 'secretary' && p === 'max123') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('sec-section').classList.remove('hidden');
                renderQs();
            } else if(u === 'manager' && p === 'admin456') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('man-section').classList.remove('hidden');
                loadManager();
            }
        }

        function renderQs() {
            const qs = [
                {q: "סבלנות מול לקוחות?", opt: ["סבלני מאוד גם בעומס", "משתדל לשמור על אורך רוח", "מעדיף פחות אינטראקציה"]},
                {q: "עבודה בצוות?", opt: ["פורח בעבודת צוות", "יכול להסתדר בצוות", "מעדיף לעבוד עצמאית"]},
                {q: "עמידה בלחץ?", opt: ["מתפקד מצוין תחת לחץ", "עובד בקצב סביר", "מעדיף סביבה רגועה"]}
                // ... (יתר השאלות בקוד המלא)
            ];
            document.getElementById('q-container').innerHTML = qs.map((q, i) => `
                <div class="card"><label>${q.q}</label><select id="ans${i}">${q.opt.map(o => `<option>${o}</option>`).join('')}</select></div>
            `).join('');
        }

        async function submitForm() {
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: Array.from(document.querySelectorAll('#q-container select')).map((s, i) => ({q: "שאלה "+i, a: s.value}))
            };
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert("נשלח!"); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            const selects = ['selCand', 'workerA', 'workerB'];
            selects.forEach(id => {
                document.getElementById(id).innerHTML = data.map(c => `<option value='${JSON.stringify(c)}'>${c.firstName}</option>`).join('');
            });
            document.getElementById('selDept').innerHTML = depts.map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = jobs.map(j => `<option>${j}</option>`).join('');
            runAnalysis();
        }

        function runAnalysis() {
            const val = document.getElementById('selCand').value;
            if(!val) return;
            const cand = JSON.parse(val);
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;

            // חישוב עומק: שם, תאריך לידה ודרגת קושי
            let base = cand.score; 
            let difficulty = intenseDepts.includes(dept) ? 10 : 5;
            
            // שקלול מחלקה
            let dScore = base + (difficulty * 2) - (cand.firstName.length % 5);
            // שקלול תפקיד
            let jScore = base + (job.length * 1.5) + (cand.num % 10);

            document.getElementById('deptScore').innerText = (dScore > 99 ? 99 : dScore) + "%";
            document.getElementById('jobScore').innerText = (jScore > 99 ? 99 : jScore) + "%";
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (85 + (cand.num % 10)) + "%";
            document.getElementById('fullAnalysis').innerText = cand.full_analysis;
        }

        function checkSync() {
            const a = JSON.parse(document.getElementById('workerA').value);
            const b = JSON.parse(document.getElementById('workerB').value);
            const res = (a.num + b.num) % 10;
            const div = document.getElementById('syncResult');
            if(res > 6 || res === 0) { div.innerHTML = "✅ סנכרון גבוה - שיתוף פעולה מצוין"; div.style.color = "green"; }
            else { div.innerHTML = "⚠️ סנכרון בינוני/נמוך - דרוש פיקוח"; div.style.color = "orange"; }
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
    num = get_num(d['dob'])
    d['num'] = num
    d['full_analysis'] = analyze_candidate(d)
    d['score'] = 75 + (num % 12)
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: db = json.load(f)
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
