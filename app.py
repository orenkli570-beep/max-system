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
    proactive_score = sum(1 for a in data.get('answers', []) if a['val'] == "A")
    
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
    
    if proactive_score >= 8:
        inter_text = "העובד הפגין רמת יוזמה גבוהה מאוד בתשובותיו. המנהל נדרש לתת לו מרחב פעולה ואוטונומיה. הוא יזהה חוסרים במדפים וניקיון באופן עצמאי. מומלץ לנהל אותו דרך הגדרת יעדים ולא דרך פיקוח הדוק על כל פעולה."
        recom = "מחלקות דינמיות: פלסטיקה, עונה, מחסן."
    else:
        inter_text = "העובד זקוק למסגרת עבודה מוגדרת היטב. המנהל נדרש לתת הנחיות ברורות בתחילת משמרת ולבצע בקרה נעימה. העובד יבצע עבודה נאמנה ומדויקת כל עוד הוא יודע בדיוק מה מצופה ממנו."
        recom = "מחלקות שירותיות: ביוטי, דקורציה, כלי כתיבה."

    return {"character": char_text, "interaction": inter_text, "recommendation": recom}

# --- ממשק משתמש (HTML) ---

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; --bg: #f1f5f9; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); margin: 0; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 5px solid var(--max-red); }
        .container { max-width: 800px; margin: 20px auto; background: white; padding: 20px; border-radius: 12px; }
        .hidden { display: none; }
        .lang-bar { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; }
        .btn-lang { padding: 6px 12px; cursor: pointer; border: 1px solid #ddd; background: white; border-radius: 15px; font-size: 14px; }
        .btn-lang.active { background: var(--max-red); color: white; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
        .insight-box { padding: 15px; border-radius: 8px; margin-bottom: 15px; border-right: 5px solid var(--max-red); background: #fef2f2; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; border-radius: 6px; border: 1px solid #ccc; font-size: 15px; }
        .btn-main { background: var(--max-red); color: white; border: none; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>MAX - מערכת קליטה</h1></div>
    <div class="container">
        
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">שאלון מועמד</button>
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
            <div id="quizArea"></div>
            <div class="card">
                <input type="text" id="cName" placeholder="שם מלא">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" onclick="submitQuiz()">שליחה למנהל</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>ניתוח ושיבוץ מועמדים</h3>
            <select id="candSelect" onchange="render()"></select>
            <div id="insArea">
                <div class="insight-box"><b>אופי:</b> <div id="cBox"></div></div>
                <div class="insight-box" style="border-right-color:var(--max-blue); background:#f0f7ff;"><b>אינטראקציה:</b> <div id="iBox"></div></div>
                <div class="insight-box" style="border-right-color:#059669; background:#f0fdf4;"><b>שיבוץ:</b> <div id="rBox"></div></div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <select id="dSet"><option>פלסטיקה</option><option>ביוטי</option><option>עונה</option></select>
                <select id="jSet"><option>סדרן/ית</option><option>קופאי/ת</option></select>
            </div>
            <button class="btn-main" style="background:#059669;" onclick="save()">שמירה</button>
        </div>
    </div>

    <script>
        const db = {
            he: { q: "לקוח זקוק לעזרה?", a1: "אעזור לו מיד בחיוך", a2: "אפנה אותו לעובד אחר" },
            en: { q: "Customer needs help?", a1: "Help immediately with a smile", a2: "Refer to another staff member" },
            ru: { q: "Нужна помощь клиенту?", a1: "Помогу с улыбкой", a2: "Направлю к коллеге" },
            ar: { q: "زبون يحتاج مساعدة؟", a1: "أساعده فوراً بابتسامة", a2: "أوجهه لموظף אחר" },
            th: { q: "ลูกค้าต้องการความช่วยเหลือ?", a1: "ช่วยเหลือทันทีด้วยรอยยิ้ม", a2: "ส่งต่อให้พนักงานคนอื่น" }
        };

        function changeLang(l) {
            const lang = db[l];
            document.body.dir = (l==='he'||l==='ar') ? 'rtl' : 'ltr';
            let html = "";
            for(let i=1; i<=15; i++) {
                html += `<div class="card"><b>${i}. ${lang.q}</b>
                <select id="q${i}"><option value="A">${lang.a1}</option><option value="B">${lang.a2}</option></select></div>`;
            }
            document.getElementById('quizArea').innerHTML = html;
        }

        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); changeLang('he'); }
        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                const r = await fetch('/api/get'); window.cands = await r.json();
                document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
                render();
            }
        }

        async function submitQuiz() {
            const name = document.getElementById('cName').value;
            const dob = document.getElementById('cDob').value;
            if(!name || !dob) return alert("נא למלא פרטים");
            const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+(i+1)).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
            alert("נשלח!"); location.reload();
        }

        function render() {
            const c = window.cands[document.getElementById('candSelect').value];
            document.getElementById('cBox').innerText = c.full_analysis.character;
            document.getElementById('iBox').innerText = c.full_analysis.interaction;
            document.getElementById('rBox').innerText = c.full_analysis.recommendation;
        }

        async function save() { alert("נשמר במערכת"); }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save_data():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
    db_list = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: db_list = json.load(f)
    db_list.append(d)
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(db_list, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
