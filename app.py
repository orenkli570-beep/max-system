from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# נתיב לקובץ הנתונים (נשמר בזיכרון זמני כל עוד השרת רץ בחינם)
DATA_FILE = 'candidates.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_CONTENT = '''
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>מערכת גיוס MAX</title>
    <style>
        :root { --max-red: #e31e24; --dark: #1e293b; }
        body { font-family: sans-serif; background: #f8fafc; padding: 20px; direction: rtl; text-align: right; }
        .card { background: white; padding: 30px; border-radius: 15px; max-width: 600px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: var(--max-red); text-align: center; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; }
        button { background: var(--max-red); color: white; font-weight: bold; cursor: pointer; border: none; }
        #admin-section, #manager-section, #success-screen { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #eee; padding: 10px; text-align: right; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX - מערכת גיוס</h1>
        
        <div id="login-section">
            <h3 style="text-align:center;">כניסה</h3>
            <input type="text" id="user" placeholder="שם משתמש">
            <input type="password" id="pass" placeholder="סיסמה">
            <button type="button" onclick="handleLogin()">כניסה למערכת</button>
            <p id="error-msg" style="color:red; display:none; text-align:center;">פרטי כניסה שגויים!</p>
        </div>

        <div id="admin-section">
            <h3>הזנת מועמד (מזכירה)</h3>
            <input type="text" id="fname" placeholder="שם מלא">
            <input type="text" id="dob" placeholder="תאריך לידה">
            <button type="button" onclick="saveCandidate()">שמור ושלח</button>
        </div>

        <div id="manager-section">
            <h3>לוח בקרה (מנהל)</h3>
            <table>
                <thead><tr><th>שם</th><th>תאריך</th></tr></thead>
                <tbody id="list"></tbody>
            </table>
        </div>

        <div id="success-screen">
            <h2 style="color:green;">נשמר בהצלחה!</h2>
            <button onclick="location.reload()">חזרה</button>
        </div>
    </div>

    <script>
        function handleLogin() {
            const u = document.getElementById('user').value.trim().toLowerCase();
            const p = document.getElementById('pass').value.trim();
            
            console.log("Login attempt:", u, p); // לבדיקה בקונסול

            if (u === "admin" && p === "max456") {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('admin-section').style.display = 'block';
            } else if (u === "manager" && p === "max123") {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('manager-section').style.display = 'block';
                loadCandidates();
            } else {
                document.getElementById('error-msg').style.display = 'block';
            }
        }

        async function saveCandidate() {
            const data = {
                name: document.getElementById('fname').value,
                dob: document.getElementById('dob').value
            };
            await fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            document.getElementById('admin-section').style.display = 'none';
            document.getElementById('success-screen').style.display = 'block';
        }

        async function loadCandidates() {
            const res = await fetch('/api/list');
            const data = await res.json();
            const tbody = document.getElementById('list');
            tbody.innerHTML = data.map(c => `<tr><td>\${c.name}</td><td>\${c.dob}</td></tr>`).join('');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

@app.route('/api/list')
def get_list():
    return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    data = load_data()
    data.append(request.json)
    save_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
