import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- לוגיקת חישוב (פרוטוקול אורן מעודכן לריאליות) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def analyze_candidate_logic(data):
    num = get_num(data['dob'])
    # זיהוי איכות תשובות לפי מילות מפתח חיוביות
    pos_keywords = ["מאוד", "תמיד", "מצוין", "מלאה", "פורח", "Very", "Always", "Excellent", "มาก", "เสมอ", "Очень", "Всегда", "دائماً", "جداً"]
    high_quality_ans = sum(1 for a in data['answers'] if any(word in a['a'] for word in pos_keywords))
    
    analysis = ""
    if num in [1, 8, 22]: analysis = "מועמד בעל חוסן מנטלי וכושר ביצוע. מתאים לעבודה תובענית. "
    elif num in [2, 6, 9]: analysis = "מועמד עם גישה שירותית מובהקת, מתאים לעבודה מול קהל וסיוע. "
    elif num in [4, 7]: analysis = "מועמד יסודי ודייקן, מצטיין בארגון וסידור סחורה. "
    else: analysis = "מועמד דינמי עם יכולת למידה מהירה, מתאים לתפקידים משתנים. "

    if high_quality_ans >= 8: analysis += "רמת המוטיבציה שהופגנה בשאלון גבוהה ומשלימה את נתוני הפתיחה."
    elif high_quality_ans <= 4: analysis += "ניכרת הססנות בתשובות, נדרש פיקוח צמוד בשלבים הראשונים."
    else: analysis += "מפגין נכונות סטנדרטית לעבודה במערכת."
    
    return {"analysis": analysis, "num": num, "quality": high_quality_ans, "name_factor": len(data['firstName'])}

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
        .score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 15px 0; }
        .score-box { text-align: center; padding: 15px; background: white; border-radius: 10px; border: 1px solid #ddd; }
        .score-val { font-size: 38px; font-weight: bold; color: var(--red); }
        .analysis-text { background: #fff3f3; padding: 15px; border-radius: 8px; border-right: 4px solid var(--red); line-height: 1.6; font-weight: bold; }
        .inter-box { color: #2563eb; font-weight: bold; text-align: center; margin: 10px 0; font-size: 18px; }
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
                <h3>מרכז ניתוח ובקרה</h3>
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
                <div id="fullAnalysis" class="analysis-text"></div>
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
                    {q: "Patience with customers?", opt: ["Very patient", "Calm", "Limited"]},
                    {q: "Teamwork?", opt: ["Love it", "Okay with it", "Solo"]},
                    {q: "Pressure?", opt: ["Great", "Moderate", "Quiet"]},
                    {q: "Order?", opt: ["Must have", "Basic", "Task only"]},
                    {q: "Availability?", opt: ["Full", "Most", "Limited"]},
                    {q: "Initiative?", opt: ["High", "Medium", "Low"]},
                    {q: "Service?", opt: ["Natural", "Trying", "Serious"]},
                    {q: "Punctuality?", opt: ["Always early", "On time", "Delays"]},
                    {q: "Physical?", opt: ["No problem", "Moderate", "Light"]},
                    {q: "Why MAX?", opt: ["Love brand", "Stability", "Learning"]}
                ]
            },
            th: {
                send: "ส่งให้ผู้จัดการ", success: "ส่งสำเร็จ!",
                questions: [
                    {q: "ความอดทน?", opt: ["มาก", "ปานกลาง", "น้อย"]},
                    {q: "ทำงานทีม?", opt: ["ชอบมาก", "ได้อยู่", "คนเดียว"]},
                    {q: "ความดัน?", opt: ["ดีมาก", "พอได้", "เงียบๆ"]},
                    {q: "ระเบียบ?", opt: ["ต้องมี", "พื้นฐาน", "งานสำคัญกว่า"]},
                    {q: "เวลา?", opt: ["เต็มที่", "ส่วนใหญ่", "จำกัด"]},
                    {q: "ริเริ่ม?", opt: ["สูง", "กลาง", "ต่ำ"]},
                    {q: "บริการ?", opt: ["ยิ้มแย้ม", "พยายาม", "จริงจัง"]},
                    {q: "ตรงเวลา?", opt: ["เสมอ", "พยายาม", "สายบ้าง"]},
                    {q: "แรงกาย?", opt: ["ได้เลย", "นิดหน่อย", "เบาๆ"]},
                    {q: "ทำไม MAX?", opt: ["รักแบรนด์", "มั่นคง", "เรียนรู้"]}
                ]
            }
            // רוסית וערבית יתווספו במבנה זהה
        };

        const intenseDepts = ["פלסטיקה", "חד פעמי", "עונה", "צעצועים", "יצירה"];
        const depts = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"];
        const jobs = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"];

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
            if(!data.firstName || !data.dob) return alert("אנא מלא את כל הפרטים");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(t.success); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            document.getElementById('selCand').innerHTML = data.map(c => `<option value='${JSON.stringify(c)}'>${c.firstName}</option>`).join('');
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

            // --- לוגיקת שקלול ריאלית ---
            let isIntense = intenseDepts.includes(dept);
            
            // בסיס שמשקלל את איכות התשובות (0-100)
            let baseScore = (cand.quality * 10); 
            
            // השפעת נומרולוגיה ושם על הנטייה
            let numFactor = (cand.num % 5); 
            let nameFactor = (cand.name_factor % 4);

            // חישוב התאמה למחלקה:
            // אם המחלקה אינטנסיבית (דרגה 10), הציון יורד משמעותית אם האיכות נמוכה
            let dScore = baseScore + (isIntense ? -15 : 10) + numFactor;
            
            // חישוב התאמה לתפקיד:
            // משלב את טיב התשובות עם אורך השם (יציבות)
            let jScore = baseScore + (job.length * 2) - nameFactor;

            // ריסון האחוזים לטווח ריאלי (45-98)
            dScore = Math.max(45, Math.min(dScore, 98));
            jScore = Math.max(48, Math.min(jScore, 97));

            document.getElementById('deptScore').innerText = Math.round(dScore) + "%";
            document.getElementById('jobScore').innerText = Math.round(jScore) + "%";
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (75 + (cand.num % 20)) + "%";
            document.getElementById('fullAnalysis').innerText = cand.analysis;
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
    result = analyze_candidate_logic(d)
    d.update(result)
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
