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

HTML_TEMPLATE = """
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX Recruitment System</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f2f5; direction: rtl; text-align: right; padding: 10px; margin: 0; }
        .card { background: white; max-width: 600px; margin: 20px auto; padding: 25px; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; font-size: 16px; }
        button { background: #e31e24; color: white; border: none; cursor: pointer; font-weight: bold; transition: 0.2s; }
        button:hover { background: #c1181d; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .lang-bar button { width: auto; padding: 8px 12px; background: #475569; font-size: 13px; }
        .lang-bar button.active { background: #e31e24; }
        .q-item { background: #f8fafc; padding: 15px; margin-bottom: 15px; border-right: 5px solid #e31e24; border-radius: 6px; }
        #admin-ui, #manager-ui, #success-ui, #quiz-ui { display: none; }
        .m-card { border: 1px solid #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 10px; background: #fff; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX - Recruitment</h1>
        
        <div id="login-ui">
            <input type="text" id="user_in" placeholder="שם משתמש / Username">
            <input type="password" id="pass_in" placeholder="סיסמה / Password">
            <button onclick="doLogin()">כניסה / Login</button>
        </div>

        <div id="admin-ui">
            <div class="lang-bar">
                <button onclick="changeL('he')" id="btn-he" class="active">עברית</button>
                <button onclick="changeL('en')" id="btn-en">English</button>
                <button onclick="changeL('ru')" id="btn-ru">Русский</button>
                <button onclick="changeL('ar')" id="btn-ar">العربية</button>
                <button onclick="changeL('fr')" id="btn-fr">Français</button>
            </div>
            <h3 id="txt-details">פרטי מועמד</h3>
            <input type="text" id="cand_name" placeholder="שם מלא / Full Name">
            <input type="text" id="cand_dob" placeholder="תאריך לידה / Date of Birth">
            <button onclick="goQuiz()" id="btn-next">המשך לשאלון</button>
        </div>

        <div id="quiz-ui">
            <h3 id="txt-quiz">שאלון התאמה</h3>
            <div id="questions-area"></div>
            <button onclick="finishAndSend()" id="btn-send">שלח למנהל</button>
        </div>

        <div id="success-ui" style="text-align:center;">
            <div style="font-size: 50px; color: #22c55e;">✓</div>
            <h2 id="txt-success">נשלח בהצלחה!</h2>
            <p id="txt-msg">הנתונים הועברו למנהל לצורך ניתוח ברוח "הגילוי הפנימי".</p>
            <button onclick="location.reload()" style="background:#475569">הזן מועמד חדש</button>
        </div>

        <div id="manager-ui">
            <h3>לוח בקרה מנהל (תצוגה בעברית)</h3>
            <div id="manager-list"></div>
            <button onclick="location.reload()" style="background:#475569; margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        let L = 'he';
        const dict = {
            he: { details: "פרטי מועמד", next: "המשך לשאלון", quiz: "שאלון התאמה", send: "שלח למנהל", success: "נשלח בהצלחה!", msg: "הנתונים הועברו למנהל לצורך ניתוח.",
                q: ["סבלנות בעבודה?", "עבודה בצוות?", "עמידה בלחץ?", "סדר וארגון?", "זמינות למשמרות?", "יוזמה אישית?", "התמודדות עם לקוח?", "דיוק בזמנים?", "עבודה פיזית?", "למה דווקא MAX?"],
                a: [["גבוהה", "בינונית", "נמוכה"], ["מעדיף צוות", "מעדיף לבד", "תלוי במשימה"], ["מצוין", "סביר", "קשה לי"], ["חשוב מאוד", "חשוב במידה", "לא חשוב"], ["מלאה", "חלקי", "רק בוקר"], ["תמיד מחפש", "עושה מה שצריך", "מעדיף הנחיות"], ["בסבלנות", "קורא למנהל", "מתעלם"], ["דייקן מאוד", "משתדל", "מאחר לפעמים"], ["מתאים לי", "סביר", "לא מתאים"], ["יציבות", "שכר", "עניין"]] },
            en: { details: "Candidate Info", next: "Continue to Quiz", quiz: "Assessment Quiz", send: "Submit to Manager", success: "Sent!", msg: "Data sent to manager for analysis.",
                q: ["Patience?", "Teamwork?", "Pressure?", "Order?", "Shifts?", "Initiative?", "Customer service?", "Punctuality?", "Physical work?", "Why MAX?"],
                a: [["High", "Medium", "Low"], ["Team", "Alone", "Depends"], ["Excellent", "Average", "Hard"], ["Very important", "Fair", "Not important"], ["Full", "Partial", "Morning only"], ["Always", "As required", "Need guidance"], ["Patiently", "Call manager", "Ignore"], ["Very punctual", "Trying", "Sometimes late"], ["Fit", "Okay", "Not fit"], ["Stability", "Salary", "Interest"]] },
            ru: { details: "Данные кандидата", next: "К тесту", quiz: "Опросник", send: "Отправить менеджеру", success: "Успешно!", msg: "Данные отправлены менеджеру.",
                q: ["Терпение?", "Команда?", "Стресс?", "Порядок?", "Смены?", "Инициатива?", "Клиенты?", "Пунктуальность?", "Физ. работа?", "Почему MAX?"],
                a: [["Высокое", "Среднее", "Низкое"], ["Команда", "Один", "Зависит"], ["Отлично", "Ок", "Трудно"], ["Очень важно", "Средне", "Не важно"], ["Полная", "Частично", "Только утро"], ["Всегда", "По заданию", "Нужны указания"], ["Терпеливо", "Звать шефа", "Игнор"], ["Пунктуален", "Стараюсь", "Опаздываю"], ["Подходит", "Ок", "Нет"], ["Стабильность", "Зарплата", "Интерес"]] },
            ar: { details: "تفاصيل المرشح", next: "متابعة للاختبار", quiz: "استبيان التقييم", send: "إرسال للمدير", success: "تم الإرسال!", msg: "تم إرسال البيانات للمدير للتحليل.",
                q: ["مستوى الصبر؟", "العمل الجماعي؟", "ضغط العمل؟", "النظام؟", "الورديات؟", "المبادرة؟", "تعامل مع زبون؟", "الدقة؟", "عمل جسدي؟", "لماذا MAX؟"],
                a: [["عالي", "متوسط", "منخفض"], ["فريق", "وحدي", "حسب"], ["ممتاز", "عادي", "صعب"], ["مهم جداً", "متوسط", "غير مهم"], ["كاملة", "جزئياً", "صباحاً فقط"], ["دائماً", "حسب الطلب", "أحتاج توجيه"], ["بصبر", "أنادي المدير", "تجاهل"], ["دقيق جداً", "أحاول", "أتأخر أحياناً"], ["يناسبني", "عادي", "لا يناسبني"], ["استقرار", "راتب", "اهتمام"]] },
            fr: { details: "Infos Candidat", next: "Continuer", quiz: "Évaluation", send: "Envoyer", success: "Envoyé!", msg: "Données envoyées au manager.",
                q: ["Patience?", "Équipe?", "Pression?", "Ordre?", "Horaires?", "Initiative?", "Clientèle?", "Ponctualité?", "Travail physique?", "Pourquoi MAX?"],
                a: [["Élevée", "Moyenne", "Basse"], ["Équipe", "Seul", "Dépend"], ["Excellent", "Moyen", "Difficile"], ["Très important", "Moyen", "Pas important"], ["Temps plein", "Partiel", "Matin seulement"], ["Toujours", "Selon besoin", "Besoin d'aide"], ["Patiemment", "Appeler chef", "Ignorer"], ["Ponctuel", "Essaye", "En retard"], ["Adapté", "Ok", "Pas adapté"], ["Stabilité", "Salaire", "Intérêt"]] }
        };

        function changeL(lang) {
            L = lang;
            document.querySelectorAll('.lang-bar button').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + lang).classList.add('active');
            document.getElementById('txt-details').innerText = dict[L].details;
            document.getElementById('btn-next').innerText = dict[L].next;
            document.getElementById('txt-quiz').innerText = dict[L].quiz;
            document.getElementById('btn-send').innerText = dict[L].send;
            document.getElementById('txt-success').innerText = dict[L].success;
            document.getElementById('txt-msg').innerText = dict[L].msg;
        }

        function doLogin() {
            const u = document.getElementById('user_in').value.trim().toLowerCase();
            const p = document.getElementById('pass_in').value.trim();
            if(u === 'admin' && p === 'max456') {
                document.getElementById('login-ui').style.display='none';
                document.getElementById('admin-ui').style.display='block';
            } else if(u === 'manager' && p === 'max123') {
                document.getElementById('login-ui').style.display='none';
                document.getElementById('manager-ui').style.display='block';
                fetchList();
            } else { alert("Error: Wrong details"); }
        }

        function goQuiz() {
            if(!document.getElementById('cand_name').value) return alert("Please enter name");
            document.getElementById('admin-ui').style.display='none';
            document.getElementById('quiz-ui').style.display='block';
            const area = document.getElementById('questions-area');
            area.innerHTML = dict[L].q.map((q, i) => `
                <div class="q-item">
                    <label><b>\${q}</b></label>
                    <select id="ans\${i}">\${dict[L].a[i].map(opt => `<option value="\${opt}">\${opt}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function finishAndSend() {
            const payload = {
                name: document.getElementById('cand_name').value,
                dob: document.getElementById('cand_dob').value,
                // תרגום התשובות לעברית עבור המנהל
                answers: dict[L].q.map((_, i) => {
                    const idx = document.getElementById('ans'+i).selectedIndex;
                    return dict['he'].a[i][idx];
                })
            };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            document.getElementById('quiz-ui').style.display='none';
            document.getElementById('success-ui').style.display='block';
        }

        async function fetchList() {
            const res = await fetch('/api/list');
            const data = await res.json();
            const div = document.getElementById('manager-list');
            div.innerHTML = data.map(c => `
                <div class="m-card">
                    <div style="color:#e31e24; font-weight:bold; font-size:1.1rem;">\${c.name}</div>
                    <div style="color:#64748b; margin-bottom:10px;">תאריך לידה: \${c.dob}</div>
                    <div style="font-size:0.9rem; border-top:1px solid #eee; padding-top:5px;">
                        \${c.answers.map((a, i) => `<div><b>\${dict['he'].q[i]}:</b> \${a}</div>`).join('')}
                    </div>
                </div>
            `).join('');
            if(data.length === 0) div.innerHTML = "<p>אין מועמדים חדשים.</p>";
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
    p = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=p)
