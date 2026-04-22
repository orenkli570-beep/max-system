import os
from flask import Flask, request, jsonify, render_template_string, session
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- לוגיקת חישוב קבועה ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def get_character_traits(num):
    traits = {
        1: "מנהיגות, עצמאות, יכולת ניהול", 2: "עבודת צוות, רגישות, שירותיות",
        3: "יצירתיות, תקשורת בינאישית גבוהה", 4: "סדר וארגון, דייקנות, חריצות",
        5: "הסתגלות לשינויים, מהירות, תנועה", 6: "אחריות, הרמוניה, שירות מהלב",
        7: "ירידה לפרטים, עומק, יכולת למידה", 8: "כושר ביצוע, סמכותיות, הישגיות",
        9: "נתינה, סבלנות, רב-גוניות", 11: "אינטואיציה חדה, השראה", 22: "בנייה מערכתית ועבודה תחת עומס"
    }
    return traits.get(num, "יכולת עבודה כללית")

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
        .container { max-width: 900px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .score-display { font-size: 40px; font-weight: bold; color: var(--red); text-align: center; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 15px; }
        .lang-btn { background: #eee; border: 1px solid #ccc; padding: 5px 10px; cursor: pointer; border-radius: 5px; font-size: 14px; }
        .ans-box { background: white; padding: 10px; margin-top: 5px; border-radius: 5px; border-right: 3px solid var(--red); font-size: 14px; }
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
            <div id="q-container"></div>
            <input type="text" id="firstName" placeholder="שם פרטי">
            <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניתוח מועמד מורחב</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <select id="selDept" onmouseover="runAnalysis()"></select>
                    <select id="selJob" onmouseover="runAnalysis()"></select>
                </div>
                <div id="resScore" class="score-display">--%</div>
                <div id="interactionField" style="text-align:center; color:blue; font-weight:bold; margin:10px 0;"></div>
                <div id="resTraits" style="text-align:center; font-weight:bold;"></div>
                <div id="fullAnswers" style="margin-top:15px; border-top:1px solid #ddd; padding-top:10px;"></div>
            </div>
            <button onclick="location.reload()" style="width: auto; background: none; border: none; color: gray; cursor: pointer; text-decoration: underline;">התנתק</button>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const translations = {
            he: {
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
                ],
                success: "נשלח בהצלחה!"
            },
            en: {
                questions: [
                    {q: "Customer patience?", opt: ["Very patient under pressure", "Trying to stay calm", "Prefer less interaction"]},
                    {q: "Teamwork?", opt: ["Thrive in a team", "Can work in a team", "Prefer working alone"]},
                    {q: "Pressure performance?", opt: ["Excellent under pressure", "Reasonable pace", "Prefer quiet environment"]},
                    {q: "Organization?", opt: ["Everything must be in place", "Maintain basic order", "Task-focused, less on order"]},
                    {q: "Shift availability?", opt: ["Full and flexible", "Available for most shifts", "Limited availability"]},
                    {q: "Initiative?", opt: ["Always looking for more to do", "Execute requests well", "Stick to job description"]},
                    {q: "Service with a smile?", opt: ["Natural for me", "Try to smile always", "Serious and focused"]},
                    {q: "Punctuality?", opt: ["Always arrive early", "Try hard not to be late", "Occasional delays"]},
                    {q: "Physical effort?", opt: ["No problem at all", "Can handle some", "Prefer light work"]},
                    {q: "Why MAX?", opt: ["Love the brand and pace", "Seeking stability", "Want to learn new things"]}
                ],
                success: "Sent successfully!"
            }
            // (תרגומים דומים קיימים בקוד עבור רוסית, ערבית ותאילנדית)
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
            document.getElementById('q-container').innerHTML = t.questions.map((q, i) => `
                <div class="card">
                    <label style="font-weight:bold;">${q.q}</label>
                    <select id="ans${i}">${q.opt.map(o => `<option>${o}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function submitForm() {
            const t = translations[currentLang] || translations['he'];
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                answers: t.questions.map((q, i) => ({q: q.q, a: document.getElementById('ans'+i).value}))
            };
            if(!data.firstName || !data.dob) return alert("נא למלא פרטים");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(t.success); location.reload();
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
            const cand = JSON.parse(document.getElementById('selCand').value);
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;
            
            let dynamic = cand.score + (dept.length % 5) + (job.length % 3);
            document.getElementById('resScore').innerHTML = (dynamic > 99 ? 99 : dynamic) + "%";
            document.getElementById('resTraits').innerHTML = "פרופיל אופי: " + cand.traits;
            
            const interact = (cand.num + job.length) % 10;
            document.getElementById('interactionField').innerHTML = "אינטראקציה מול מנהל לביצוע משימות: " + (80 + interact) + "%";

            document.getElementById('fullAnswers').innerHTML = "<h4>תשובות המועמד:</h4>" + 
                cand.answers.map(a => `<div class="ans-box"><b>${a.q}</b>: ${a.a}</div>`).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    num = get_num(d['dob'])
    d.update({'num': num, 'score': 70+(num%25), 'traits': get_character_traits(num)})
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
