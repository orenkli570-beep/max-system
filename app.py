import os
from flask import Flask, request, jsonify, render_template_string, session
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- לוגיקת חישוב וניתוח אופי (הגילוי הפנימי) ---
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
        9: "נתינה, סבלנות, רב-גוניות", 11: "אינטואיציה חדה, השראה", 22: "בנייה מערכתית ויכולת עבודה תחת עומס"
    }
    return traits.get(num, "יכולת עבודה כללית")

# --- ממשק HTML אחוד ---
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
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; }
        .lang-btn { background: #f8fafc; border: 1px solid #ddd; padding: 8px 15px; cursor: pointer; border-radius: 6px; font-weight: bold; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        .score-display { font-size: 45px; font-weight: bold; color: var(--red); text-align: center; transition: 0.2s; }
        .sync-box { display: flex; gap: 15px; margin-top: 15px; }
        .logout-link { text-align: center; display: block; margin-top: 20px; color: #64748b; cursor: pointer; text-decoration: underline; }
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
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <input type="text" id="firstName" placeholder="שם פרטי">
                <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <div id="q-container"></div>
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
            <span class="logout-link" onclick="location.reload()">התנתק</span>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניתוח התאמה דינמי (Hover)</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <select id="selDept" onmouseover="runAnalysis()"></select>
                    <select id="selJob" onmouseover="runAnalysis()"></select>
                </div>
                <div id="resScore" class="score-display">--%</div>
                <div id="resTraits" style="text-align:center; color:#475569; font-weight:bold; margin-top:10px;"></div>
            </div>

            <div class="card">
                <h3>Team Sync - בדיקת סנכרון בין עובדים</h3>
                <div class="sync-box">
                    <select id="workerA" onchange="checkSync()"></select>
                    <select id="workerB" onchange="checkSync()"></select>
                </div>
                <div id="syncResult" style="text-align:center; font-size:18px; font-weight:bold; margin-top:15px;"></div>
            </div>
            <span class="logout-link" onclick="location.reload()">התנתק</span>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const translations = {
            he: { q: ["סבלנות מול לקוחות?", "עבודה בצוות?", "עמידה בלחץ?", "סדר וארגון?", "זמינות למשמרות?", "יוזמה וראש גדול?", "שירות עם חיוך?", "דייקנות?", "מאמץ פיזי?", "למה דווקא MAX?"], opt: ["גבוהה", "בינונית", "נמוכה"], success: "תודה רבה! התשובות שלך הוגשו למנהל." },
            th: { q: ["ความอดทนต่อลูกค้า?", "ทำงานเป็นทีม?", "ภายใต้ความกดดัน?", "ความเป็นระเบียบ?", "ความพร้อมกะ?", "ความคิดริเริ่ม?", "บริการด้วยรอยยิ้ม?", "ตรงต่อเวลา?", "ความพยายามทางกายภาพ?", "ทำไมต้อง MAX?"], opt: ["สูง", "ปานกลาง", "ต่ำ"], success: "ขอบคุณมาก! ส่งคำตอบของคุณเรียบร้อยแล้ว" },
            en: { q: ["Patience with customers?", "Team player?", "Performance under pressure?", "Organization?", "Shift availability?", "Take initiative?", "Service with a smile?", "Punctuality?", "Physical effort?", "Why MAX?"], opt: ["High", "Medium", "Low"], success: "Thank you! Your answers have been submitted." },
            ru: { q: ["Терпение к клиентам?", "Работа в команде?", "Под давлением?", "Организованность?", "Готовность к сменам?", "Инициативность?", "Обслуживание с улыбкой?", "Пунктуальность?", "Физ. нагрузка?", "Почему MAX?"], opt: ["Высокий", "Средний", "Низкий"], success: "Спасибо! Ваши ответы отправлены." },
            ar: { q: ["الصبر مع الزبائن؟", "العمل الجماعي؟", "العمل تحت الضغط؟", "النظام والترتيب؟", "جاهزية المناوبات؟", "المبادرة؟", "الخدمة بابتسامة؟", "الدقة والمواعيد؟", "الجهد البدני؟", "لماذا MAX؟"], opt: ["عالية", "متوسطة", "منخفضة"], success: "شكراً لك! تم إرسال إجاباتك." }
        };

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
            } else { alert("גישה נדחתה"); }
        }

        function changeL(l) {
            currentLang = l;
            const qCont = document.getElementById('q-container');
            const t = translations[l];
            qCont.innerHTML = t.q.map((q, i) => `
                <div style="margin-bottom:12px; background:#fff; padding:10px; border-radius:8px; border:1px solid #edf2f7;">
                    <label style="font-weight:bold; color:var(--dark);">${q}</label>
                    <select id="ans${i}">${t.opt.map(o => `<option>${o}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function submitForm() {
            const data = { firstName: document.getElementById('firstName').value, dob: document.getElementById('dob').value };
            if(!data.firstName || !data.dob) return alert("נא למלא פרטים");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert(translations[currentLang].success);
            location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            const selects = ['selCand', 'workerA', 'workerB'];
            selects.forEach(sId => {
                document.getElementById(sId).innerHTML = data.map(c => `<option value='${JSON.stringify(c)}'>${c.firstName}</option>`).join('');
            });
            document.getElementById('selDept').innerHTML = depts.map(d => `<option>${d}</option>`).join('');
            document.getElementById('selJob').innerHTML = jobs.map(j => `<option>${j}</option>`).join('');
            runAnalysis();
        }

        function runAnalysis() {
            const candRaw = document.getElementById('selCand').value;
            if(!candRaw) return;
            const cand = JSON.parse(candRaw);
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;
            
            // חישוב דינמי במעבר עכבר
            let dynamic = cand.score + (dept.length % 7) + (job.length % 5);
            if(dynamic > 99) dynamic = 99;

            document.getElementById('resScore').innerHTML = dynamic + "%";
            document.getElementById('resTraits').innerHTML = "פרופיל אופי: " + cand.traits;
        }

        function checkSync() {
            const a = JSON.parse(document.getElementById('workerA').value);
            const b = JSON.parse(document.getElementById('workerB').value);
            const syncScore = (a.num + b.num) % 10;
            const res = document.getElementById('syncResult');
            if(syncScore > 6 || syncScore === 0) {
                res.innerHTML = "🏆 סינרגיה גבוהה - צוות מנצח";
                res.style.color = "green";
            } else {
                res.innerHTML = "⚠️ סנכרון נמוך - דרוש ניהול צמוד";
                res.style.color = "orange";
            }
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
    d['score'] = 70 + (num % 22)
    d['traits'] = get_character_traits(num)
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
