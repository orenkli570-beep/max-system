import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- לוגיקה עסקית: ניתוח עומק מילולי ---

def get_numerology_num(dob):
    if not dob: return 0
    nums = [int(d) for d in dob if d.isdigit()]
    res = sum(nums)
    while res > 9 and res not in [11, 22]:
        res = sum(int(digit) for digit in str(res))
    return res

def generate_full_analysis(data):
    num = get_numerology_num(data.get('dob', ''))
    # ספירת סוגי תשובות (A=יוזמה גבוהה, B=שירותיות, C=צמוד לנהלים, D=ראש קטן)
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    # 1. ניתוח אופי (נומרולוגיה)
    traits = {
        1: "לפניך מועמד בעל אנרגיה של מנהיגות וביצוע עצמאי. הוא לא זקוק למישהו שידחוף אותו; הוא מזהה לבד מה צריך לעשות וניגש למשימה. טיפוס עצמאי מאוד שלא אוהב פיקוח הדוק.",
        2: "מדובר באדם שירותי מאוד, המצטיין בעבודת צוות ובהכלה. הוא זקוק לסביבה אנושית נעימה ופורח כשיש סביבו שיתוף פעולה. עובד נאמן מאוד שרואה את טובת הכלל.",
        3: "מועמד בעל יכולת ביטוי גבוהה ויצירתיות רבה. הוא יודע לפתור בעיות מול לקוחות בצורה מקורית ונעימה, וניחן בקסם אישי שהופך אותו למכירתי ושירותי במיוחד.",
        4: "אדם של סדר, דיוק וארגון מופתי. הוא מצטיין במשימות יסודיות שדורשות תשומת לב לפרטים הקטנים. עובד יציב מאוד שלא נרתע מעבודה שגרתית ומדויקת.",
        5: "מועמד דינמי, זריז ובעל יכולת הסתגלות מהירה לשינויים. הוא נהנה מקצב עבודה גבוה ותנאי לחץ, ויודע לתפקד מצוין בסביבה משתנה שדורשת תנועה רבה.",
        6: "אדם אחראי מאוד, הרמוני ומשפחתי. הוא רואה בחנות את 'הבית השני' שלו ודואג לסביבת עבודה אסתטית ונעימה. מסור מאוד ללקוחות ולחבריו לצוות.",
        7: "מועמד בעל יכולת למידה עצמית גבוהה וריכוז עמוק. הוא לומד נהלים במהירות ומעדיף לעבוד בצורה מחושבת ושקטה. אדם של עומק שאינו פועל בפזיזות.",
        8: "מדובר באדם בעל חוסן מנטלי יוצא דופן. הוא יודע לנהל לחצים כבדים ולעבוד תחת עומס רב מבלי לאבד את העשתונות. טיפוס סמכותי וביצועיסט.",
        9: "אדם בעל ראייה רחבה ורצון אמיתי לעזור לזולת. הוא ניחן בסבלנות רבה מאוד, גם מול הלקוחות הקשים ביותר, ורואה בעבודתו שליחות שירותית.",
        11: "מועמד בעל אינטואיציה חזקה והבנה מהירה של צרכי המנהל והלקוח. הוא קולט מצבים עוד לפני שהם נאמרים ומגיב בהתאם בצורה חכמה.",
        22: "בעל יכולת ביצוע מרשימה במיוחד. אדם שיודע לקחת פרויקטים מורכבים (כמו סידור מחלקה מאפס) ולבצע אותם ברמה הגבוהה ביותר בשטח."
    }
    char_text = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות גבוהה למגוון רחב של משימות בחנות.")

    # 2. פרוטוקול אינטראקציה (מבוסס תשובות)
    if counts['A'] >= 8:
        inter_text = "העובד הפגין יוזמה גבוהה מאוד ('ראש גדול'). המנהל נדרש לתת לו מרחב פעולה ואוטונומיה. הוא יזהה חוסרים במדפים וסידור באופן עצמאי. מומלץ להגדיר לו יעדים כלליים ולתת לו לנהל את הדרך לשם."
        recom = "מחלקות דינמיות הדורשות תקתוק עבודה עצמאי (פלסטיקה, עונה, מחסן)."
    elif counts['B'] >= counts['A'] and counts['B'] >= 8:
        inter_text = "מדובר בביצועיסט שירותי מעולה. הוא יבצע את הוראות המנהל בצורה נאמנה עם חיוך ללקוח. המנהל נדרש לספק לו משוב חיובי ולתת לו תחושה שהוא חלק משמעותי מהצוות."
        recom = "מחלקות שירותיות עם קשר ישיר ללקוח (ביוטי, דקורציה, כלי כתיבה)."
    else:
        inter_text = "העובד זקוק למסגרת עבודה ברורה ולהנחיות מפורטות. המנהל נדרש להגדיר לו משימות שלב-אחרי-שלב בתחילת משמרת ולבצע בקרה נעימה בסופה. הוא מעריך סדר וסמכות ניהולית."
        recom = "מחלקות מובנות הדורשות סדר ודיוק (קופות, כלי מטבח, יצירה)."

    return {"character": char_text, "interaction": inter_text, "recommendation": recom}

