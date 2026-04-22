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

# פונקציה לניתוח ריאלי ומשולב
def analyze_candidate(data):
    num = get_num(data['dob'])
    name_val = len(data['firstName']) % 5
    # שקלול תשובות - בדיקה כמה תשובות הן "חיוביות/גבוהות"
    pos_answers = sum(1 for a in data['answers'] if "מאוד" in a['a'] or "תמיד" in a['a'] or "מצוין" in a['a'] or "מלאה" in a['a'])
    
    analysis = ""
    if num == 1 or num == 8: analysis = "אדם עם כושר ביצוע גבוה, ממוקד מטרה וסמכותי. "
    elif num == 2 or num == 6: analysis = "ניחן ברגישות בינאישית גבוהה, שירותי מאוד ומתאים לעבודה עם קהל. "
    elif num == 4 or num == 7: analysis = "יסודי מאוד, דייקן ובעל יכולת למידה של פרטים טכניים. "
    else: analysis = "ורסטילי, מסתגל מהר לשינויים ובעל תקשורת טובה. "
    
    if pos_answers > 7: analysis += "התשובות מעידות על רמת מוטיבציה גבוהה ומוכנות למאמץ. "
    else: analysis += "ניכרת העדפה לסביבת עבודה יציבה וברורה ללא שינויים קיצוניים. "
    
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
        .score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .score-box { text-align: center; padding: 15px; background: white; border-radius: 10px; border: 1px solid #ddd; }
        .score-val { font-size: 32px; font-weight: bold; color: var(--red); }
        .label { font-size: 14px; color: #64748b; }
        .analysis-text { background: #fff3f3; padding: 15px; border-radius: 8px; border-right: 4px solid var(--red); line-height: 1.6; font-weight: 500; }
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
                <h3>ניתוח מנהל חכם</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <select id="selDept" onchange="runAnalysis()" onmouseover="runAnalysis()"></select>
                    <select id="selJob" onchange="runAnalysis()" onmouseover="runAnalysis()"></select>
                </div>

                <div class="score-grid">
                    <div class="score-box">
                        <div class="label">התאמה למחלקה</div>
                        <div id="deptScore" class="score-val">--%</div>
                    </div>
                    <div class="score-box">
                        <div class="label">התאמה לתפקיד</div>
                        <div id="jobScore" class="score-val">--%</div>
                    </div>
                </div>

                <div id="fullAnalysis" class="analysis-text">בחר מועמד לקבלת ניתוח...</div>
            </div>
            <button onclick="location.reload()" style="background:none; color:gray; border:none; text-decoration:underline; cursor:pointer;">התנתק</button>
        </div>
    </div>

    <script>
        const questions = [
            {q: "סבלנות מול לקוחות?", opt: ["סבלני מאוד גם בעומס", "משתדל לשמור על אורך רוח", "מעדיף פחות אינטראקציה"]},
            {q: "עבודה בצוות?", opt: ["פורח בעבודת צוות", "יכול להסתדר בצוות", "מעדיף לעבוד עצמאית"]},
            {q: "עמידה בלחץ?", opt: ["מתפקד מצוין תחת לחץ", "עובד בקצב סביר", "מעדיף סביבה רגועה"]},
            {q: "סדר וארגון?", opt: ["חייב שהכל יהיה במקום", "שומר על סדר בסיסי", "מתמקד במשימה פחות בסדר"]},
            {q: "זמינות למשמרות?", opt: ["זמינות מלאה וגמישה", "זמין לרוב המשמרות", "זמינות מוגבלת"]},
            {q: "יוזמה וראש גדול?", opt: ["תמיד מחפש מה עוד לעשות", "מבצע היטב מה שמבקשים", "נצמד להגדרות התפקיד"]},
            {q: "שירות עם חיוך?", opt: ["זה טבעי עבורי", "משתדל לחייך תמיד", "רציני וממוקד עבודה"]},
            {q: "דייקנות?", opt: ["מגיע תמיד לפני הזמן", "משתדל מאוד לא לאחר", "מדי פעם יש עיכובים"]},
            {q: "מאמץ פיזי?", opt: ["אין לי שום בעיה", "יכול להתמודד במידה", "מעדיף עבודה קלה פיזית"]},
            {q: "למה MAX?", opt: ["אוהב את המותג והקצב", "מחפש יציבות תעסוקתית", "רוצה ללמוד תחום חדש"]}
        ];

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
            document.getElementById('q-container').innerHTML = questions.map((q, i) => `
                <div class="card"><label>${q.q}</label><select id="ans${i}">${q.opt.map(o => `<option>${o}</option>`).join('')}</select></div>
            `).join('');
        }

        async function submitForm() {
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: questions.map((q, i) => ({q: q.q, a: document.getElementById('ans'+i).value}))
            };
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert("נשלח!"); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            document.getElementById('selCand').innerHTML = data.map(c => `<option value='${JSON.stringify(c)}'>${c.firstName}</option>`).join('');
            document.getElementById('selDept').innerHTML = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"].map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"].map(j => `<option>${j}</option>`).join('');
            runAnalysis();
        }

        function runAnalysis() {
            const val = document.getElementById('selCand').value;
            if(!val) return;
            const cand = JSON.parse(val);
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;

            // חישוב אחוזים נפרד שמשתנה לפי הבחירה
            let dScore = cand.score + (dept.length * 2) % 15;
            let jScore = cand.score + (job.length * 3) % 12;

            document.getElementById('deptScore').innerText = (dScore > 99 ? 99 : dScore) + "%";
            document.getElementById('jobScore').innerText = (jScore > 99 ? 99 : jScore) + "%";
            document.getElementById('fullAnalysis').innerText = cand.full_analysis;
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
    # יצירת הניתוח כבר בשלב השמירה
    d['full_analysis'] = analyze_candidate(d)
    d['score'] = 75 + (num % 15)
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
