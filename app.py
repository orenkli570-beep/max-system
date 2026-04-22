import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- רשימות המערכת המעודכנות ---
DEPARTMENTS = [
    "פלסטיקה", "ביוטי", "דקורציה", "עונה", "כלי מטבח", "יצירה", 
    "צעצועים", "טקסטיל", "ניקיון", "חזרה לבית הספר", "מחסן", "חשמל", "קופות"
]

ROLES = [
    "סדרן/ית", "קופאי/ת", "מחסנאי/ת", "סגן/ית מנהל", "אחראי/ת משמרת", 
    "אחראי/ת מחלקה", "מלגזן/ית", "עובד/ת ניקיון", "נציג/ת שירות", 
    "בודק/ת חשבוניות", "אחראי/ת החזרות", "סופר/ת מלאי", "מתפעל/ת מבצעים",
    "עובד/ת לילה", "תומך/ת טכני"
]

# --- לוגיקה: ניתוח עומק מילולי מורחב ---
def get_numerology_num(dob):
    if not dob: return 0
    nums = [int(d) for d in dob if d.isdigit()]
    res = sum(nums)
    while res > 9 and res not in [11, 22]:
        res = sum(int(digit) for digit in str(res))
    return res

def generate_full_analysis(data):
    num = get_numerology_num(data.get('dob', ''))
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    # ניתוח אופי בסיסי
    traits = {
        1: "מוביל טבעי, עצמאי מאוד.", 4: "יסודי, דייקן, אוהב סדר.", 
        8: "חוסן מנטלי גבוה, עומד בלחץ.", 5: "דינמי, מהיר, מסתגל."
    }
    char_base = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות.")

    # ניתוח אינטראקציה חברתית (בין עובדים)
    if counts['A'] + counts['B'] >= 10:
        social_text = "עובד חברותי מאוד, מהווה 'דבק' בצוות. הוא יסייע לאחרים מיוזמתו וידע למנוע חיכוכים בתוך המחלקה."
    else:
        social_text = "עובד משימתי וממוקד מטרה. הוא מעדיף לעבוד לבד בשקט ופחות לעסוק באינטראקציה חברתית בזמן העבודה."

    # אינטראקציה מול מנהל (איך לנהל אותו)
    if counts['A'] >= 8:
        manager_text = "תן לו אוטונומיה. הוא יפרח אם תטיל עליו משימה ותשחרר. דבר איתו בגובה העיניים, הוא מעריך אמון."
    else:
        manager_text = "היה סמכותי וברור. הוא זקוק להנחיות כתובות או מילוליות מדויקות. אל תשאיר לו 'שטחים אפורים'."

    return {
        "character": char_base,
        "social": social_text,
        "manager_protocol": manager_text,
        "recommendation": "מותאם אישית לפי הפרוטוקול לעיל."
    }

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX Management PRO</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; }
        body { font-family: 'Segoe UI', sans-serif; background: #f1f5f9; margin: 0; }
        .container { max-width: 900px; margin: 20px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card { background: #f8fafc; border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        .insight-card { padding: 15px; border-radius: 8px; margin-bottom: 15px; border-right: 5px solid var(--max-red); background: #fff1f2; }
        .header { background: var(--max-red); color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 24px; }
        select, input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }
        .btn-main { background: var(--max-red); color: white; border: none; cursor: pointer; font-weight: bold; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="header">מערכת ניהול MAX - פרוטוקול מורחב</div>
    <div class="container">
        
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">כניסת מזכירה</button>
            <input type="password" id="mPass" placeholder="סיסמת מנהל" style="margin-top:20px;">
            <button class="btn-main" style="background:var(--max-blue);" onclick="showMan()">כניסת מנהל</button>
        </div>

        <div id="sec-view" class="hidden">
            <div id="quizArea"></div>
            <input type="text" id="cName" placeholder="שם המועמד">
            <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <button class="btn-main" onclick="submitQuiz()">שליחה</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>ניתוח מועמד ושיבוץ</h3>
            <select id="candSelect" onchange="render()"></select>
            <div id="insArea">
                <div class="insight-card"><b>אופי:</b> <div id="cBox"></div></div>
                <div class="insight-card" style="border-color:var(--max-blue);"><b>אינטראקציה בין עובדים:</b> <div id="sBox"></div></div>
                <div class="insight-card" style="border-color:orange;"><b>אינטראקציה עובד-מנהל:</b> <div id="mBox"></div></div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                <select id="dSet">""" + "".join([f"<option>{d}</option>" for d in DEPARTMENTS]) + """</select>
                <select id="jSet">""" + "".join([f"<option>{r}</option>" for r in ROLES]) + """</select>
            </div>
            <button class="btn-main" style="background:green;">שמירת שיבוץ סופי</button>
        </div>
    </div>

    <script>
        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); renderQuiz(); }
        function renderQuiz() {
            let h = "";
            for(let i=1; i<=15; i++) {
                h += `<div class="card"><b>שאלה ${i}: מה תעשה בסיטואציה...?</b>
                <select id="q${i}"><option value="A">אופציה א'</option><option value="B">אופציה ב'</option><option value="C">אופציה ג'</option><option value="D">אופציה ד'</option></select></div>`;
            }
            document.getElementById('quizArea').innerHTML = h;
        }
        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                const r = await fetch('/api/get'); window.cands = await r.json();
                document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
                if(window.cands.length > 0) render();
            }
        }
        function render() {
            const c = window.cands[document.getElementById('candSelect').value];
            document.getElementById('cBox').innerText = c.full_analysis.character;
            document.getElementById('sBox').innerText = c.full_analysis.social;
            document.getElementById('mBox').innerText = c.full_analysis.manager_protocol;
        }
        async function submitQuiz() {
            const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+(i+1)).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:document.getElementById('cName').value, dob:document.getElementById('cDob').value, answers}) });
            alert("נשלח!"); location.reload();
        }
    </script>
</body>
</html>
"""

# --- Routes API (זהה לגרסאות קודמות) ---
@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
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
    app.run(debug=True, port=5000)
