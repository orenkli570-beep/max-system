from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

DATA_FILE = 'candidates.json'

def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_CONTENT = '''
<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX - מערכת גיוס רב-לשונית</title>
    <style>
        :root { --max-red: #e31e24; --dark: #1e293b; }
        body { font-family: sans-serif; background: #f1f5f9; padding: 20px; direction: rtl; text-align: right; }
        .card { background: white; padding: 30px; border-radius: 15px; max-width: 800px; margin: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .lang-btns { text-align: center; margin-bottom: 20px; }
        .lang-btns button { width: auto; padding: 8px 15px; margin: 5px; background: #64748b; font-size: 0.9rem; }
        .lang-btns button.active { background: var(--max-red); }
        h1 { color: var(--max-red); text-align: center; }
        input, select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #cbd5e1; box-sizing: border-box; }
        button { background: var(--max-red); color: white; font-weight: bold; cursor: pointer; border: none; }
        .question-block { background: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 4px solid var(--max-red); }
        #admin-section, #manager-section, #success-screen, #questionnaire { display: none; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #eee; padding: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h1 id="main-title">MAX - מערכת גיוס</h1>
        
        <div id="login-section">
            <input type="text" id="user" placeholder="שם משתמש">
            <input type="password" id="pass" placeholder="סיסמה">
            <button onclick="handleLogin()">כניסה</button>
        </div>

        <div id="admin-section">
            <div class="lang-btns">
                <button onclick="setLang('he')" id="btn-he" class="active">עברית</button>
                <button onclick="setLang('en')" id="btn-en">English</button>
                <button onclick="setLang('ru')" id="btn-ru">Русский</button>
                <button onclick="setLang('ar')" id="btn-ar">العربية</button>
                <button onclick="setLang('fr')" id="btn-fr">Français</button>
            </div>
            <h3 id="step1-title">פרטי המועמד</h3>
            <input type="text" id="fname" placeholder="שם מלא / Full Name">
            <input type="text" id="dob" placeholder="תאריך לידה / DOB">
            <button onclick="startQuestions()" id="start-btn">התחל שאלון</button>
        </div>

        <div id="questionnaire">
            <h3 id="step2-title">שאלון התאמה</h3>
            <div id="questions-list"></div>
            <button onclick="saveFullData()" id="submit-btn">שלח למנהל</button>
        </div>

        <div id="success-screen" style="text-align:center;">
            <h2 id="success-msg" style="color:green;">נשלח בהצלחה!</h2>
            <button onclick="location.reload()">חזרה</button>
        </div>

        <div id="manager-section">
            <h3>לוח מנהל (עברית בלבד)</h3>
            <table>
                <thead><tr><th>שם</th><th>תאריך</th><th>פעולות</th></tr></thead>
                <tbody id="list"></tbody>
            </table>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const translations = {
            he: { title: "MAX - מערכת גיוס", step1: "פרטי המועמד", start: "התחל שאלון", step2: "שאלון התאמה", submit: "שלח למנהל", success: "נשלח בהצלחה!",
                  questions: [
                    {q: "רמת סבלנות?", a: ["גבוהה", "בינונית", "נמוכה"]},
                    {q: "עבודה בצוות?", a: ["אוהב מאוד", "מעדיף לבד", "תלוי במשימה"]},
                    {q: "לחץ בעבודה?", a: ["מתפקד מצוין", "סביר", "קשה לי"]},
                    {q: "סדר וארגון?", a: ["חשוב מאוד", "בינוני", "לא חשוב"]},
                    {q: "שעות נוספות?", a: ["אפשרי", "רק בבוקר", "לא מתאים"]}
                  ]},
            en: { title: "MAX - Recruitment", step1: "Candidate Details", start: "Start Quiz", step2: "Assessment", submit: "Submit to Manager", success: "Sent Successfully!",
                  questions: [
                    {q: "Patience level?", a: ["High", "Medium", "Low"]},
                    {q: "Teamwork?", a: ["Love it", "Prefer alone", "Depends"]},
                    {q: "Work pressure?", a: ["Great", "Average", "Difficult"]},
                    {q: "Organization?", a: ["Very important", "Medium", "Not important"]},
                    {q: "Extra hours?", a: ["Possible", "Mornings only", "No"]}
                  ]},
            ru: { title: "MAX - Рекрутинг", step1: "Данные кандидата", start: "Начать тест", step2: "Опросник", submit: "Отправить менеджеру", success: "Успешно отправлено!",
                  questions: [
                    {q: "Уровень терпения?", a: ["Высокий", "Средний", "Низкий"]},
                    {q: "Командная работа?", a: ["Люблю", "Предпочитаю один", "Зависит"]},
                    {q: "Стресс?", a: ["Отлично", "Средне", "Трудно"]},
                    {q: "Порядок?", a: ["Очень важно", "Средне", "Не важно"]},
                    {q: "Доп. часы?", a: ["Возможно", "Только утро", "Нет"]}
                  ]},
            ar: { title: "MAX - توظيف", step1: "تفاصيل المرشح", start: "ابدأ الاختبار", step2: "استبيان التقييم", submit: "إرسال للمدير", success: "تم الإرسال بنجاح!",
                  questions: [
                    {q: "مستوى الصبر؟", a: ["عالي", "متوسط", "منخفض"]},
                    {q: "العمل الجماعي؟", a: ["أحب جداً", "أفضل وحدي", "حسب المهمة"]},
                    {q: "ضغط العمل؟", a: ["ممتاز", "متوسط", "صعب"]},
                    {q: "النظام؟", a: ["مهم جداً", "متوسط", "غير مهم"]},
                    {q: "ساعات إضافية؟", a: ["ممكن", "صباحاً فقط", "غير مناسب"]}
                  ]},
            fr: { title: "MAX - Recrutement", step1: "Détails du candidat", start: "Commencer", step2: "Évaluation", submit: "Envoyer au Manager", success: "Envoyé avec succès!",
                  questions: [
                    {q: "Niveau de patience?", a: ["Élevé", "Moyen", "Bas"]},
                    {q: "Travail d'équipe?", a: ["J'adore", "Préfère seul", "Dépend"]},
                    {q: "Pression?", a: ["Excellent", "Moyen", "Difficile"]},
                    {q: "Organisation?", a: ["Très important", "Moyen", "Pas important"]},
                    {q: "Heures sup?", a: ["Possible", "Matin seulement", "Non"]}
                  ]}
        };

        function setLang(lang) {
            currentLang = lang;
            document.querySelectorAll('.lang-btns button').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + lang).classList.add('active');
            document.getElementById('main-title').innerText = translations[lang].title;
            document.getElementById('step1-title').innerText = translations[lang].step1;
            document.getElementById('start-btn').innerText = translations[lang].start;
            document.getElementById('step2-title').innerText = translations[lang].step2;
            document.getElementById('submit-btn').innerText = translations[lang].submit;
            document.getElementById('success-msg').innerText = translations[lang].success;
        }

        function handleLogin() {
            const u = document.getElementById('user').value.trim().toLowerCase();
            const p = document.getElementById('pass').value.trim();
            if (u === "admin" && p === "max456") {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('admin-section').style.display = 'block';
            } else if (u === "manager" && p === "max123") {
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('manager-section').style.display = 'block';
                loadCandidates();
            } else { alert("Error"); }
        }

        function startQuestions() {
            document.getElementById('admin-section').style.display = 'none';
            document.getElementById('questionnaire').style.display = 'block';
            const list = document.getElementById('questions-list');
            list.innerHTML = translations[currentLang].questions.map((q, i) => `
                <div class="question-block">
                    <label><b>\${q.q}</b></label>
                    <select id="q\${i}">\${q.a.map(opt => `<option value="\${opt}">\${opt}</option>`).join('')}</select>
                </div>
            `).join('');
        }

        async function saveFullData() {
            // שומר את האינדקס של התשובה כדי שהמנהל יוכל לראות אותה בעברית
            const data = {
                name: document.getElementById('fname').value,
                dob: document.getElementById('dob').value,
                answers: translations[currentLang].questions.map((_, i) => {
                    const selIdx = document.getElementById('q'+i).selectedIndex;
                    return translations['he'].questions[i].a[selIdx]; // תמיד שומר לעברית
                })
            };
            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            document.getElementById('questionnaire').style.display = 'none';
            document.getElementById('success-screen').style.display = 'block';
        }

        async function loadCandidates() {
            const res = await fetch('/api/list');
            const data = await res.json();
            document.getElementById('list').innerHTML = data.map(c => `
                <tr><td>\${c.name}</td><td>\${c.dob}</td><td><button onclick='alert("\${c.answers.join(", ")}")'>צפה (בעברית)</button></td></tr>
            `).join('');
        }
    </script>
</body>
</html>
