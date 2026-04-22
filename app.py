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

HTML_CONTENT = """
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX - מערכת גיוס</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; direction: rtl; text-align: right; padding: 20px; margin: 0; }
        .card { background: white; max-width: 600px; margin: 20px auto; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; margin-bottom: 5px; font-size: 2.2rem; }
        h2 { color: #475569; text-align: center; margin-top: 0; font-size: 1.1rem; font-weight: normal; margin-bottom: 25px; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; font-size: 16px; }
        button { background: #e31e24; color: white; border: none; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #b91c1c; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .lang-bar button { width: auto; padding: 8px 15px; background: #64748b; font-size: 13px; }
        .lang-bar button.active { background: #e31e24; }
        .q-box { background: #f8fafc; padding: 15px; border-right: 5px solid #e31e24; margin-bottom: 12px; border-radius: 6px; }
        #admin-ui, #manager-ui, #success-ui, #quiz-ui { display: none; }
        .m-item { border-bottom: 1px solid #eee; padding: 15px; }
        .m-item b { color: #e31e24; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX</h1>
        <h2>מערכת ניהול וגיוס מועמדים</h2>
        
        <div id="login-ui">
            <input type="text" id="userInput" placeholder="שם משתמש">
            <input type="password" id="passInput" placeholder="סיסמה">
            <button onclick="login()">כניסה למערכת</button>
        </div>

        <div id="admin-ui">
            <div class="lang-bar">
                <button onclick="setL('he')" id="btn-he" class="active">עברית</button>
                <button onclick="setL('en')" id="btn-en">English</button>
                <button onclick="setL('ru')" id="btn-ru">Русский</button>
                <button onclick="setL('ar')" id="btn-ar">العربية</button>
                <button onclick="setL('fr')" id="btn-fr">Français</button>
            </div>
            <h3 id="t-details">פרטי מועמד</h3>
            <input type="text" id="c_name" placeholder="שם מלא / Full Name">
            <input type="text" id="c_dob" placeholder="תאריך לידה / DOB">
            <button onclick="openQuiz()" id="btn-next">המשך לשאלון התאמה</button>
        </div>

        <div id="quiz-ui">
            <h3 id="t-quiz">שאלון התאמה</h3>
            <div id="questions-list"></div>
            <button onclick="submitData()" id="btn-send">שלח נתונים למנהל</button>
        </div>

        <div id="success-ui" style="text-align:center;">
            <h2 style="color:green; font-weight:bold;">✓ השאלון נשלח בהצלחה!</h2>
            <p>הנתונים נשמרו במערכת עבור המנהל.</p>
            <button onclick="location.reload()">חזרה לתפריט כניסה</button>
        </div>

        <div id="manager-ui">
            <h3>לוח בקרה - מועמדים שנקלטו</h3>
            <div id="manager-results">טוען נתונים...</div>
            <button onclick="location.reload()" style="background:#475569; margin-top:20px;">התנתק מהמערכת</button>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const dictionary = {
            he: { details: "פרטי מועמד", next: "המשך לשאלון התאמה", quiz: "שאלון התאמה", send: "שלח נתונים למנהל",
                q: ["סבלנות?", "צוות?", "לחץ?", "סדר?", "משמרות?", "יוזמה?", "שירות?", "זמנים?", "פיזי?", "למה MAX?"],
                a: [["גבוהה","בינונית","נמוכה"],["צוות","לבד","תלוי"],["טוב מאוד","סביר","קשה"],["חשוב","סביר","לא"],["מלאה","חלקית","בוקר"],["יוזם","מבצע","צריך הנחיה"],["סבלני","מנהל","מתעלם"],["דייקן","משתדל","מאחר"],["מתאים","סביר","לא"],["יציבות","שכר","עניין"]] },
            en: { details: "Candidate Info", next: "Continue to Quiz", quiz: "Assessment", send: "Submit to Manager",
                q: ["Patience?", "Teamwork?", "Pressure?", "Order?", "Shifts?", "Initiative?", "Service?", "Punctuality?", "Physical?", "Why MAX?"],
                a: [["High","Mid","Low"],["Team","Alone","Depends"],["Great","Ok","Hard"],["Important","Ok","No"],["Full","Part","Morning"],["Proactive","Doer","Guidance"],["Patient","Manager","Ignore"],["Punctual","Trying","Late"],["Fit","Ok","No"],["Stability","Salary","Interest"]] },
            ru: { details: "Данные", next: "Далее", quiz: "Опрос", send: "Отправить",
                q: ["Терпение?", "Команда?", "Стресс?", "Порядок?", "Смены?", "Инициатива?", "Сервис?", "Время?", "Физ. труд?", "Почему MAX?"],
                a: [["Высокое","Среднее","Низкое"],["Команда","Один","Зависит"],["Отлично","Ок","Трудно"],["Важно","Ок","Нет"],["Полная","Часть","Утро"],["Сам","Делаю","Нужна помощь"],["Терпелив","Босс","Игнор"],["Вовремя","Стараюсь","Опаздываю"],["Подходит","Ок","Нет"],["Стабильность","Зарплата","Интерес"]] },
            ar: { details: "تفاصيل", next: "متابعة", quiz: "استبيان", send: "إرسال",
                q: ["الصبر؟", "فريق؟", "ضغط؟", "نظام؟", "وردية؟", "مبادرة؟", "زبائن؟", "دقة؟", "عمل جسدي؟", "لماذا MAX؟"],
                a: [["عالي","متوسط","منخفض"],["فريق","وحدي","حسب"],["ممتاز","عادي","صعب"],["مهم","عادي","لا"],["كاملة","جزئية","صباحا"],["מבادر","منفذ","توجيه"],["صبور","مدير","تجاهל"],["دقيق","أחاول","أتأخر"],["يناسب","عادي","לא"],["استقرار","راتب","اهتمام"]] },
            fr: { details: "Détails", next: "Suivant", quiz: "Quiz", send: "Envoyer",
                q: ["Patience?", "Equipe?", "Pression?", "Ordre?", "Horaires?", "Initiative?", "Service?", "Ponctualité?", "Physique?", "Pourquoi MAX?"],
                a: [["Haute","Moyenne","Basse"],["Equipe","Seul","Depend"],["Super","Ok","Dur"],["Important","Ok","Non"],["Plein","Partiel","Matin"],["Proactif","Executant","Besoin d'aide"],["Patient","Chef","Ignorer"],["Ponctuel","Essaye","Retard"],["Adapte","Ok","Non"],["Stabilite","Salaire","Interet"]] }
        };

        function setL(l) {
            currentLang = l;
            document.querySelectorAll('.lang-bar button').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + l).classList.add('active');
            document.getElementById('t-details').innerText = dictionary[l].details;
            document.getElementById('btn-next').innerText = dictionary[l].next;
            document.getElementById('t-quiz').innerText = dictionary[l].quiz;
            document.getElementById('btn-send').innerText = dictionary[l].send;
        }

        function login() {
            const u = document.getElementById('userInput').value.trim().toLowerCase();
            const p = document.getElementById('passInput').value.trim();
            if(u === 'admin' && p === 'max456') {
                document.getElementById('login-ui').style.display = 'none';
                document.getElementById('admin-ui').style.display = 'block';
            } else if(u === 'manager' && p === 'max123') {
                document.getElementById('login-ui').style.display = 'none';
                document.getElementById('manager-ui').style.display = 'block';
                fetchManagerData();
            } else {
                alert("שם משתמש או סיסמה שגויים!");
            }
        }

        function openQuiz() {
            if(!document.getElementById('c_name').value) return alert("נא להזין שם מועמד");
            document.getElementById('admin-ui').style.display = 'none';
            document.getElementById('quiz-ui').style.display = 'block';
            const list = document.getElementById('questions-list');
            list.innerHTML = dictionary[currentLang].q.map((q, i) => `
                <div class="q-box">
                    <label><b>\${q}</b></label>
                    <select id="qsel\${i}">\${dictionary[currentLang].a[i].map(opt => `<option value="\${opt}">\${opt}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function submitData() {
            const payload = {
                name: document.getElementById('c_name').value,
                dob: document.getElementById('c_dob').value,
                answers: dictionary[currentLang].q.map((_, i) => document.getElementById('qsel'+i).value)
            };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            document.getElementById('quiz-ui').style.display = 'none';
            document.getElementById('success-ui').style.display = 'block';
        }

        async function fetchManagerData() {
            const res = await fetch('/api/list');
            const data = await res.json();
            const div = document.getElementById('manager-results');
            if(data.length === 0) { div.innerHTML = "<p>אין מועמדים רשומים במערכת.</p>"; return; }
            div.innerHTML = data.map(c => `
                <div class="m-item">
                    <b>\${c.name}</b> (\${c.dob})<br>
                    <small>תשובות: \${c.answers.join(' | ')}</small>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_CONTENT)

@app.route('/api/list')
def get_list(): return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    d = load_data()
    d.append(request.json)
    save_data(d)
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
