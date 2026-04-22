import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- לוגיקה עסקית: ניתוח עומק ואינטראקציה ---

def get_numerology_num(dob):
    if not dob: return 0
    nums = [int(d) for d in dob if d.isdigit()]
    res = sum(nums)
    while res > 9 and res not in [11, 22]:
        res = sum(int(digit) for digit in str(res))
    return res

def generate_full_analysis(data):
    num = get_numerology_num(data.get('dob', ''))
    proactive_score = sum(1 for a in data.get('answers', []) if a['idx'] == "1")
    
    traits = {
        1: "מנהיגות וביצוע עצמאי. אדם שמוביל תהליכים ולא מחכה להוראות.",
        2: "שירותיות, הכלה ועבודת צוות. זקוק לסביבה אנושית נעימה.",
        3: "תקשורת בין-אישית גבוהה ויצירתיות בפתרון בעיות.",
        4: "סדר, דיוק וארגון מופתי. מצטיין במשימות יסודיות.",
        5: "זריזות, דינמיות והסתגלות מהירה לשינויים.",
        6: "אחראי, הרמוני ורואה את טובת החנות כערך עליון.",
        7: "ריכוז, עומק ויכולת למידה עצמית גבוהה של נהלים.",
        8: "חוסן מנטלי, ניהול לחצים ויכולת עבודה בעומס.",
        9: "ראייה רחבה, סבלנות רבה ורצון לעזור לזולת.",
        11: "אינטואיציה חזקה והבנה מהירה של צרכי המערכת.",
        22: "בעל יכולת ביצוע מרשימה ובניית תשתיות מאפס."
    }
    
    char_text = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות גבוהה.")
    
    if proactive_score >= 10:
        inter_text = "העובד הפגין יוזמה גבוהה ('ראש גדול'). המנהל נדרש לתת לו אוטונומיה. מומלץ להגדיר יעדים ולהניח לו לנהל את המשימה. הוא יזהה צרכים לבד (סידור מדפים/ניקיון) ללא צורך בפיקוח צמוד."
        recom = "מחלקות דינמיות: פלסטיקה, עונה, מחסן."
    else:
        inter_text = "העובד זקוק להנחיות ברורות ומובנות. המנהל נדרש להגדיר משימות שלב-אחרי-שלב ולתת משוב חיובי. העובד יבצע עבודה נאמנה תחת ניהול מובנה."
        recom = "מחלקות שירותיות: ביוטי, דקורציה, כלי כתיבה."

    return {"character": char_text, "interaction": inter_text, "recommendation": recom}

