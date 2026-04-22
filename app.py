import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# פונקציות בסיס נתונים
def load_data():
    if not os.path.exists('candidates.json'):
        with open('candidates.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    try:
        with open('candidates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# שים לב לשימוש ב-Triple Quotes וב-r כדי למנוע את השגיאה מהתמונה שלך
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; direction: rtl; text-align: right; padding: 20px; }
        .card { background: white; max-width: 500px; margin: auto; padding: 25px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; }
        input, button, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; font-size: 16px; }
        button { background: #e31e24; color: white; border: none; font-weight: bold; cursor: pointer; }
        #admin-ui, #manager-ui, #quiz-ui, #success-ui { display: none; }
        .q-item { background: #f8fafc; padding: 10px; border-right: 4px solid #e31e24; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX</h1>
        <p style="text-align:center;">מערכת ניהול וגיוס מועמדים</p>
        
        <div id="login-ui">
            <input type="text" id="u" placeholder="שם משתמש">
            <input type="password" id="p" placeholder="סיסמה">
            <button id="loginBtn">כניסה למערכת</button>
        </div>

        <div id="admin-ui">
            <h3>פרטי מועמד</h3>
            <input type="text" id="cName" placeholder="שם מלא">
            <input type="text" id="cDob" placeholder="תאריך לידה">
            <button id="goQuizBtn">המשך לשאלון</button>
        </div>

        <div id="quiz-ui">
            <h3>שאלון התאמה</h3>
            <div id="qList"></div>
            <button id="sendBtn">שלח למנהל</button>
        </div>

        <div id="success-ui" style="text-align:center;">
            <h2 style="color:green;">נשלח בהצלחה!</h2>
            <button onclick="location.reload()">חזרה</button>
        </div>

        <div id="manager-ui">
            <h3>לוח מנהל</h3>
            <div id="mList">טוען...</div>
            <button onclick="location.reload()" style="background:#555">התנתק</button>
        </div>
    </div>

    <script>
        // פונקציות עזר למניעת שגיאות סינטקס
        const loginBtn = document.getElementById('loginBtn');
        
        loginBtn.addEventListener('click', function() {
            const user = document.getElementById('u').value.trim().toLowerCase();
            const pass = document.getElementById('p').value.trim();
            
            if(user === 'admin' && pass === 'max456') {
                document.getElementById('login-ui').style.display = 'none';
                document.getElementById('admin-ui').style.display = 'block';
            } else if(user === 'manager' && pass === 'max123') {
                document.getElementById('login-ui').style.display = 'none';
                document.getElementById('manager-ui').style.display = 'block';
                loadManagerData();
            } else {
                alert("פרטים שגויים");
            }
        });

        function loadManagerData() {
            fetch('/api/list')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    data.forEach(item => {
                        html += '<div style="border-bottom:1px solid #eee; padding:10px;"><b>' + item.name + '</b><br><small>' + item.ans.join(' | ') + '</small></div>';
                    });
                    document.getElementById('mList').innerHTML = html || "אין נתונים";
                });
        }

        // שאר הפונקציות הוסרו מהבדיקה הזו כדי לוודא שהכניסה עובדת קודם כל
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CONTENT)

@app.route('/api/list')
def get_list():
    return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    d = load_data()
    d.append(request.json)
    save_data(d)
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
