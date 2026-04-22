import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

# --- לוגיקת ניתוח (פרוטוקול אורן) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def deep_analysis(data):
    num = get_num(data['dob'])
    traits = {
        1: "מנהיגות וביצוע", 2: "שירות והכלה", 3: "יצירתיות וחיוך", 
        4: "סדר ודיוק", 5: "דינמיות וזריזות", 6: "אחריות ושירות", 
        7: "ריכוז ועומק", 8: "חוסן וניהול", 9: "נדיבות וראייה רחבה",
        11: "אינטואיציה", 22: "ביצוע פרויקטים"
    }
    trait = traits.get(num, "ורסטילי")
    res = f"מועמד בעל תדר {num} ({trait}). "
    res += "ניתוח הצלבה מראה התאמה למחלקות שירותיות ואסתטיות. מומלץ להימנע משיבוץ במחלקות אינטנסיביות ללא חפיפה צמודה."
    return res

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
        .container { max-width: 1100px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; }
        .hidden { display: none; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 16px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .btn-update { background: #10b981; color: white; border: none; font-weight: bold; cursor: pointer; margin-top: 5px; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .analysis-text { background: #fff3f3; padding: 15px; border-radius: 8px; border-right: 5px solid var(--red); line-height: 1.6; font-weight: bold; white-space: pre-wrap; }
        .inter-box { color: #2563eb; font-weight: bold; text-align: center; margin: 10px 0; font-size: 22px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background-color: #f1f5f9; }
        .status-tag { padding: 4px 8px; border-radius: 4px; font-size: 13px; font-weight: bold; background: #e2e8f0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MAX – ניהול ושיבוץ עובדים</h1>
    </div>

    <div class="container">
        <div id="login-section">
            <input type="text" id="username" placeholder="שם משתמש">
            <input type="password" id="password" placeholder="סיסמה">
            <button class="btn-main" onclick="login()">כניסה למערכת</button>
        </div>

        <div id="sec-section" class="hidden">
            <h3>שאלון מועמד חדש</h3>
            <input type="text" id="firstName" placeholder="שם פרטי">
            <input type="text" id="dob" placeholder="תאריך לידה (DD.MM.YYYY)">
            <button class="btn-main" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>מרכז ניתוח ושיבוץ</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label>מחלקה:</label>
                        <select id="editDept">
                            <option>טרם שובץ</option>
                            <option>פלסטיקה</option><option>חד פעמי</option><option>כלי עבודה</option>
                            <option>כלי מטבח</option><option>טקסטיל</option><option>דקורציה</option>
                            <option>צעצועים</option><option>יצירה</option><option>ביוטי</option>
                            <option>כלי כתיבה</option><option>סלולר</option><option>עונה</option>
                        </select>
                    </div>
                    <div>
                        <label>תפקיד:</label>
                        <select id="editJob">
                            <option>טרם שובץ</option>
                            <option>מנהל</option><option>סגן מנהל</option><option>אחראי מחלקה</option>
                            <option>סדרן</option><option>קופאית</option><option>מחסנאי</option>
                        </select>
                    </div>
                </div>
                <button class="btn-update" onclick="updateAssignment()">עדכן שיבוץ במערכת</button>
                
                <div id="managerInter" class="inter-box"></div>
                <div id="fullAnalysis" class="analysis-text"></div>
            </div>

            <div class="card">
                <h3>רשימת עובדים פעילה</h3>
                <table>
                    <thead>
                        <tr>
                            <th>שם העובד</th>
                            <th>תאריך לידה</th>
                            <th>מחלקה</th>
                            <th>תפקיד</th>
                        </tr>
                    </thead>
                    <tbody id="staffBody"></tbody>
                </table>
            </div>
            
            <button onclick="location.reload()" style="background:none; border:none; text-decoration:underline; cursor:pointer; color:gray;">התנתק</button>
        </div>
    </div>

    <script>
        function login() {
            const u = document.getElementById('username').value;
            const p = document.getElementById('password').value;
            if(u === 'secretary' && p === 'max123') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('sec-section').classList.remove('hidden');
            } else if(u === 'manager' && p === 'admin456') {
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('man-section').classList.remove('hidden');
                loadManager();
            }
        }

        async function submitForm() {
            const data = {
                firstName: document.getElementById('firstName').value,
                dob: document.getElementById('dob').value,
                dept: "טרם שובץ",
                job: "טרם שובץ",
                answers: []
            };
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
            alert("מועמד נוסף בהצלחה!"); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            
            document.getElementById('selCand').innerHTML = data.map((c, i) => `<option value='${i}'>${c.firstName}</option>`).join('');
            
            const tableBody = data.map(c => `
                <tr>
                    <td><b>${c.firstName}</b></td>
                    <td>${c.dob}</td>
                    <td><span class="status-tag">${c.dept || '---'}</span></td>
                    <td><span class="status-tag">${c.job || '---'}</span></td>
                </tr>
            `).join('');
            document.getElementById('staffBody').innerHTML = tableBody;
            
            runAnalysis();
        }

        async function runAnalysis() {
            const idx = document.getElementById('selCand').value;
            const res = await fetch('/api/get');
            const data = await res.json();
            const cand = data[idx];
            
            document.getElementById('managerInter').innerText = "אינטראקציה מול מנהל: " + (80 + (cand.num % 15)) + "%";
            document.getElementById('fullAnalysis').innerText = cand.analysis;
            document.getElementById('editDept').value = cand.dept || "טרם שובץ";
            document.getElementById('editJob').value = cand.job || "טרם שובץ";
        }

        async function updateAssignment() {
            const idx = document.getElementById('selCand').value;
            const newDept = document.getElementById('editDept').value;
            const newJob = document.getElementById('editJob').value;
            
            await fetch('/api/update', { 
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({ index: idx, dept: newDept, job: newJob })
            });
            alert("השיבוץ עודכן ונשמר!");
            loadManager();
        }
    </script>
</body>
</html>
"""

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['num'] = get_num(d['dob'])
    d['analysis'] = deep_analysis(d)
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
    idx = int(req['index'])
    with open('data.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    db[idx]['dept'] = req['dept']
    db[idx]['job'] = req['job']
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
