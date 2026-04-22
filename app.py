import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- פונקציות עזר (לוגיקה) ---

def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def generate_insights(data):
    num = get_num(data['dob'])
    # בדיקת איכות תשובות (יוזמה)
    is_proactive = sum(1 for a in data['answers'] if a['idx'] == "1") > 10
    
    traits = {
        1: "טיפוס מנהיגותי, דורש מרחב פעולה ועצמאות.",
        2: "טיפוס שירותי מאוד, זקוק לסביבה הרמונית ועבודת צוות.",
        3: "תקשורתי ודינמי, פורח באינטראקציה עם לקוחות.",
        4: "יסודי ומדויק, מעדיף סדר קבוע ונהלים ברורים.",
        5: "זריז וסתגלן, מתאים לשינויים מהירים במשימות.",
        6: "אחראי ומשפחתי, רואה את טובת החנות כערך עליון.",
        7: "מעמיק ושקט, זקוק להוראות ברורות ולא אוהב רעש מיותר.",
        8: "עמיד בלחץ, משימתי מאוד וקר רוח במצבי דוחק.",
        9: "אדיב וסבלני, ניחן ביכולת הקשבה גבוהה ללקוחות קשים.",
        11: "בעל אינטואיציה גבוהה, קורא אנשים ומצבים במהירות.",
        22: "בעל יכולת ביצוע מרשימה, מסוגל להוביל פרויקטים גדולים."
    }
    
    char_desc = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות גבוהה.")
    
    # ניתוח אינטראקציה מנהל-עובד (המלל המקיף)
    interaction = "במפגש היומיומי, המנהל נדרש "
    if is_proactive:
        interaction += "לתת לעובד זה יד חופשית וגיבוי ליוזמות. הוא מזהה צרכים לבד ולא יחכה להוראות, לכן כדאי להגדיר לו יעדים ולא שלבי עבודה. האינטראקציה צריכה להיות בגובה העיניים."
    else:
        interaction += "לספק הנחיות ברורות ומפורטות בתחילת המשמרת. העובד מבצע עבודה טובה מאוד תחת מסגרת ידועה, ומעריך משוב חיובי וביטחון בתפקידו. מומלץ לבצע מעקב תמיכה תקופתי."

    return {
        "character": char_desc,
        "interaction": interaction,
        "recommendation": "שיבוץ אידיאלי: " + ("מחלקות קצה ודינמיות" if is_proactive else "מחלקות שירות יציבות")
    }

# --- HTML & Frontend ---

HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX System 2026</title>
    <style>
        :root { --red: #e31e24; --blue: #1e40af; --bg: #f1f5f9; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); margin: 0; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 4px solid var(--red); }
        .container { max-width: 900px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; }
        .card { background: #fdfdfd; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        .hidden { display: none; }
        .insight-box { padding: 15px; margin: 10px 0; border-right: 5px solid var(--red); background: #fef2f2; }
        .label { font-weight: bold; color: var(--blue); display: block; margin-bottom: 5px; }
        select, input, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; }
        .btn-save { background: #059669; color: white; border: none; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>MAX - ניהול חכם</h1></div>
    <div class="container">
        
        <div id="login-section">
            <input type="password" id="managerPass" placeholder="סיסמת מנהל">
            <button onclick="managerLogin()" style="background:var(--red); color:white;">כניסה לצד מנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניתוח אינטראקציה ואופי</h3>
                <label>מועמד לבחינה:</label>
                <select id="candSelect" onchange="loadManagerInsights()"></select>
                
                <div id="insightsArea">
                    <div class="insight-box">
                        <span class="label">ניתוח אופי עומק:</span>
                        <div id="charText"></div>
                    </div>
                    <div class="insight-box" style="border-right-color: var(--blue); background: #f0f7ff;">
                        <span class="label">פרוטוקול אינטראקציה מנהל-עובד:</span>
                        <div id="interText"></div>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <select id="setDept"><option>פלסטיקה</option><option>ביוטי</option><option>עונה</option></select>
                    <select id="setJob"><option>סדרן/ית</option><option>קופאי/ת</option></select>
                </div>
                <button class="btn-save" onclick="saveAssignment()">שמירה ועדכון שיבוץ</button>
            </div>
        </div>

    </div>

    <script>
        let candidates = [];

        async function managerLogin() {
            if(document.getElementById('managerPass').value === '1234') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('man-section').classList.remove('hidden');
                fetchData();
            }
        }

        async function fetchData() {
            const res = await fetch('/api/get');
            candidates = await res.json();
            const sel = document.getElementById('candSelect');
            sel.innerHTML = candidates.map((c, i) => `<option value="${i}">${c.firstName}</option>`).join('');
            if(candidates.length > 0) loadManagerInsights();
        }

        function loadManagerInsights() {
            const c = candidates[document.getElementById('candSelect').value];
            document.getElementById('charText').innerText = c.insights.character;
            document.getElementById('interText').innerText = c.insights.interaction;
        }

        async function saveAssignment() {
            const idx = document.getElementById('candSelect').value;
            const res = await fetch('/api/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    index: idx,
                    dept: document.getElementById('setDept').value,
                    job: document.getElementById('setJob').value
                })
            });
            if(res.ok) alert("שיבוץ נשמר בהצלחה בעברית");
        }
    </script>
</body>
</html>
"""

# --- API Routes (מונע שגיאות Not Found) ---

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/get', methods=['GET'])
def get_candidates():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/save', methods=['POST'])
def save_candidate():
    data = request.json
    data['insights'] = generate_insights(data) # יצירת הניתוח לפי הפרוטוקול
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    db.append(data)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"status": "success"})

@app.route('/api/update', methods=['POST'])
def update_candidate():
    req = request.json
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
        idx = int(req['index'])
        db[idx]['dept'] = req['dept']
        db[idx]['job'] = req['job']
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
        return jsonify({"status": "updated"})
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
