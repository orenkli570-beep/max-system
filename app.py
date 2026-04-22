import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- הגדרות קבועות ---
DEPARTMENTS = ["טקסטיל", "כלי בית", "חשמל", "צעצועים", "ניקיון", "פארם", "כלי כתיבה", "ימי הולדת", "יצירה", "כלי עבודה", "ספורט", "רכב", "חיות מחמד"]
JOBS = ["מנהל סניף", "סגן מנהל", "אחראי משמרת", "אחראי מחלקה", "קופאית", "מחסנאי", "סדרן"]

# --- לוגיקה נומרולוגית (הגילוי הפנימי) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def get_name_num(name):
    g_map = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':1,'כ':2,'ל':3,'מ':4,'נ':5,'ס':6,'ע':7,'פ':8,'צ':9,'ק':1,'ר':2,'ש':3,'ת':4,'ך':2,'ם':4,'ן':5,'ף':8,'ץ':9}
    total = sum(g_map.get(c, 0) for c in name)
    return get_num(total)

# --- ניהול מסד נתונים ---
def get_db(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def save_to_db(filename, data):
    db = get_db(filename)
    db.append(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- ממשק המשתמש (HTML/JS) ---
HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System - 2026</title>
    <style>
        :root { --red: #e31e24; --dark: #1e293b; --bg: #f8fafc; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); direction: rtl; margin: 0; padding: 15px; }
        .container { background: white; max-width: 900px; margin: 20px auto; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { color: var(--red); text-align: center; }
        .hidden { display: none; }
        input, select, .btn { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 16px; }
        .btn { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .tab-bar { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #eee; }
        .tab { padding: 10px 20px; cursor: pointer; background: #eee; border-radius: 10px 10px 0 0; }
        .tab.active { background: var(--red); color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
        th, td { border: 1px solid #eee; padding: 10px; text-align: center; }
        th { background: #f1f5f9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MAX - כאן קונים בכיף</h1>
        
        <div id="ui-login">
            <input type="password" id="pass" placeholder="הכנס סיסמה (admin/manager)">
            <button class="btn" onclick="login()">כניסה</button>
        </div>

        <div id="ui-sec" class="hidden">
            <h3>שאלון מועמד חדש</h3>
            <div id="lang-btns" style="display:flex; gap:5px; margin-bottom:15px;">
                <button onclick="setL('he')">עברית</button>
                <button onclick="setL('en')">English</button>
                <button onclick="setL('th')">ไทย</button>
                <button onclick="setL('ru')">Русский</button>
                <button onclick="setL('ar')">العربية</button>
            </div>
            <input type="text" id="cName" placeholder="שם המועמד">
            <input type="text" id="cDob" placeholder="תאריך לידה (למשל 15.05.1990)">
            <div id="questions-list"></div>
            <button class="btn" onclick="saveCand()">שלח לאישור מנהל</button>
        </div>

        <div id="ui-man" class="hidden">
            <div class="tab-bar">
                <div class="tab active" onclick="showView('v-list')">רשימת מועמדים</div>
                <div class="tab" onclick="showView('v-match')">בדיקת התאמה וסינרגיה</div>
            </div>

            <div id="v-list">
                <table>
                    <thead><tr><th>שם</th><th>התאמה</th><th>מחלקה</th><th>תפקיד</th></tr></thead>
                    <tbody id="mTable"></tbody>
                </table>
            </div>

            <div id="v-match" class="hidden">
                <h4>בדיקת התאמה אישית</h4>
                <select id="selCand"></select>
                <select id="selDept"></select>
                <select id="selJob"></select>
                <button class="btn" onclick="checkMatch()">חשב התאמה</button>
                <div id="matchRes" style="font-size:24px; text-align:center; margin-top:15px; color:var(--red);"></div>
            </div>
            
            <button class="btn" onclick="location.reload()" style="background:#475569; margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        let curL = 'he';
        const dict = {
            he: { q: ["סבלנות?","צוות?","לחץ?","סדר?","משמרות?","יוזמה?","שירות?","דייקנות?","פיזי?","למה MAX?"], a: ["גבוהה","בינונית","נמוכה"] },
            th: { q: ["ความอดทน?","ทำงานเป็นทีม?","กดดัน?","ระเบียบ?","กะงาน?","ริเริ่ม?","บริการ?","ตรงเวลา?","ร่างกาย?","ทำไม MAX?"], a: ["สูง","กลาง","ต่ำ"] }
        };
        const depts = ["טקסטיל", "כלי בית", "חשמל", "צעצועים", "ניקיון", "פארם", "כלי כתיבה", "ימי הולדת", "יצירה", "כלי עבודה", "ספורט", "רכב", "חיות מחמד"];
        const jobs = ["מנהל סניף", "סגן מנהל", "אחראי משמרת", "אחראי מחלקה", "קופאית", "מחסנאי", "סדרן"];

        function login() {
            const p = document.getElementById('pass').value;
            if(p==='admin') { document.getElementById('ui-login').classList.add('hidden'); document.getElementById('ui-sec').classList.remove('hidden'); renderQ(); }
            if(p==='manager') { document.getElementById('ui-login').classList.add('hidden'); document.getElementById('ui-man').classList.remove('hidden'); loadMan(); }
        }

        function renderQ() {
            const qBox = document.getElementById('questions-list');
            const d = dict[curL] || dict['he'];
            qBox.innerHTML = d.q.map((q, i) => `
                <div style="border-bottom:1px solid #eee; padding:10px;">
                    <label>${q}</label>
                    <select id="ans${i}"><option>${d.a[0]}</option><option>${d.a[1]}</option><option>${d.a[2]}</option></select>
                </div>
            `).join('');
        }

        async function saveCand() {
            const payload = {
                name: document.getElementById('cName').value,
                dob: document.getElementById('cDob').value,
                ans: Array.from({length:10}, (_, i) => document.getElementById('ans'+i).value)
            };
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
            alert("נשלח בהצלחה"); location.reload();
        }

        async function loadMan() {
            const r = await fetch('/api/get');
            const data = await r.json();
            document.getElementById('mTable').innerHTML = data.reverse().map(c => `
                <tr><td>${c.name}</td><td style="font-weight:bold; color:red;">${c.score}%</td><td>${c.dept}</td><td>${c.job}</td></tr>
            `).join('');
            
            // מילוי סלקטים לבדיקה
            document.getElementById('selCand').innerHTML = data.map(c => `<option value="${c.dob}|${c.name}">${c.name}</option>`).join('');
            document.getElementById('selDept').innerHTML = depts.map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = jobs.map(j => `<option>${j}</option>`).join('');
        }

        function checkMatch() {
            const [dob, name] = document.getElementById('selCand').value.split('|');
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;
            
            // חישוב התאמה מהיר (כסימולציה)
            const score = 70 + (dob.length + name.length + dept.length + job.length) % 28;
            document.getElementById('matchRes').innerText = `אחוז התאמה: ${score}%`;
        }

        function showView(v) {
            document.getElementById('v-list').classList.toggle('hidden', v!=='v-list');
            document.getElementById('v-match').classList.toggle('hidden', v!=='v-match');
            document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.innerText.includes(v==='v-list'?'רשימה':'בדיקה')));
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    n_num = get_name_num(d['name'])
    d_num = get_num(d['dob'])
    d['dept'] = DEPARTMENTS[d_num % len(DEPARTMENTS)]
    d['job'] = JOBS[n_num % len(JOBS)]
    d['score'] = 75 + (n_num + d_num) % 25
    save_to_db('candidates.json', d)
    return jsonify({"ok":True})

@app.route('/api/get')
def get_data():
    return jsonify(get_db('candidates.json'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