# --- ממשק משתמש (HTML) ---

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX Management System</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; --bg: #f8fafc; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); margin: 0; color: #1e293b; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 5px solid var(--max-red); box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .container { max-width: 850px; margin: 25px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
        .hidden { display: none; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; }
        .btn-lang { padding: 10px 18px; cursor: pointer; border: 1px solid #ddd; background: white; border-radius: 25px; font-weight: bold; transition: 0.3s; }
        .btn-lang.active { background: var(--max-red); color: white; border-color: var(--max-red); }
        .card { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 18px; border-radius: 12px; margin-bottom: 15px; }
        .insight-card { padding: 20px; border-radius: 10px; margin-bottom: 20px; border-right: 6px solid var(--max-red); background: #fef2f2; line-height: 1.6; font-size: 1.05em; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 16px; }
        .btn-main { background: var(--max-red); color: white; border: none; font-weight: bold; cursor: pointer; font-size: 1.1em; padding: 15px; }
        .btn-save { background: #059669; color: white; border: none; font-weight: bold; cursor: pointer; }
        h3 { color: var(--max-blue); border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header"><h1>MAX - מערכת קליטה וניהול</h1></div>
    <div class="container">
        
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">כניסת מזכירה (שאלון מועמד)</button>
            <div style="margin-top: 40px; border-top: 1px solid #eee; pt: 20px;">
                <input type="password" id="mPass" placeholder="סיסמת מנהל לניתוח ושיבוץ">
                <button class="btn-main" style="background:var(--max-blue);" onclick="showMan()">כניסת מנהל</button>
            </div>
        </div>

        <div id="sec-view" class="hidden">
            <div class="lang-bar">
                <button class="btn-lang active" onclick="changeLang('he')">עברית</button>
                <button class="btn-lang" onclick="changeLang('en')">English</button>
                <button class="btn-lang" onclick="changeLang('ru')">Русский</button>
                <button class="btn-lang" onclick="changeLang('ar')">العربية</button>
                <button class="btn-lang" onclick="changeLang('th')">ไทย</button>
            </div>
            <div id="quizArea"></div>
            <div class="card">
                <input type="text" id="cName" placeholder="שם מלא">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" onclick="submitQuiz()">שליחת שאלון למנהל</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>פרוטוקול ניתוח ואינטראקציה</h3>
            <select id="candSelect" onchange="render()"></select>
            
            <div id="insArea">
                <div class="insight-card">
                    <b style="color:var(--max-red);">דיוקן אופי המועמד:</b>
                    <div id="cBox" style="margin-top:10px;"></div>
                </div>
                <div class="insight-card" style="border-right-color: var(--max-blue); background: #f0f7ff;">
                    <b style="color:var(--max-blue);">פרוטוקול אינטראקציה (מנהל-עובד):</b>
                    <div id="iBox" style="margin-top:10px;"></div>
                </div>
                <div class="insight-card" style="border-right-color: #059669; background: #f0fdf4;">
                    <b style="color:#059669;">המלצת שיבוץ מנומקת:</b>
                    <div id="rBox" style="margin-top:10px;"></div>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <select id="dSet">
                    <option value="">בחר מחלקה</option>
                    <option>פלסטיקה</option><option>ביוטי</option><option>דקורציה</option>
                    <option>עונה</option><option>כלי מטבח</option><option>יצירה</option>
                </select>
                <select id="jSet">
                    <option value="">בחר תפקיד</option>
                    <option>סדרן/ית</option><option>קופאי/ת</option><option>מחסנאי/ת</option>
                </select>
            </div>
            <button class="btn-save" style="padding:15px; border-radius:8px; margin-top:10px;" onclick="saveAssignment()">שמירת שיבוץ במערכת</button>
            <button onclick="location.reload()" style="background:none; color:gray; border:none; text-decoration:underline; cursor:pointer; margin-top:20px;">התנתק וחזור למסך ראשי</button>
        </div>
    </div>

    <script>
        // בסיס נתונים של שאלות ותשובות (15 שאלות, 4 תשובות לכל אחת)
        const translations = {
            he: {
                q: "לקוח מבקש עזרה בזמן עומס?",
                a1: "אעזור לו מיד בחיוך ואפתור את הבעיה", a2: "אראה לו איפה המוצר ואחזור למשימה שלי", 
                a3: "אבקש ממנו להמתין עד שמישהו יתפנה", a4: "אגיד לו שאני באמצע משימה אחרת",
                name: "שם מלא", dob: "תאריך לידה (DD.MM.YYYY)", btn: "שליחה למנהל"
            },
            en: {
                q: "Customer needs help during rush hour?",
                a1: "Help immediately with a smile", a2: "Show location and return to task",
                a3: "Ask them to wait for someone else", a4: "Say I am busy with another task",
                name: "Full Name", dob: "Birth Date (DD.MM.YYYY)", btn: "Submit"
            },
            ru: {
                q: "Клиенту нужна помощь в час пик?",
                a1: "Помогу сразу с улыбкой", a2: "Покажу где товар и вернусь к работе",
                a3: "Попрошу подождать коллегу", a4: "Скажу что я занят другой задачей",
                name: "ФИО", dob: "Дата рождения", btn: "Отправить"
            },
            ar: {
                q: "زبون يحتاج مساعدة وقت الزحمة؟",
                a1: "أساعده فوراً بابتسامة", a2: "أدله على المكان وأعود لعملي",
                a3: "أطلب منه الانتظار لموظف آخر", a4: "أقول له أنني مشغول بمهمة أخرى",
                name: "الاسم الكامل", dob: "تاريخ الميلاد", btn: "إرسال"
            },
            th: {
                q: "ลูกค้าต้องการความช่วยเหลือขณะร้านยุ่ง?",
                a1: "ช่วยเหลือทันทีด้วยรอยยิ้ม", a2: "บอกตำแหน่งสินค้าแล้วกลับไปทำงาน",
                a3: "บอกให้รอพนักงานคนอื่น", a4: "บอกว่ากำลังยุ่งกับงานอื่น",
                name: "ชื่อ-นามสกุล", dob: "วันเกิด", btn: "ส่งข้อมูล"
            }
        };

        function changeLang(l) {
            const lang = translations[l];
            document.body.dir = (l==='he'||l==='ar') ? 'rtl' : 'ltr';
            document.getElementById('cName').placeholder = lang.name;
            document.getElementById('cDob').placeholder = lang.dob;
            
            let html = "";
            for(let i=1; i<=15; i++) {
                html += `<div class="card">
                    <b>${i}. ${lang.q}</b>
                    <select id="q${i}">
                        <option value="A">${lang.a1}</option>
                        <option value="B">${lang.a2}</option>
                        <option value="C">${lang.a3}</option>
                        <option value="D">${lang.a4}</option>
                    </select>
                </div>`;
            }
            document.getElementById('quizArea').innerHTML = html;
            document.querySelectorAll('.btn-lang').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }

        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); changeLang('he'); }
        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                const r = await fetch('/api/get'); 
                window.cands = await r.json();
                document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
                if(window.cands.length > 0) render();
            } else alert("סיסמה שגויה");
        }

        async function submitQuiz() {
            const name = document.getElementById('cName').value;
            const dob = document.getElementById('cDob').value;
            if(!name || !dob) return alert("נא למלא שם ותאריך לידה");
            const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+(i+1)).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
            alert("השאלון נשלח בהצלחה!"); location.reload();
        }

        function render() {
            const c = window.cands[document.getElementById('candSelect').value];
            document.getElementById('cBox').innerText = c.full_analysis.character;
            document.getElementById('iBox').innerText = c.full_analysis.interaction;
            document.getElementById('rBox').innerText = c.full_analysis.recommendation;
        }

        async function saveAssignment() {
            const idx = document.getElementById('candSelect').value;
            await fetch('/api/update', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({index:idx, dept:document.getElementById('dSet').value, job:document.getElementById('jSet').value})
            });
            alert("השיבוץ נשמר במערכת!");
        }
    </script>
</body>
</html>
"""

# --- Routes API ---

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
    d['dept'] = ""
    d['job'] = ""
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
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/update', methods=['POST'])
def update():
    req = request.json
    with open('data.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    idx = int(req['index'])
    db[idx]['dept'] = req['dept']
    db[idx]['job'] = req['job']
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
