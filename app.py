import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- לוגיקת חישוב (פרוטוקול אורן) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def analyze_candidate_logic(data):
    num = get_num(data['dob'])
    name_len = len(data['firstName'])
    # בדיקה רוחבית של התשובות (מזהה מילות מפתח חיוביות בכל השפות)
    positive_keywords = ["מאוד", "תמיד", "מצוין", "מלאה", "פורח", "Very", "Always", "Thrive", "Excellent", "มาก", "เสมอ", "ที่สุด", "Очень", "Всегда", "Отлично", "دائماً", "جداً", "ممتاز"]
    high_quality_ans = sum(1 for a in data['answers'] if any(word in a['a'] for word in positive_keywords))
    
    analysis = ""
    if num in [1, 8, 22]:
        analysis = "מועמד בעל כושר ביצוע גבוה ודומיננטיות. מתאים למחלקות אינטנסיביות. "
    elif num in [2, 6, 9]:
        analysis = "מועמד בעל רגישות שירותית גבוהה ויכולת הכלה בעבודה מול קהל. "
    elif num in [4, 7]:
        analysis = "מועמד יסודי, דייקן ומתאים למשימות הדורשות ריכוז וסדר מופתי. "
    else:
        analysis = "מועמד ורסטילי, תקשורתי ובעל יכולת אלתור והסתגלות מהירה. "

    if high_quality_ans > 7:
        analysis += "מפגין מוטיבציה גבוהה מאוד ונכונות למאמץ משמעותי במערכת."
    else:
        analysis += "ניכרת העדפה ליציבות וסביבת עבודה מוגדרת היטב."
    
    return {"analysis": analysis, "num": num, "quality": high_quality_ans}

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
        .lang-btn:hover { background: #ddd; }
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
                send: "שליחה למנהל",
                success: "נשלח בהצלחה!",
                questions: [
                    {q: "סבלנות מול לקוחות?", opt: ["סבלני מאוד גם בעומס", "משתדל לשמור על אורך רוח", "מעדיף פחות אינטראקציה"]},
                    {q: "עבודה בצוות?", opt: ["פורח בעבודת צוות", "יכול להסתדר בצוות", "מעדיף לעבוד עצמאית"]},
                    {q: "עמידה בלחץ?", opt: ["מתפקד מצוין תחת לחץ", "עובד בקצב סביר", "מעדיף סביבה רגועה"]},
                    {q: "סדר וארגון?", opt: ["חייב שהכל יהיה במקום", "שומר על סדר בסיסי", "מתמקד במשימה פחות בסדר"]},
                    {q: "זמינות למשמרות?", opt: ["זמינות מלאה וגמישה", "זמין לרוב המשמרות", "זמינות מוגבלת"]}
                ]
            },
            en: {
                send: "Send to Manager",
                success: "Sent Successfully!",
                questions: [
                    {q: "Patience with customers?", opt: ["Very patient even under pressure", "Try to stay calm", "Prefer less interaction"]},
                    {q: "Teamwork?", opt: ["Thrive in a team", "Can work in a team", "Prefer working alone"]},
                    {q: "Pressure handling?", opt: ["Excellent under pressure", "Reasonable pace", "Prefer quiet environment"]},
                    {q: "Organization?", opt: ["Everything must be in place", "Basic order", "Task focused"]},
                    {q: "Availability?", opt: ["Full and flexible", "Most shifts", "Limited availability"]}
                ]
            },
            th: {
                send: "ส่งให้ผู้จัดการ",
                success: "ส่งสำเร็จ!",
                questions: [
                    {q: "ความอดทนต่อลูกค้า?", opt: ["อดทนมากแม้ในสภาวะกดดัน", "พยายามสงบสติอารมณ์", "ชอบปฏิสัมพันธ์น้อย"]},
                    {q: "การทำงานเป็นทีม?", opt: ["เติบโตได้ดีในทีม", "ทำงานเป็นทีมได้", "ชอบทำงานคนเดียว"]},
                    {q: "การจัดการแรงกดดัน?", opt: ["ยอดเยี่ยมภายใต้ความกดดัน", "ก้าวที่สมเหตุสมผล", "ชอบสภาพแวดล้อมที่เงียบสงบ"]},
                    {q: "การจัดการองค์กร?", opt: ["ทุกอย่างต้องเข้าที่", "ระเบียบพื้นฐาน", "เน้นงานมากกว่าระเบียบ"]},
                    {q: "ความพร้อมในการทำงาน?", opt: ["เต็มเวลาและยืดหยุ่น", "กะส่วนใหญ่", "จำกัดเวลา"]}
                ]
            },
            ru: {
                send: "Отправить менеджеру",
                success: "Успешно отправлено!",
                questions: [
                    {q: "Терпение к клиентам?", opt: ["Очень терпелив даже при нагрузке", "Стараюсь сохранять спокойствие", "Предпочитаю меньше общения"]},
                    {q: "Командная работа?", opt: ["Процветаю в команде", "Могу работать в команде", "Предпочитаю работать один"]},
                    {q: "Работа под давлением?", opt: ["Отлично работаю под давлением", "Разумный темп", "Предпочитаю спокойную обстановку"]},
                    {q: "Порядок и организация?", opt: ["Все должно быть на своих местах", "Базовый порядок", "Фокус на задаче"]},
                    {q: "Доступность смен?", opt: ["Полная и гибкая", "Большинство смен", "Ограниченная доступность"]}
                ]
            },
            ar: {
                send: "إرسال إلى المدير",
                success: "تم الإرسال بنجاح!",
                questions: [
                    {q: "الصبر مع الزبائن؟", opt: ["صبور جداً حتى تحت الضغط", "أحاول البقاء هادئاً", "أفضل تفاعل أقل"]},
                    {q: "العمل الجماعي؟", opt: ["أزدهر في العمل الجماعي", "يمكنني العمل في فريق", "أفضل العمل بمفردي"]},
                    {q: "العمل تحت الضغط؟", opt: ["ممتاز تحت الضغط", "سرعة معقولة", "أفضل بيئة هادئة"]},
                    {q: "النظام والتنظيم؟", opt: ["يجب أن يكون كل شيء في مكانه", "نظام أساسي", "التركيز على المهمة"]},
                    {q: "التوفر للمناوبات؟", opt: ["توفر كامل ومرن", "معظم المناوبات", "توفر محدود"]}
                ]
            }
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
            if(!data.firstName || !data.dob) return alert("Please fill all details");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(t.success); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            ['selCand', 'workerA', 'workerB'].forEach(id => {
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

            let difficulty = intenseDepts.includes(dept) ? 10 : 5;
            let base = 75 + (cand.num % 10) + (cand.quality * 1.2);
            
            let dScore = base + (difficulty === 10 ? 4 : -4) - (cand.firstName.length % 3);
            let jScore = base + (job.length * 0.5) + (cand.num % 4);

            document.getElementById('deptScore').innerText = Math.min(Math.round(dScore), 99) + "%";
            document.getElementById('jobScore').innerText = Math.min(Math.round(jScore), 99) + "%";
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (85 + (cand.num % 10)) + "%";
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
