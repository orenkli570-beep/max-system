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

# --- ממשק HTML אחוד ---
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
        .container { max-width: 900px; margin: 30px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 25px rgba(0,0,0,0.05); }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .lang-bar { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .lang-btn { background: #eee; border: 1px solid #ccc; padding: 5px 15px; cursor: pointer; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #eee; padding: 12px; text-align: center; }
        th { background: var(--dark); color: white; }
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
            <input type="text" id="firstName" placeholder="שם פרטי">
            <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <div id="questions-container"></div>
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <h3>רשימת מועמדים וניתוח</h3>
            <div style="background:#fff1f2; padding:15px; border-radius:10px; margin-bottom:20px;">
                <label>סימולטור התאמה ואינטראקציה מול מנהל:</label>
                <select id="selCand"></select>
                <select id="selDept"></select>
                <select id="selJob"></select>
                <button class="btn-main" style="background:var(--dark);" onclick="runAnalysis()">בצע ניתוח משימות וסינרגיה</button>
                <div id="simResult" style="text-align:center; font-size:24px; font-weight:bold; color:var(--red); margin-top:15px;"></div>
            </div>
            <table id="mTable">
                <thead><tr><th>שם פרטי</th><th>תאריך לידה</th><th>התאמה כללית</th></tr></thead>
                <tbody></tbody>
            </table>
            <button onclick="logout()" style="margin-top:20px; background:#64748b; color:white; border:none; padding:10px; border-radius:8px; cursor:pointer;">התנתק</button>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const translations = {
            he: { q: ["האם יש לך סבלנות לעבודה ממושכת מול לקוחות?", "האם את/ה מעדיף/ה לעבוד בצוות או לבד?", "איך התפקוד שלך במצבי לחץ ועומס בחנות?", "האם סדר וארגון הם חלק בלתי נפרד מצורת העבודה שלך?", "האם יש לך נכונות מלאה לעבודה במשמרות?", "האם את/ה נוהג/ה להגדיל ראש ולקחת יוזמה?", "עד כמה חשוב לך לתת שירות אדיב וחייכני?", "האם את/ה מקפיד/ה על דייקנות בזמני ההגעה?", "האם יש לך מגבלה כלשהי לביצוע עבודה פיזית?", "למה לדעתך את/ה הכי מתאים/ה לעבוד ב-MAX?"], opt: ["גבוהה", "בינונית", "נמוכה"], success: "תודה רבה! התשובות שלך הוגשו בהצלחה למנהל הסניף. הנתונים נשמרו במערכת העסקית. מאחלים לך המון בהצלחה בתהליך הגיוס!" },
            th: { q: ["คุณมีความอดทนในการทำงานกับลูกค้าหรือไม่?", "คุณชอบทำงานเป็นทีมหรือทำงานคนเดียว?", "คุณทำงานภายใต้ความกดดันได้ดีแค่ไหน?", "ความเป็นระเบียบเป็นส่วนหนึ่งของการทำงานของคุณหรือไม่?", "คุณพร้อมทำงานเป็นกะหรือไม่?", "คุณมีความคิดริเริ่มในการทำงานหรือไม่?", "การบริการด้วยรอยยิ้มสำคัญสำหรับคุณแค่ไหน?", "คุณเป็นคนตรงต่อเวลาหรือไม่?", "คุณมีข้อจำกัดในการทำงานทางกายภาพหรือไม่?", "ทำไมคุณถึงเหมาะที่จะทำงานที่ MAX?"], opt: ["สูง", "ปานกลาง", "ต่ำ"], success: "ขอบคุณมาก! คำตอบของคุณถูกส่งไปยังผู้จัดการสาขาแล้ว ข้อมูลถูกบันทึกในระบบ ขอให้คุณโชคดีในการสมัครงาน!" },
            en: { q: ["Do you have patience for long shifts with customers?", "Do you prefer working in a team or alone?", "How is your performance under pressure?", "Is organization an integral part of your work?", "Are you fully available for shifts?", "Do you take initiative and show leadership?", "How important is it to provide friendly service?", "Are you punctual with arrival times?", "Do you have any physical limitations for work?", "Why are you the best fit for MAX?"], opt: ["High", "Medium", "Low"], success: "Thank you! Your answers have been submitted to the manager. Good luck!" },
            ru: { q: ["Есть ли у вас терпение для работы с клиентами?", "Вы предпочитаете работать в команде или в одиночку?", "Как вы справляетесь со стрессом?", "Является ли порядок важной частью вашей работы?", "Готовы ли вы работать по сменам?", "Проявляете ли вы инициативу?", "Насколько важно для вас вежливое обслуживание?", "Пунктуальны ли вы?", "Есть ли у вас физические ограничения?", "Почему вы подходите для MAX?"], opt: ["Высокий", "Средний", "Низкий"], success: "Спасибо! Ваши ответы отправлены менеджеру. Удачи!" },
            ar: { q: ["هل لديك صبر للعمل مع الزبائن لفترات طويلة؟", "هل تفضل العمل في فريق أم بمفردك؟", "كيف هو أداؤك تحت الضغط؟", "هل التنظيم جزء أساسي من عملك؟", "هل أنت متاح تمامًا للعمل بنظام الورديات؟", "هل تأخذ زمام المبادرة في العمل؟", "ما مدى أهمية تقديم خدمة ودودة؟", "هل تلتزم بالمواعيد بدقة؟", "هل لديك أي قيود بدنية للعمل؟", "لماذا تعتقد أنك الأنسب للعمل في MAX؟"], opt: ["عالية", "متوسطة", "منخفضة"], success: "شكراً لك! تم إرسال إجاباتك للمدير. بالتوفيق!" }
        };

        const depts = ["פלסטיקה", "חד פעמי", "כלי עבודה", "כלי מטבח", "מחלקת זכוכית", "טקסטיל", "דקורציה", "צעצועים", "יצירה", "ביוטי", "כלי כתיבה", "סלולר", "עונה"];
        const jobs = ["מנהל", "סגן מנהל", "אחראי מחלקה", "אחראי משמרת", "סדרן", "קופאית ראשית", "עובד כללי", "מנהל מחסן", "מחסנאי", "בודק סחורה", "אדמיניסטרציה"];

        async function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            const res = await fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({u, p}) });
            const result = await res.json();
            if(result.ok) { checkStatus(); } else { alert("פרטי גישה שגויים"); }
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
                <div style="margin-bottom:15px; background:#f9fafb; padding:10px; border-radius:8px;">
                    <p style="margin:5px 0; font-weight:bold;">${q}</p>
                    <select id="ans${i}">
                        <option>${lang.opt[0]}</option>
                        <option>${lang.opt[1]}</option>
                        <option>${lang.opt[2]}</option>
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
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(translations[currentLang]?.success || translations['he'].success);
            // איפוס וחזרה לעברית
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
            
            document.getElementById('selCand').innerHTML = data.map(c => `<option value="${c.score}">${c.firstName} (${c.dob})</option>`).join('');
            document.getElementById('selDept').innerHTML = depts.map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = jobs.map(j => `<option>${j}</option>`).join('');
        }

        function runAnalysis() {
            const score = parseInt(document.getElementById('selCand').value);
            document.getElementById('simResult').innerHTML = `התאמה לביצוע משימות מול מנהל: ${score + (Math.floor(Math.random()*11)-5)}%`;
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
    # שימוש בשמות המשתמש והסיסמאות המקוריים שלך
    USERS = {"secretary": "max123", "manager": "admin456"}
    if d['u'] in USERS and USERS[d['u']] == d['p']:
        session['user'] = d['u']
        session['role'] = 'manager' if d['u'] == 'manager' else 'secretary'
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401

@app.route('/api/status')
def status():
    if 'user' in session: return jsonify({"logged_in": True, "role": session['role']})
    return jsonify({"logged_in": False})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['score'] = 75 + (get_num(d['dob']) % 20)
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: db = json.load(f)
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if 'role' in session and session['role'] == 'manager':
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
