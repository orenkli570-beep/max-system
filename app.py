import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- מנוע ניתוח מורחב (פרוטוקול אורן) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def deep_analysis(data):
    num = get_num(data['dob'])
    name = data['firstName']
    pos_keywords = ["מאוד", "תמיד", "מצוין", "מלאה", "פורח", "Very", "Always", "Excellent", "มาก", "เสมอ", "Очень", "Всегда", "دائماً", "جداً"]
    high_quality_count = sum(1 for a in data['answers'] if any(word in a['a'] for word in pos_keywords))
    
    # ניתוח בסיס לפי נומרולוגיה
    traits = {
        1: "טיפוס מנהיגותי, עצמאי, דוחף קדימה ובעל כושר ביצוע גבוה.",
        2: "טיפוס רגיש, שירותי, בעל יכולת הקשבה והכלה מעולה.",
        3: "יצירתי, תקשורתי, נהנה מאינטראקציה חברתית ובעל חיוך תמידי.",
        4: "יסודי, דייקן, אוהב סדר וארגון ומתפקד היטב בשגרה.",
        5: "דינמי, זריז, מסתגל מהר לשינויים ואוהב גיוון בעבודה.",
        6: "אחראי, משפחתי, שירותי מאוד ורואה את צורכי הזולת.",
        7: "אנליטי, שקט, מעדיף משימות עומק וריכוז גבוה.",
        8: "סמכותי, בעל חוסן מנטלי, מתמודד היטב עם לחץ ואחריות.",
        9: "בעל ראייה רחבה, נדיב, שירותי מאוד ובעל רצון לעזור.",
        11: "אינטואיטיבי, רגיש מאוד ובעל יכולת הבנה מהירה של אנשים.",
        22: "בעל יכולת תכנון וביצוע של פרויקטים גדולים ומורכבים."
    }
    base_trait = traits.get(num, "בעל יכולות מגוונות המתאימות למערכת.")

    # הצלבת נתונים לניתוח מקיף
    analysis = f"ניתוח עבור {name} (תדר {num}):\n"
    analysis += f"על פי התדר האישי, המועמד הוא {base_trait} "
    
    if high_quality_count >= 8:
        analysis += "מהשאלון עולה רמת מוטיבציה יוצאת דופן ונכונות להשקעה מקסימלית במותג. "
    elif high_quality_count <= 4:
        analysis += "התשובות בשאלון מעידות על צורך בהכוונה צמודה ועל רמת אנרגיה משתנה. "
    else:
        analysis += "המועמד מפגין עקביות ורצון להשתלב בצוות בצורה מאוזנת. "

    # המלצת מחלקות מפורטת
    intense = ["פלסטיקה", "חד פעמי", "עונה", "צעצועים", "יצירה"]
    light = ["דקורציה", "כלי כתיבה", "ביוטי", "טקסטיל", "כלי מטבח"]
    
    if num in [1, 5, 8, 22]:
        analysis += "\n\nהתאמה למחלקות: המועמד מתאים מאוד למחלקות אינטנסיביות הדורשות קצב עבודה גבוה ודינמיות, כגון: " + ", ".join(intense[:3]) + "."
        analysis += "\nפחות מתאים למחלקות סטטיות או כאלו הדורשות ישיבה ממושכת, שכן הוא זקוק לתנועה."
    else:
        analysis += "\n\nהתאמה למחלקות: המועמד יפרח במחלקות הדורשות עין אסתטית, סבלנות וסידור קפדני, כגון: " + ", ".join(light) + "."
        analysis += "\nפחות מומלץ לשבצו במחלקות כבדות ואינטנסיביות כמו " + intense[0] + " או " + intense[1] + ", שם העומס הפיזי עלול לשחוק אותו מהר מדי."

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
        .container { max-width: 900px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .analysis-text { background: #fff3f3; padding: 20px; border-radius: 8px; border-right: 6px solid var(--red); line-height: 1.8; font-weight: bold; white-space: pre-wrap; font-size: 17px; }
        .inter-box { color: #2563eb; font-weight: bold; text-align: center; margin: 15px 0; font-size: 24px; border: 2px dashed #2563eb; padding: 10px; border-radius: 10px; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
        .lang-btn { background: #eee; border: 1px solid #ccc; padding: 8px 15px; cursor: pointer; border-radius: 5px; font-weight: bold; }
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
                <button class="lang-btn" onclick="changeL('en')">English</button>
                <button class="lang-btn" onclick="changeL('th')">ไทย</button>
                <button class="lang-btn" onclick="changeL('ru')">Русский</button>
                <button class="lang-btn" onclick="changeL('ar')">العربية</button>
            </div>
            <div id="q-container"></div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <input type="text" id="firstName" placeholder="שם פרטי">
                <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" id="submitBtn" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>מרכז בקרה וניתוח מועמד</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                <div id="managerInter" class="inter-box"></div>
                <div id="fullAnalysis" class="analysis-text">אנא בחר מועמד לצפייה בניתוח המקיף...</div>
            </div>

            <div class="card">
                <h3>Team Sync - סנכרון בין עובדים</h3>
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
        let currentLang = 'he';
        const translations = {
            he: {
                send: "שליחה למנהל", success: "נשלח בהצלחה!",
                questions: [
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
                ]
            },
            en: {
                send: "Send to Manager", success: "Sent Successfully!",
                questions: [
                    {q: "Patience with customers?", opt: ["Very patient", "Moderate", "Low"]},
                    {q: "Teamwork?", opt: ["Love it", "Okay", "Solo"]},
                    {q: "Pressure?", opt: ["Excellent", "Reasonable", "Quiet environment"]},
                    {q: "Order?", opt: ["Must be organized", "Basic", "Task focused"]},
                    {q: "Availability?", opt: ["Full/Flexible", "Most shifts", "Limited"]},
                    {q: "Initiative?", opt: ["Always proactive", "Do what's asked", "Basic requirements"]},
                    {q: "Service?", opt: ["Natural smile", "Trying", "Focused"]},
                    {q: "Punctuality?", opt: ["Always early", "On time", "Delays"]},
                    {q: "Physical?", opt: ["No problem", "Moderate", "Light work"]},
                    {q: "Why MAX?", opt: ["Love brand", "Stability", "Learning"]}
                ]
            }
            // שפות נוספות יתווספו באותו מבנה
        };

        function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            if(u === 'secretary' && p === 'max123') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('sec-section').classList.remove('hidden');
                changeL('he');
            } else if(u === 'manager' && p === 'admin456') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('man-section').classList.remove('hidden');
                loadManager();
            }
        }

        function changeL(l) {
            currentLang = l;
            const t = translations[l] || translations['he'];
            document.getElementById('submitBtn').innerText = t.send;
            document.getElementById('q-container').innerHTML = t.questions.map((q, i) => `
                <div class="card"><label style="font-weight:bold;">${q.q}</label>
                <select id="ans${i}">${q.opt.map(o => `<option>${o}</option>`).join('')}</select></div>
            `).join('');
        }

        async function submitForm() {
            const t = translations[currentLang] || translations['he'];
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: t.questions.map((q, i) => ({q: q.q, a: document.getElementById('ans'+i).value}))
            };
            if(!data.firstName || !data.dob) return alert("Fill all details");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(t.success); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            ['selCand', 'workerA', 'workerB'].forEach(id => {
                document.getElementById(id).innerHTML = data.map(c => `<option value='${JSON.stringify(c)}'>${c.firstName}</option>`).join('');
            });
            runAnalysis();
        }

        function runAnalysis() {
            const val = document.getElementById('selCand').value;
            if(!val) return;
            const cand = JSON.parse(val);
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (78 + (cand.num % 18)) + "%";
            document.getElementById('fullAnalysis').innerText = cand.analysis;
        }

        function checkSync() {
            const a = JSON.parse(document.getElementById('workerA').value);
            const b = JSON.parse(document.getElementById('workerB').value);
            const sync = (a.num + b.num) % 10;
            const div = document.getElementById('syncResult');
            div.innerHTML = (sync > 6 || sync === 0) ? "✅ סנכרון גבוה - מומלץ לעבודה יחד" : "⚠️ סנכרון נמוך - מצריך השגחה";
            div.style.color = (sync > 6 || sync === 0) ? "green" : "orange";
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
    d['analysis'] = deep_analysis(d)
    d['num'] = get_num(d['dob'])
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
            try: return jsonify(json.load(f))
            except: return jsonify([])
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
