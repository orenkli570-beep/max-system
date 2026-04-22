import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- מנוע הגילוי הפנימי (צמצום והצלבה) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def check_synergy(p1_dob, p2_dob):
    # חישוב התאמה בין שני אנשים
    n1 = get_num(p1_dob)
    n2 = get_num(p2_dob)
    res = get_num(n1 + n2)
    
    synergy_map = {
        1: "שילוב של כוח וביצוע. מעולה למשימות מהירות.",
        2: "שילוב רגיש. מצוין לשירות לקוחות משותף.",
        4: "שילוב יציב מאוד. מעולה לספירות מלאי וסדר.",
        5: "שילוב תוסס. עלול להיות חוסר שקט אם אין עניין.",
        8: "שילוב הישגי. יעמדו בכל יעד מכירות שתציב.",
        11: "הבנה אינטואיטיבית. עובדים כגוף אחד.",
        22: "צוות עוצמתי. יכולים להרים מחלקה שלמה לבד."
    }
    return synergy_map.get(res, "עבודה זורמת וסטנדרטית.")

# --- ניהול קבצים ---
def get_db(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    return []

def save_db(filename, data):
    db = get_db(filename)
    db.append(data)
    with open(filename, 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)

# --- ממשק HTML ---
HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX - Smart HR & Synergy</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; direction: rtl; margin: 0; padding: 20px; }
        .container { background: white; max-width: 1000px; margin: auto; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; }
        .tabs { display: flex; border-bottom: 2px solid #ddd; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; border: 1px solid transparent; }
        .tab.active { border-bottom: 3px solid #e31e24; font-weight: bold; color: #e31e24; }
        .hidden { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #eee; padding: 12px; text-align: center; }
        .synergy-box { background: #fff3f3; padding: 15px; border-radius: 8px; border: 1px solid #e31e24; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MAX כאן קונים בכיף</h1>
        <h2 style="text-align:center; font-weight:normal;">ניהול הון אנושי וסינרגיית צוות</h2>

        <div id="ui-login">
            <input type="password" id="pass" placeholder="קוד כניסה מנהל/מזכירה" style="width:100%; padding:10px;">
            <button onclick="login()" style="width:100%; padding:10px; margin-top:10px; background:#e31e24; color:white; border:none;">כניסה</button>
        </div>

        <div id="main-ui" class="hidden">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('candidates')">מועמדים חדשים</div>
                <div class="tab" onclick="switchTab('staff')">צוות ותיק</div>
                <div class="tab" onclick="switchTab('synergy')">הצלבת עובדים (סינרגיה)</div>
            </div>

            <div id="tab-candidates">
                <div id="cand-list">טוען נתונים...</div>
            </div>

            <div id="tab-staff" class="hidden">
                <h3>הוספת עובד ותיק למערכת</h3>
                <input type="text" id="sName" placeholder="שם העובד">
                <input type="text" id="sDob" placeholder="תאריך לידה">
                <button onclick="addStaff()">הוסף לצוות</button>
                <hr>
                <div id="staff-list"></div>
            </div>

            <div id="tab-synergy" class="hidden">
                <h3>בדיקת התאמה בין עובדים / מועמדים</h3>
                <p>בחר שני אנשים כדי לבדוק איך הם יעבדו יחד במשמרת:</p>
                <select id="person1"></select>
                <select id="person2"></select>
                <button onclick="checkSynergy()" style="background:black;">בדוק הצלבה</button>
                <div id="synergy-result" class="synergy-box hidden"></div>
            </div>
        </div>
    </div>

    <script>
        let allPeople = [];

        function login() {
            if(document.getElementById('pass').value) {
                document.getElementById('ui-login').classList.add('hidden');
                document.getElementById('main-ui').classList.remove('hidden');
                loadAll();
            }
        }

        function switchTab(t) {
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-candidates').classList.add('hidden');
            document.getElementById('tab-staff').classList.add('hidden');
            document.getElementById('tab-synergy').classList.add('hidden');
            document.getElementById('tab-' + t).classList.remove('hidden');
        }

        async function addStaff() {
            const name = document.getElementById('sName').value;
            const dob = document.getElementById('sDob').value;
            await fetch('/api/add_staff', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name, dob}) });
            loadAll();
        }

        async function loadAll() {
            const res = await fetch('/api/all_data');
            const data = await res.json();
            allPeople = data.combined;
            
            // עדכון רשימות
            let cHtml = '<table><tr><th>שם</th><th>התאמה</th><th>מחלקה</th></tr>';
            data.candidates.forEach(c => {
                cHtml += `<tr><td>${c.name}</td><td>${c.score}%</td><td>${c.dept}</td></tr>`;
            });
            document.getElementById('cand-list').innerHTML = cHtml + '</table>';

            let sHtml = '<ul>';
            data.staff.forEach(s => { sHtml += `<li>${s.name} (${s.dob})</li>`; });
            document.getElementById('staff-list').innerHTML = sHtml + '</ul>';

            // עדכון סלקטים לסינרגיה
            let opts = allPeople.map(p => `<option value="${p.dob}">${p.name}</option>`).join('');
            document.getElementById('person1').innerHTML = opts;
            document.getElementById('person2').innerHTML = opts;
        }

        async function checkSynergy() {
            const dob1 = document.getElementById('person1').value;
            const dob2 = document.getElementById('person2').value;
            const res = await fetch('/api/check_synergy', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({dob1, dob2}) });
            const data = await res.json();
            const box = document.getElementById('synergy-result');
            box.classList.remove('hidden');
            box.innerHTML = `<strong>תוצאת הצלבה:</strong><br>${data.result}`;
        }
    </script>
</body>
</html>
"""

@app.route('/api/add_staff', methods=['POST'])
def add_staff():
    save_db('staff.json', request.json)
    return jsonify({"ok": True})

@app.route('/api/all_data')
def all_data():
    cands = get_db('candidates.json')
    staff = get_db('staff.json')
    return jsonify({
        "candidates": cands,
        "staff": staff,
        "combined": cands + staff
    })

@app.route('/api/check_synergy', methods=['POST'])
def check_syn():
    d = request.json
    result = check_synergy(d['dob1'], d['dob2'])
    return jsonify({"result": result})

# ... (שאר הפונקציות מהקוד הקודם)
