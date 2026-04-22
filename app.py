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

# שימוש ב-raw string (r) למניעת שגיאות ה-invalid escape שראינו בלוגים שלך
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX - Recruitment System</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; direction: rtl; text-align: right; padding: 15px; margin: 0; }
        .card { background: white; max-width: 550px; margin: 20px auto; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #e31e24; margin-bottom: 20px; padding-bottom: 10px; }
        h1 { color: #e31e24; margin: 0; font-size: 2.2rem; }
        h2 { color: #475569; margin: 5px 0; font-size: 1.1rem; font-weight: normal; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; font-size: 16px; }
        button { background: #e31e24; color: white; border: none; cursor: pointer; font-weight: bold; }
        .lang-bar { display: flex; justify-content: center; gap: 5px; margin-bottom: 15px; flex-wrap: wrap; }
        .lang-bar button { width: auto; padding: 6px 10px; background: #64748b; font-size: 13px; }
        .q-item { background: #f8fafc; padding: 12px; margin-bottom: 12px; border-right: 4px solid #e31e24; border-radius: 4px; }
        .hidden { display: none; }
        .m-card { border-bottom: 1px solid #eee; padding: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>MAX</h1>
            <h2>מערכת ניהול וגיוס מועמדים</h2>
        </div>
        
        <div id="ui-login">
            <input type="text" id="user" placeholder="שם משתמש">
            <input type="password" id="pass" placeholder="סיסמה">
            <button onclick="doLogin()">כניסה למערכת</button>
        </div>

        <div id="ui-admin" class="hidden">
            <div class="lang-bar">
                <button onclick="setL('he')">עברית</button>
                <button onclick="setL('en')">English</button>
                <button onclick="setL('ru')">Русский</button>
                <button onclick="setL('ar')">العربية</button>
                <button onclick="setL('fr')">Français</button>
            </div>
            <h3 id="lbl-det">פרטי מועמד</h3>
            <input type="text" id="cName" placeholder="שם מלא">
            <input type="text" id="cDob" placeholder="תאריך לידה">
            <button id="btn-next" onclick="showQuiz()">המשך לשאלון התאמה</button>
        </div>

        <div id="ui-quiz" class="hidden">
            <h3 id="lbl-quiz">שאלון התאמה</h3>
            <div id="questions-area"></div>
            <button id="btn-save" onclick="submit()">סיום ושליחה למנהל</button>
        </div>

        <div id="ui-success" class="hidden" style="text-align:center;">
            <h2 style="color:green">✓ השאלון נשלח בהצלחה</h2>
            <button onclick="location.reload()">חזרה להתחלה</button>
        </div>

        <div id="ui-manager" class="hidden">
            <h3>לוח מנהל (תצוגה בעברית)</h3>
            <div id="manager-list">טוען נתונים...</div>
            <button onclick="location.reload()" style="background:#475569">התנתק</button>
        </div>
    </div>

    <script>
        let L = 'he';
        const content = {
            he: { det:"פרטי מועמד", quiz:"שאלון התאמה", next:"המשך לשאלון", save:"שלח למנהל",
                  q: ["סבלנות?","עבודה בצוות?","עמידה בלחץ?","סדר וארגון?","משמרות?","יוזמה?","שירות לקוחות?","דייקנות?","מאמץ פיזי?","למה MAX?"],
                  a: [["גבוהה","בינונית","נמוכה"],["צוות","לבד","תלוי"],["טוב","סביר","קשה"],["חשוב","סביר","לא"],["מלאה","חלקית","בוקר"],["מבادر","מבצע","הנחיה"],["סבלני","מנהל","מתעלם"],["דייקן","משתדל","מאחר"],["מתאים","סביר","לא"],["יציבות","שכר","עניין"]] },
            en: { det:"Candidate Info", quiz:"Assessment", next:"Continue", save:"Submit",
                  q: ["Patience?","Teamwork?","Pressure?","Order?","Shifts?","Initiative?","Service?","Punctual?","Physical?","Why MAX?"],
                  a: [["High","Mid","Low"],["Team","Alone","Depends"],["Great","Ok","Hard"],["Important","Ok","No"],["Full","Part","Morning"],["Proactive","Doer","Guidance"],["Patient","Manager","Ignore"],["On time","Trying","Late"],["Fit","Ok","No"],["Stability","Salary","Interest"]] },
            ru: { det:"Данные", quiz:"Опрос", next:"Далее", save:"Отправить",
                  q: ["Терпение?","Команда?","Стресс?","Порядок?","Смены?","Инициатива?","Сервис?","Время?","Физ. труд?","Почему MAX?"],
                  a: [["Высокое","Среднее","Низкое"],["Команда","Один","Зависит"],["Отлично","Ок","Трудно"],["Важно","Ок","Нет"],["Полная","Часть","Утро"],["Сам","Делаю","Нужна помощь"],["Терпелив","Босс","Игнор"],["Вовремя","Стараюсь","Опаздываю"],["Подходит","Ок","Нет"],["Стабильность","Зарплата","Интерес"]] },
            ar: { det:"تفاصيل", quiz:"استبيان", next:"متابعة", save:"إرسال",
                  q: ["الصبر؟","فريق؟","ضغط؟","نظام؟","وردية؟","مبادرة؟","زبائن؟","دقة؟","جسדי؟","لماذا MAX؟"],
                  a: [["عالي","متوسط","منخفض"],["فريق","وحدي","حسب"],["ممتاز","عادي","صعب"],["مهم","عادي","لا"],["كاملة","جزئية","صباحا"],["מבادر","منفذ","توجيه"],["صبור","مدير","تجاهل"],["دقيق","أحاول","أتأخر"],["يناسب","عادي","לא"],["استقرار","راتב","اهتمام"]] },
            fr: { det:"Détails", quiz:"Evaluation", next:"Continuer", save:"Envoyer",
                  q: ["Patience?","Equipe?","Pression?","Ordre?","Horaires?","Initiative?","Service?","Ponctualité?","Physique?","Pourquoi MAX?"],
                  a: [["Haute","Moyenne","Basse"],["Equipe","Seul","Depend"],["Super","Ok","Dur"],["Important","Ok","Non"],["Plein","Partiel","Matin"],["Proactif","Executant","Aide"],["Patient","Chef","Ignorer"],["Ponctuel","Essaye","Retard"],["Adapte","Ok","Non"],["Stabilité","Salaire","Intérêt"]] }
        };

        function setL(lang) {
            L = lang;
            document.getElementById('lbl-det').innerText = content[L].det;
            document.getElementById('btn-next').innerText = content[L].next;
            document.getElementById('cName').placeholder = (L === 'he') ? "שם מלא" : "Full Name";
            document.getElementById('cDob').placeholder = (L === 'he') ? "תאריך לידה" : "Date of Birth";
        }

        function doLogin() {
            const u = document.getElementById('user').value.trim().toLowerCase();
            const p = document.getElementById('pass').value.trim();
            if(u === 'admin' && p === 'max456') {
                document.getElementById('ui-login').classList.add('hidden');
                document.getElementById('ui-admin').classList.remove('hidden');
            } else if(u === 'manager' && p === 'max123') {
                document.getElementById('ui-login').classList.add('hidden');
                document.getElementById('ui-manager').classList.remove('hidden');
                loadManager();
            } else { alert("פרטים שגויים"); }
        }

        function showQuiz() {
            if(!document.getElementById('cName').value) return alert("נא להזין שם");
            document.getElementById('ui-admin').classList.add('hidden');
            document.getElementById('ui-quiz').classList.remove('hidden');
            document.getElementById('lbl-quiz').innerText = content[L].quiz;
            document.getElementById('btn-save').innerText = content[L].save;
            
            let html = '';
            content[L].q.forEach((q, i) => {
                html += '<div class="q-item"><b>' + q + '</b><select id="ans' + i + '">';
                content[L].a[i].forEach(opt => { html += '<option value="' + opt + '">' + opt + '</option>'; });
                html += '</select></div>';
            });
            document.getElementById('questions-area').innerHTML = html;
        }

        async function submit() {
            const results = [];
            for(let i=0; i<10; i++) {
                const sel = document.getElementById('ans'+i);
                // תרגום חזרה לעברית עבור המנהל לפי מיקום התשובה שנבחרה
                results.push(content['he'].a[i][sel.selectedIndex]);
            }
            const payload = { name: document.getElementById('cName').value, dob: document.getElementById('cDob').value, ans: results };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            document.getElementById('ui-quiz').classList.add('hidden');
            document.getElementById('ui-success').classList.remove('hidden');
        }

        function loadManager() {
            fetch('/api/list').then(r => r.json()).then(data => {
                document.getElementById('manager-list').innerHTML = data.map(c => 
                    '<div class="m-card"><b>'+c.name+'</b> ('+c.dob+')<br><small>'+c.ans.join(' | ')+'</small></div>'
                ).join('') || "אין מועמדים ברשימה";
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_CONTENT)

@app.route('/api/list')
def list_candidates(): return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save_candidate():
    data = load_data()
    data.append(request.json)
    save_data(data)
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
