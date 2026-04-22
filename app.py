import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

def load_data():
    if not os.path.exists('candidates.json'): return []
    try:
        with open('candidates.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_data(data):
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# שימוש במשתנה נפרד ל-HTML כדי למנוע שגיאות סינטקס
HTML_TEMPLATE = """
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX System</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; direction: rtl; text-align: right; padding: 20px; }
        .card { background: white; max-width: 600px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; }
        button { background: #e31e24; color: white; border: none; cursor: pointer; font-weight: bold; }
        .lang-bar { display: flex; justify-content: space-around; margin-bottom: 15px; background: #eee; padding: 10px; border-radius: 5px; }
        .lang-bar button { width: auto; padding: 5px 10px; background: #555; font-size: 0.8rem; }
        .q-block { background: #f9f9f9; padding: 10px; margin-bottom: 10px; border-right: 4px solid #e31e24; }
        #admin-section, #manager-section, #success-screen, #questions-section { display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1 style="text-align:center; color:#e31e24;">MAX Recruitment</h1>
        
        <div id="login-section">
            <input type="text" id="user" placeholder="User Name">
            <input type="password" id="pass" placeholder="Password">
            <button onclick="login()">Login / כניסה</button>
        </div>

        <div id="admin-section">
            <div class="lang-bar">
                <button onclick="setL('he')">עברית</button>
                <button onclick="setL('en')">EN</button>
                <button onclick="setL('ru')">RU</button>
                <button onclick="setL('ar')">AR</button>
                <button onclick="setL('fr')">FR</button>
            </div>
            <h3 id="h-details">פרטי מועמד</h3>
            <input type="text" id="fname" placeholder="שם מלא / Full Name">
            <input type="text" id="dob" placeholder="תאריך לידה / DOB">
            <button onclick="showQ()" id="btn-next">המשך לשאלון / Next</button>
        </div>

        <div id="questions-section">
            <h3 id="h-quiz">שאלון התאמה</h3>
            <div id="q-list"></div>
            <button onclick="send()" id="btn-send">שלח למנהל / Send</button>
        </div>

        <div id="success-screen" style="text-align:center;">
            <h2 style="color:green" id="h-success">נשלח בהצלחה!</h2>
            <button onclick="location.reload()">חזרה / Back</button>
        </div>

        <div id="manager-section">
            <h3>לוח מנהל (עברית)</h3>
            <div id="m-list"></div>
            <button onclick="location.reload()" style="background:#555">התנתק / Logout</button>
        </div>
    </div>

    <script>
        let curL = 'he';
        const trans = {
            he: { details: "פרטי מועמד", next: "המשך לשאלון", quiz: "שאלון התאמה", send: "שלח למנהל", success: "נשלח בהצלחה!", q: ["סבלנות?", "צוות?", "לחץ?", "סדר?", "שעות נוספות?"], a: [["גבוהה", "בינונית", "נמוכה"], ["אוהב", "לבד", "תלוי"], ["מצוין", "סביר", "קשה"], ["חשוב", "סביר", "לא"], ["כן", "רק בוקר", "לא"]] },
            en: { details: "Candidate Info", next: "Start Quiz", quiz: "Assessment", send: "Send", success: "Sent Successfully!", q: ["Patience?", "Teamwork?", "Pressure?", "Order?", "Extra hours?"], a: [["High", "Mid", "Low"], ["Love", "Alone", "Depends"], ["Great", "Ok", "Hard"], ["Important", "Ok", "No"], ["Yes", "Morning", "No"]] },
            ru: { details: "Данные", next: "Начать", quiz: "Опрос", send: "Отправить", success: "Успешно!", q: ["Терпение?", "Команда?", "Стресс?", "Порядок?", "Доп. часы?"], a: [["Высокое", "Средне", "Низкое"], ["Люблю", "Один", "Зависит"], ["Отлично", "Ок", "Трудно"], ["Важно", "Ок", "Нет"], ["Да", "Утро", "Нет"]] },
            ar: { details: "تفاصيل", next: "متابعة", quiz: "استביאן", send: "إرسال", success: "تم الإرسال!", q: ["الصبر؟", "فريق؟", "ضغط؟", "نظام؟", "ساعات؟"], a: [["عالي", "متوسط", "منخفض"], ["أحب", "وحدي", "حسب"], ["ممتاز", "عادي", "صعب"], ["مهم", "عادي", "لا"], ["نعم", "صباحا", "لا"]] },
            fr: { details: "Détails", next: "Continuer", quiz: "Quiz", send: "Envoyer", success: "Envoyé!", q: ["Patience?", "Équipe?", "Pression?", "Ordre?", "Heures?"], a: [["Haut", "Moyen", "Bas"], ["J'adore", "Seul", "Dépend"], ["Génial", "Ok", "Dur"], ["Important", "Ok", "Non"], ["Oui", "Matin", "Non"]] }
        };

        function setL(l) {
            curL = l;
            document.getElementById('h-details').innerText = trans[l].details;
            document.getElementById('btn-next').innerText = trans[l].next;
            document.getElementById('h-quiz').innerText = trans[l].quiz;
            document.getElementById('btn-send').innerText = trans[l].send;
            document.getElementById('h-success').innerText = trans[l].success;
        }
        
        function login() {
            const u = document.getElementById('user').value.toLowerCase().trim();
            const p = document.getElementById('pass').value.trim();
            if(u==='admin' && p==='max456') {
                document.getElementById('login-section').style.display='none';
                document.getElementById('admin-section').style.display='block';
            } else if(u==='manager' && p==='max123') {
                document.getElementById('login-section').style.display='none';
                document.getElementById('manager-section').style.display='block';
                loadM();
            } else { alert("Login failed"); }
        }

        function showQ() {
            document.getElementById('admin-section').style.display='none';
            document.getElementById('questions-section').style.display='block';
            const div = document.getElementById('q-list');
            div.innerHTML = trans[curL].q.map((q, i) => `
                <div class="q-block">
                    <label><b>\${q}</b></label>
                    <select id="sel\${i}">\${trans[curL].a[i].map(opt => `<option value="\${opt}">\${opt}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function send() {
            const data = {
                name: document.getElementById('fname').value,
                dob: document.getElementById('dob').value,
                ans: trans[curL].q.map((_, i) => document.getElementById('sel'+i).value)
            };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            document.getElementById('questions-section').style.display='none';
            document.getElementById('success-screen').style.display='block';
        }

        async function loadM() {
            const res = await fetch('/api/list');
            const data = await res.json();
            document.getElementById('m-list').innerHTML = data.map(c => `
                <div style="border-bottom:1px solid #ccc; padding:10px;">
                    <b>\${c.name}</b> (\${c.dob})<br>
                    <small>תשובות: \${c.ans.join(', ')}</small>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/list')
def get_list(): return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    data = load_data()
    data.append(request.json)
    save_data(data)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