# --- ממשק משתמש (HTML) ---

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System 2026</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; --bg: #f1f5f9; }
        body { font-family: 'Segoe UI', system-ui; background: var(--bg); margin: 0; }
        .header { background: white; padding: 20px; text-align: center; border-bottom: 5px solid var(--max-red); }
        .container { max-width: 850px; margin: 20px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .hidden { display: none; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn-lang { padding: 8px 16px; cursor: pointer; border: 2px solid #ddd; background: white; border-radius: 20px; font-weight: bold; }
        .btn-lang.active { background: var(--max-red); color: white; border-color: var(--max-red); }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; margin-bottom: 12px; }
        .insight-card { padding: 15px; border-radius: 10px; margin-bottom: 15px; border-right: 5px solid var(--max-red); background: #fef2f2; line-height: 1.5; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; }
        .btn-main { background: var(--max-red); color: white; border: none; font-weight: bold; cursor: pointer; font-size: 1.1em; }
        .error-msg { color: var(--max-red); font-size: 0.9em; font-weight: bold; margin-bottom: 10px; display: none; }
    </style>
</head>
<body>
    <div class="header"><h1 id="mainTitle">MAX - כאן קונים בכיף</h1></div>
    <div class="container">
        
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">כניסת מזכירה (שאלון מועמד)</button>
            <input type="password" id="mPass" placeholder="סיסמת מנהל">
            <button class="btn-main" style="background:var(--max-blue);" onclick="showMan()">כניסת מנהל</button>
        </div>

        <div id="sec-view" class="hidden">
            <div class="lang-bar">
                <button class="btn-lang active" onclick="changeLang('he')">עברית</button>
                <button class="btn-lang" onclick="changeLang('en')">English</button>
                <button class="btn-lang" onclick="changeLang('ru')">Русский</button>
                <button class="btn-lang" onclick="changeLang('ar')">العربية</button>
                <button class="btn-lang" onclick="changeLang('th')">ไทย</button>
            </div>
            <div id="questionsArea"></div>
            <div class="card">
                <div id="validationError" class="error-msg">נא למלא שם ותאריך לידה תקין (DD.MM.YYYY)</div>
                <input type="text" id="candName" placeholder="שם מלא">
                <input type="text" id="candDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" id="submitBtn" onclick="submitQuiz()">שליחה למנהל</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>ניתוח אינטראקציה ושיבוץ</h3>
            <select id="candSelect" onchange="renderInsights()"></select>
            <div id="insightsContainer">
                <div class="insight-card"><span style="color:var(--max-red); font-weight:bold;">אופי המועמד:</span><div id="charBox"></div></div>
                <div class="insight-card" style="border-right-color: var(--max-blue); background: #f0f7ff;"><span style="color:var(--max-blue); font-weight:bold;">פרוטוקול אינטראקציה (מנהל-עובד):</span><div id="interBox"></div></div>
                <div class="insight-card" style="border-right-color: #059669; background: #f0fdf4;"><span style="color:#059669; font-weight:bold;">המלצת שיבוץ:</span><div id="recomBox"></div></div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <select id="deptSelect"><option value="">בחר מחלקה</option><option>פלסטיקה</option><option>ביוטי</option><option>דקורציה</option><option>עונה</option></select>
                <select id="jobSelect"><option value="">בחר תפקיד</option><option>סדרן/ית</option><option>קופאי/ת</option><option>מחסנאי/ת</option></select>
            </div>
            <button class="btn-main" style="background:#059669;" onclick="saveAssignment()">שמירת שיבוץ עובד</button>
            <button onclick="location.reload()" style="background:none; color:gray; border:none; text-decoration:underline; cursor:pointer; margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        const content = {
            he: { title: "MAX - שאלון גיוס", name: "שם מלא", dob: "תאריך לידה (DD.MM.YYYY)", btn: "שליחה למנהל", questions: ["לקוח מבקש עזרה?", "לחץ בצוות?", "לקוח חשוד?", "שינוי מחלקה?", "אין עומס?", "תכונה חשובה?", "צעקות על מחיר?", "מוצר פגום?", "משימה פיזית?", "טעות של עמית?", "הגעה בזמן?", "נוהל חדש?", "חוסר במלאי?", "ביקורת מנהל?", "כסף על הרצפה?"] },
            en: { title: "MAX - Recruitment", name: "Full Name", dob: "Birth Date (DD.MM.YYYY)", btn: "Submit", questions: ["Customer needs help?", "Team pressure?", "Suspicious customer?", "Dept change?", "No rush?", "Key trait?", "Price shouting?", "Damaged product?", "Physical task?", "Peer mistake?", "Punctuality?", "New procedure?", "Out of stock?", "Manager feedback?", "Money on floor?"] },
            ru: { title: "MAX - Тест", name: "ФИО", dob: "Дата рождения", btn: "Отправить", questions: ["Помощь клиенту?", "Давление в команде?", "Подозрительный клиент?", "Смена отдела?", "Нет очереди?", "Главное качество?", "Крик из-за цены?", "Брак?", "Физический труд?", "Ошибка коллеги?", "Пунктуальность?", "Новое правило?", "Нет на складе?", "Критика босса?", "Деньги на полу?"] },
            ar: { title: "MAX - اختبار التوظيف", name: "الاسم الكامل", dob: "تاريخ الميلاد", btn: "إرسال", questions: ["مساعدة زبون؟", "ضغط فريق؟", "زبון مشتبه به؟", "تغيير قسم؟", "لا يوجد زحمة؟", "أهم صفة؟", "صراخ على السعر؟", "منتج تالف؟", "مهمة بدنية؟", "خطأ زميل؟", "الالتزام بالوقت؟", "إجراء جديد؟", "نقص مخزون؟", "نقد المدير؟", "مال على الأرض؟"] },
            th: { title: "MAX - แบบทดสอบ", name: "ชื่อ-นามสกุล", dob: "วันเกิด", btn: "ส่งข้อมูล", questions: ["ช่วยลูกค้า?", "ความกดดัน?", "ลูกค้ามีพิรุธ?", "เปลี่ยนแผนก?", "ร้านว่าง?", "คุณสมบัติสำคัญ?", "ลูกค้าโวยวาย?", "ของเสีย?", "งานหนัก?", "เพื่อนทำผิด?", "ตรงเวลา?", "กฎใหม่?", "ของหมด?", "คำวิจารณ์?", "เจอเงิน?"] }
        };

        function changeLang(l) {
            const c = content[l];
            document.body.dir = (l==='he'||l==='ar') ? 'rtl' : 'ltr';
            document.getElementById('candName').placeholder = c.name;
            document.getElementById('candDob').placeholder = c.dob;
            document.getElementById('submitBtn').innerText = c.btn;
            document.getElementById('questionsArea').innerHTML = c.questions.map((q, i) => `
                <div class="card"><b>${i+1}. ${q}</b><select id="q${i}"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select></div>
            `).join('');
        }

        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); changeLang('he'); }
        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                fetchManagerData();
            } else alert("סיסמה שגויה");
        }

        async function submitQuiz() {
            const name = document.getElementById('candName').value;
            const dob = document.getElementById('candDob').value;
            const dobRegex = /^\d{2}\.\d{2}\.\d{4}$/;

            if(!name || !dobRegex.test(dob)) {
                document.getElementById('validationError').style.display = 'block';
                return;
            }

            const answers = Array.from({length:15}, (_, i) => ({ idx: document.getElementById('q'+i).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
            alert("נשלח בהצלחה"); location.reload();
        }

        async function fetchManagerData() {
            const res = await fetch('/api/get');
            const data = await res.json();
            window.allCandidates = data;
            document.getElementById('candSelect').innerHTML = data.map((c, i) => `<option value="${i}">${c.firstName}</option>`).join('');
            if(data.length > 0) renderInsights();
        }

        function renderInsights() {
            const c = window.allCandidates[document.getElementById('candSelect').value];
            document.getElementById('charBox').innerText = c.full_analysis.character;
            document.getElementById('interBox').innerText = c.full_analysis.interaction;
            document.getElementById('recomBox').innerText = c.full_analysis.recommendation;
        }

        async function saveAssignment() {
            const idx = document.getElementById('candSelect').value;
            await fetch('/api/update', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({index:idx, dept:document.getElementById('deptSelect').value, job:document.getElementById('jobSelect').value})
            });
            alert("שיבוץ עודכן");
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
def get():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/update', methods=['POST'])
def update():
    req = request.json
    with open('data.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    db[int(req['index'])]['dept'] = req['dept']
    db[int(req['index'])]['job'] = req['job']
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
