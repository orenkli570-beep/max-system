from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

# נתיב לקובץ הנתונים - זה מה שיאפשר לשני המחשבים לראות את אותו מידע
DATA_FILE = '/data/candidates.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    # יצירת התיקייה במידה והיא לא קיימת (עבור הדיסק של רנדר)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# כאן נמצא כל העיצוב והשאלון של המערכת
HTML_CONTENT = '''
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>מערכת גיוס MAX | הגילוי הפנימי</title>
    <style>
        :root { --max-red: #e31e24; --dark: #1e293b; --bg: #f8fafc; }
        body { font-family: sans-serif; background: var(--bg); padding: 20px; direction: rtl; text-align: right; }
        .card { background: white; padding: 30px; border-radius: 15px; max-width: 700px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: var(--max-red); text-align: center; border-bottom: 2px solid var(--max-red); padding-bottom: 10px; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 1rem; box-sizing: border-box; }
        button { background: var(--max-red); color: white; font-weight: bold; cursor: pointer; border: none; transition: 0.3s; }
        button:hover { opacity: 0.8; }
        .q-box { margin-bottom: 15px; padding: 10px; background: #fff; border: 1px solid #eee; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #eee; padding: 12px; text-align: right; }
        th { background: var(--dark); color: white; }
        #admin-section, #manager-section, #success-screen { display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX - גיוס והתאמה</h1>
        
        <div id="login-section">
            <h3 style="text-align:center;">כניסה למערכת</h3>
            <input type="text" id="user" placeholder="שם משתמש (admin/manager)">
            <input type="password" id="pass" placeholder="סיסמה">
            <button onclick="login()">כניסה</button>
        </div>

        <div id="admin-section">
            <h3>שלב 1: פרטי מועמד</h3>
            <input type="text" id="fname" placeholder="שם מלא">
            <input type="text" id="dob" placeholder="תאריך לידה (למשל 12/05/1990)">
            <hr>
            <h3>שלב 2: שאלון התאמה</h3>
            <div id="questions-container"></div>
            <button onclick="saveCandidate()">שלח נתונים למנהל</button>
        </div>

        <div id="success-screen" style="text-align:center;">
            <h2 style="color:green;">✓ הנתונים נשמרו!</h2>
            <p>המידע עבר למנהל בהצלחה.</p>
            <button onclick="location.reload()" style="background:#1e293b;">הזן מועמד חדש</button>
        </div>

        <div id="manager-section">
            <h3>לוח בקרה לניהול וניתוח</h3>
            <table>
                <thead>
                    <tr>
                        <th>שם המועמד</th>
                        <th>תאריך לידה</th>
                        <th>פעולות</th>
                    </tr>
                </thead>
                <tbody id="candidates-list"></tbody>
            </table>
            <button onclick="location.reload()" style="background:#64748b; margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        const questions = [
            "איך היית מגדיר/ה את הסבלנות שלך מ-1 עד 10?",
            "האם את/ה מעדיף/ה עבודה בצוות או לבד?",
            "איך את/ה מגיב/ה ללקוח כועס?",
            "מה רמת הסדר והארגון שלך?",
            "האם את/ה זמין/ה למשמרות לילה?",
            "איך את/ה מתמודד/ה עם שינויים בלו''ז?",
            "מהי התכונה הכי חזקה שלך?",
            "האם עבודה פיזית מתאימה לך?",
            "למה בחרת לעבוד דווקא ב-MAX?",
            "איפה את/ה רואה את עצמך בעוד שנה?"
        ];

        function login() {
            const u = document.getElementById('user').value;
            const p = document.getElementById('pass').value;
            // הגדרת סיסמאות פשוטות
            if(u === 'admin' && p === 'max456') {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('admin-section').style.display = 'block';
                renderQuestions();
            } else if(u === 'manager' && p === 'max123') {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('manager-section').style.display = 'block';
                fetchCandidates();
            } else { alert('שם משתמש או סיסמה שגויים'); }
        }

        function renderQuestions() {
            const container = document.getElementById('questions-container');
            container.innerHTML = questions.map((q, i) => `
                <div class="q-box">
                    <label><b>\${i+1}. \${q}</b></label>
                    <select id="q\${i}">
                        <option value="גבוהה">גבוהה / מתאים מאוד</option>
                        <option value="בינונית">בינונית / סביר</option>
                        <option value="נמוכה">נמוכה / פחות מתאים</option>
                    </select>
                </div>
            `).join('');
        }

        async function saveCandidate() {
            const name = document.getElementById('fname').value;
            const dob = document.getElementById('dob').value;
            if(!name || !dob) { alert("נא למלא שם ותאריך לידה"); return; }

            const payload = {
                name: name,
                dob: dob,
                answers: questions.map((q, i) => ({ question: q, answer: document.getElementById('q'+i).value }))
            };

            const response = await fetch('/api/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            if(response.ok) {
                document.getElementById('admin-section').style.display = 'none';
                document.getElementById('success-screen').style.display = 'block';
            }
        }

        async function fetchCandidates() {
            const res = await fetch('/api/list');
            const data = await res.json();
            const list = document.getElementById('candidates-list');
            list.innerHTML = data.map(c => `
                <tr>
                    <td>\${c.name}</td>
                    <td>\${c.dob}</td>
                    <td><button style="width:auto; padding:5px 10px;" onclick="viewDetail('\${c.name}', \${JSON.stringify(c.answers)})">נתח</button></td>
                </tr>
            `).join('');
        }

        function viewDetail(name, answers) {
            let msg = "ניתוח תשובות עבור: " + name + "\\n\\n";
            answers.forEach(a => msg += a.question + ": " + a.answer + "\\n");
            alert(msg);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

@app.route('/api/list', methods=['GET'])
def get_list():
    return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    data = load_data()
    data.append(request.json)
    save_data(data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # הרצה בפורט שרנדר מספק או 5000 כברירת מחדל
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
