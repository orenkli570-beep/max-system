import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# פונקציות טעינה ושמירה
def load_data():
    try:
        if not os.path.exists('candidates.json'): return []
        with open('candidates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

def save_data(data):
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ממשק משתמש
HTML_CODE = """
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX System</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; direction: rtl; text-align: right; padding: 20px; }
        .container { background: white; max-width: 500px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; margin-bottom: 5px; }
        h2 { color: #555; text-align: center; font-size: 1rem; margin-bottom: 20px; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #ddd; font-size: 16px; box-sizing: border-box; }
        button { background: #e31e24; color: white; border: none; font-weight: bold; cursor: pointer; }
        .lang-btns { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; flex-wrap: wrap; }
        .lang-btns button { width: auto; padding: 5px 10px; background: #666; font-size: 12px; }
        .q-row { background: #f9f9f9; padding: 10px; border-right: 4px solid #e31e24; margin-bottom: 8px; }
        #admin-ui, #manager-ui, #quiz-ui, #success-ui { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MAX</h1>
        <h2>מערכת ניהול וגיוס מועמדים</h2>

        <div id="login-ui">
            <input type="text" id="user" placeholder="שם משתמש">
            <input type="password" id="pass" placeholder="סיסמה">
            <button onclick="doLogin()">כניסה</button>
        </div>

        <div id="admin-ui">
            <div class="lang-btns">
                <button onclick="changeLang('he')">עברית</button>
                <button onclick="changeLang('en')">English</button>
                <button onclick="changeLang('ru')">Русский</button>
                <button onclick="changeLang('ar')">العربية</button>
                <button onclick="changeLang('fr')">Français</button>
            </div>
            <h3 id="t-head">פרטי מועמד</h3>
            <input type="text" id="cName" placeholder="שם מלא">
            <input type="text" id="cDob" placeholder="תאריך לידה">
            <button onclick="showQuiz()">המשך לשאלון</button>
        </div>

        <div id="quiz-ui">
            <h3 id="t-quiz">שאלון התאמה (10 שאלות)</h3>
            <div id="qArea"></div>
            <button onclick="submitFinal()">שלח למנהל</button>
        </div>

        <div id="success-ui" style="text-align:center;">
            <h2 style="color:green">נשלח בהצלחה!</h2>
            <button onclick="location.reload()">חזרה</button>
        </div>

        <div id="manager-ui">
            <h3>לוח בקרה מנהל (עברית)</h3>
            <div id="mList">טוען נתונים...</div>
            <button onclick="location.reload()" style="background:#444">התנתק</button>
        </div>
    </div>

    <script>
        let L = 'he';
        const data = {
            he: { h:"פרטי מועמד", q:["סבלנות?","צוות?","לחץ?","סדר?","משמרות?","יוזמה?","שירות?","זמנים?","פיזי?","למה MAX?"], a:[["גבוהה","בינונית","נמוכה"],["צוות","לבד","תלוי"],["טוב","סביר","קשה"],["חשוב","סביר","לא"],["מלאה","חלקית","בוקר"],["יוזם","מבצע","הנחיה"],["סבלני","מנהל","מתעלם"],["דייקן","משתדל","מאחר"],["מתאים","סביר","לא"],["יציבות","שכר","עניין"]] },
            en: { h:"Candidate Info", q:["Patience?","Teamwork?","Pressure?","Order?","Shifts?","Initiative?","Service?","Punctual?","Physical?","Why MAX?"], a:[["High","Mid","Low"],["Team","Alone","Depends"],["Great","Ok","Hard"],["Important","Ok","No"],["Full","Part","Morning"],["Proactive","Doer","Guidance"],["Patient","Manager","Ignore"],["On time","Trying","Late"],["Fit","Ok","No"],["Stability","Salary","Interest"]] },
            ru: { h:"Данные", q:["Терпение?","Команда?","Стресс?","Порядок?","Смены?","Инициатива?","Сервис?","Время?","Физ. труд?","Почему MAX?"], a:[["Высокое","Среднее","Низкое"],["Команда","Один","Зависит"],["Отлично","Ок","Трудно"],["Важно","Ок","Нет"],["Полная","Часть","Утро"],["Сам","Делаю","Нужна помощь"],["Терпелив","Босс","Игнор"],["Вовремя","Стараюсь","Опаздываю"],["Подходит","Ок","Нет"],["Стабильность","Зарплата","Интерес"]] },
            ar: { h:"تفاصيل", q:["الصبر؟","فريق؟","ضغط؟","نظام؟","وردية؟","مبادرة؟","زبائن؟","دقة؟","جسדי؟","لماذا MAX؟"], a:[["عالي","متوسط","منخفض"],["فريق","وحدي","حسب"],["ممتاز","عادي","صعب"],["مهم","عادي","لا"],["كاملة","جزئية","صباحا"],["מבادر","منفذ","توجيه"],["صبور","مدير","تجاهل"],["دقيق","أحاول","أتأخر"],["يناسب","عادي","לא"],["استقرار","راتב","اهتمام"]] },
            fr: { h:"Détails", q:["Patience?","Equipe?","Pression?","Ordre?","Horaires?","Initiative?","Service?","Ponctualité?","Physique?","Pourquoi MAX?"], a:[["Haute","Moyenne","Basse"],["Equipe","Seul","Depend"],["Super","Ok","Dur"],["Important","Ok","Non"],["Plein","Partiel","Matin"],["Proactif","Executant","Besoin d'aide"],["Patient","Chef","Ignorer"],["Ponctuel","Essaye","Retard"],["Adapte","Ok","Non"],["Stabilite","Salaire","Interet"]] }
        };

        function doLogin() {
            const u = document.getElementById('user').value.trim().toLowerCase();
            const p = document.getElementById('pass').value.trim();
            if(u === 'admin' && p === 'max456') {
                document.getElementById('login-ui').style.display='none';
                document.getElementById('admin-ui').style.display='block';
            } else if(u === 'manager' && p === 'max123') {
                document.getElementById('login-ui').style.display='none';
                document.getElementById('manager-ui').style.display='block';
                loadM();
            } else { alert("פרטים שגויים"); }
        }

        function changeLang(lang) {
            L = lang;
            document.getElementById('t-head').innerText = data[L].h;
        }

        function showQuiz() {
            if(!document.getElementById('cName').value) return alert("נא להזין שם");
            document.getElementById('admin-ui').style.display='none';
            document.getElementById('quiz-ui').style.display='block';
            const qDiv = document.getElementById('qArea');
            qDiv.innerHTML = data[L].q.map((q, i) => `
                <div class="q-row">
                    <label><b>\${q}</b></label>
                    <select id="sel\${i}">\${data[L].a[i].map(opt => `<option value="\${opt}">\${opt}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function submitFinal() {
            const payload = {
                name: document.getElementById('cName').value,
                dob: document.getElementById('cDob').value,
                ans: data[L].q.map((_, i) => {
                    const idx = document.getElementById('sel'+i).selectedIndex;
                    return data['he'].a[i][idx]; // תמיד שומר בעברית למנהל
                })
            };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            document.getElementById('quiz-ui').style.display='none';
            document.getElementById('success-ui').style.display='block';
        }

        async function loadM() {
            const res = await fetch('/api/list');
            const items = await res.json();
            const div = document.getElementById('mList');
            div.innerHTML = items.length ? items.map(c => `
                <div style="border-bottom:1px solid #eee; padding:10px;">
                    <b>\${c.name}</b> (\${c.dob})<br><small>\${c.ans.join(' | ')}</small>
                </div>
            `).join('') : "אין נתונים";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_CODE)

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
