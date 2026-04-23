import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- נתונים ניהוליים ---
DEPARTMENTS = ["פלסטיקה", "ביוטי", "דקורציה", "עונה", "כלי מטבח", "יצירה", "צעצועים", "טקסטיל", "ניקיון", "חזרה לבית הספר", "מחסן", "חשמל", "קופות"]
ROLES = ["סדרן/ית", "קופאי/ת", "מחסנאי/ת", "סגן/ית מנהל", "אחראי/ת משמרת", "אחראי/ת מחלקה", "מלגזן/ית", "עובד/ת ניקיון", "נציג/ת שירות", "בודק/ת חשבוניות", "אחראי/ת החזרות", "סופר/ת מלאי", "מתפעל/ת מבצעים", "עובד/ת לילה", "תומך/ת טכני"]

def generate_full_analysis(data):
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    if counts['A'] >= 8:
        char_text = "מועמד בעל יוזמה יוצאת דופן. מזהה הזדמנויות לשיפור באופן עצמאי. אנרגטי וביצועיסט."
    elif counts['B'] >= 8:
        char_text = "מועמד שירותי במיוחד. רואה את הלקוח במרכז, סבלני מאוד ונעים הליכות."
    else:
        char_text = "עובד משימתי וממוקד. מצטיין בדיוק, עקביות וביצוע מטלות שגרתיות ברמה גבוהה."

    social_text = "שחקן נשמה. תורם המון לאווירה בצוות." if counts['B'] + counts['A'] >= 10 else "עצמאי וממוקד. מעדיף עבודה בגיזרה שלו."
    manager_text = "ניהול באמון: תן לו את האחריות ושחרר." if counts['A'] >= 7 else "ניהול תומך: זקוק להנחיות ברורות."

    return {"character": char_text, "social": social_text, "manager_protocol": manager_text}

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX STOCK | ניהול מועמדים</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root { --max-red: #e31e24; --max-red-dark: #b91c1c; --max-blue: #1e3a8a; --bg: #f3f4f6; }
        body { font-family: 'Heebo', sans-serif; background-color: var(--bg); margin: 0; }
        .header { background: linear-gradient(135deg, var(--max-red) 0%, var(--max-red-dark) 100%); color: white; padding: 40px 20px; text-align: center; border-bottom-left-radius: 40px; border-bottom-right-radius: 40px; }
        .container { max-width: 800px; width: 90%; margin: -30px auto 50px auto; }
        .glass-card { background: white; border-radius: 24px; padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); }
        .question-card { background: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; border-radius: 18px; margin-bottom: 20px; }
        select, input { width: 100%; padding: 14px; border-radius: 12px; border: 2px solid #e5e7eb; font-size: 1rem; font-family: 'Heebo'; }
        .btn { cursor: pointer; border: none; border-radius: 14px; padding: 16px 30px; font-weight: 700; width: 100%; transition: 0.3s; }
        .btn-primary { background: var(--max-red); color: white; }
        .btn-save { background: #10b981; color: white; margin-top: 20px; }
        .insight-box { padding: 20px; border-radius: 16px; margin-bottom: 15px; border-right: 6px solid var(--max-red); background: #fff5f5; }
        .hidden { display: none; }
    </style>
</head>
<body>

<div class="header"><h1>MAX STOCK</h1><p>מערכת גיוס ושיבוץ</p></div>

<div class="container">
    <div class="glass-card">
        
        <div id="login-view">
            <button class="btn btn-primary" onclick="showSec()">התחל שאלון מועמד</button>
            <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 30px;">
                <input type="password" id="mPass" placeholder="קוד כניסת מנהל">
                <button class="btn" style="background: var(--max-blue); color:white; margin-top:10px;" onclick="showMan()">כניסת מנהל</button>
            </div>
        </div>

        <div id="sec-view" class="hidden">
            <div id="quizArea"></div>
            <div class="question-card">
                <b>פרטי המועמד</b>
                <input type="text" id="cName" placeholder="שם מלא">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)" style="margin-top:10px;">
            </div>
            <button class="btn btn-primary" onclick="submitQuiz()">שלח שאלון</button>
        </div>

        <div id="man-view" class="hidden">
            <h2 style="color: var(--max-blue);">ניתוח ושיבוץ</h2>
            <select id="candSelect" onchange="render()"></select>
            
            <div id="insArea" style="margin-top:20px;">
                <div class="insight-box"><b>דיוקן אופי:</b> <div id="cBox"></div></div>
                <div class="insight-box" style="border-color: var(--max-blue); background: #f0f7ff;"><b>אינטראקציה חברתית:</b> <div id="sBox"></div></div>
                <div class="insight-box" style="border-color: #10b981; background: #f0fdf4;"><b>פרוטוקול ניהול:</b> <div id="mBox"></div></div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-top:20px;">
                <div><label>מחלקה:</label><select id="dSet">""" + "".join([f"<option>{d}</option>" for d in DEPARTMENTS]) + """</select></div>
                <div><label>תפקיד:</label><select id="jSet">""" + "".join([f"<option>{r}</option>" for r in ROLES]) + """</select></div>
            </div>
            <button class="btn btn-save" onclick="saveAssignment()">שמור שיבוץ מועמד</button>
            <button onclick="location.reload()" style="background:none; color:gray; width:100%; margin-top:15px; border:none; cursor:pointer;">חזרה</button>
        </div>

    </div>
</div>

<script>
    const questions = [
        {q: "לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a: "אבדוק מיד במחסן ואנסה להביא לו", b: "אבדוק במחשב או אשאל את האחראי", c: "אעדכן אותו שכרגע חסר במלאי", d: "אמשיך בעבודה שלי כרגיל"},
        {q: "יש תור ארוך בקופות ואתה בסידור מדף, מה תגובתך?", a: "אגש מיד לעזור בקופה בלי שיבקשו", b: "אחכה שיקראו לי לעזור לעמיתים", c: "אמשיך לסדר כי זה התפקיד שהוגדר לי", d: "אלך למחסן כדי להימנע מהעומס"}
        // ... שאר השאלות (קוצר לצורך התצוגה, בקוד שלך יהיו כולן)
    ];

    function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); renderQuiz(); }
    
    function renderQuiz() {
        let h = "";
        questions.forEach((item, i) => {
            h += `<div class="question-card"><b>${i+1}. ${item.q}</b>
            <select id="q${i}"><option value="A">${item.a}</option><option value="B">${item.b}</option><option value="C">${item.c}</option><option value="D">${item.d}</option></select></div>`;
        });
        document.getElementById('quizArea').innerHTML = h;
    }

    async function showMan() {
        if(document.getElementById('mPass').value === 'admin456') {
            document.getElementById('login-view').classList.add('hidden');
            document.getElementById('man-view').classList.remove('hidden');
            loadCands();
        }
    }

    async function loadCands() {
        const r = await fetch('/api/get'); window.cands = await r.json();
        document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName} ${c.assigned_dept ? '✅' : ''}</option>`).join('');
        if(window.cands.length > 0) render();
    }

    function render() {
        const c = window.cands[document.getElementById('candSelect').value];
        document.getElementById('cBox').innerText = c.full_analysis.character;
        document.getElementById('sBox').innerText = c.full_analysis.social;
        document.getElementById('mBox').innerText = c.full_analysis.manager_protocol;
        if(c.assigned_dept) document.getElementById('dSet').value = c.assigned_dept;
        if(c.assigned_role) document.getElementById('jSet').value = c.assigned_role;
    }

    async function saveAssignment() {
        const idx = document.getElementById('candSelect').value;
        const dept = document.getElementById('dSet').value;
        const role = document.getElementById('jSet').value;
        await fetch('/api/assign', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ index: idx, dept: dept, role: role })
        });
        alert("השיבוץ נשמר בהצלחה!");
        loadCands();
    }

    async function submitQuiz() {
        const answers = Array.from({length:questions.length}, (_, i) => ({ val: document.getElementById('q'+i).value }));
        await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:document.getElementById('cName').value, dob:document.getElementById('cDob').value, answers}) });
        alert("נשלח!"); location.reload();
    }
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
    d['assigned_dept'] = ""
    d['assigned_role'] = ""
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: db = json.load(f)
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/assign', methods=['POST'])
def assign():
    data = request.json
    with open('data.json', 'r', encoding='utf-8') as f: db = json.load(f)
    idx = int(data['index'])
    db[idx]['assigned_dept'] = data['dept']
    db[idx]['assigned_role'] = data['role']
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
