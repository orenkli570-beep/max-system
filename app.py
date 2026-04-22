import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- לוגיקה של הגילוי הפנימי ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def get_name_num(name):
    g_map = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':1,'כ':2,'ל':3,'מ':4,'נ':5,'ס':6,'ע':7,'פ':8,'צ':9,'ק':1,'ר':2,'ש':3,'ת':4,'ך':2,'ם':4,'ן':5,'ף':8,'ץ':9}
    total = sum(g_map.get(c, 0) for c in name)
    return get_num(total)

def analyze_rel(c_dob):
    m_num = 5 # 14.9 = 1+4+9=14 -> 1+4=5
    c_num = get_num(c_dob)
    rel_score = get_num(m_num + c_num)
    map_rel = {
        1: "יחסים של סמכות וביצוע מהיר. המועמד יכבד דרישות חדות.",
        2: "שיתוף פעולה רגיש. דורש הסברים רכים ונעימים.",
        3: "דינמיקה יצירתית. המועמד יפרח תחת דרישות שמאפשרות ביטוי עצמי.",
        4: "יחסי עבודה פרקטיים מאוד. המועמד מצפה לדרישות ברורות ומסודרות.",
        5: "תקשורת מהירה ודינמית. שניכם צריכים מרחב פעולה.",
        6: "הרמוניה ואחריות. המועמד יבצע דרישות מתוך תחושת מחויבות גבוהה.",
        7: "צורך בשקט והסברים מעמיקים. לא אוהב דרישות בלחץ.",
        8: "הישגיות גבוהה וכוח. המועמד יבצע דרישות כדי להתקדם.",
        9: "שירותיות רחבה. המועמד יבצע דרישות למען המטרה הכללית.",
        11: "אינטואיציה גבוהה. המועמד יבין את הדרישות שלך לפני שתגיד אותן.",
        22: "ביצועיסט על. מסוגל להוציא לפועל פרויקטים מורכבים עבורך."
    }
    return map_rel.get(rel_score, "יחסי עבודה סטנדרטיים")

def save_db(data):
    db = []
    if os.path.exists('candidates.json'):
        with open('candidates.json', 'r', encoding='utf-8') as f: db = json.load(f)
    db.append(data)
    with open('candidates.json', 'w', encoding='utf-8') as f: json.dump(db, f, ensure_ascii=False, indent=4)

# --- ממשק משתמש ---
HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX System</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; direction: rtl; padding: 20px; }
        .card { background: white; max-width: 800px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; margin:0; } h2 { color: #475569; border-bottom: 2px solid #e31e24; padding-bottom: 10px; }
        .lang-bar { display: flex; gap: 5px; margin-bottom: 20px; }
        .lang-bar button { flex: 1; padding: 5px; background: #64748b; color: white; border: none; border-radius: 4px; cursor: pointer; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ddd; }
        .btn-main { background: #e31e24; color: white; font-weight: bold; font-size: 1.1rem; border: none; cursor: pointer; }
        .hidden { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background: #f8fafc; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX כאן קונים בכיף</h1>
        <h2>מערכת גיוס והתאמת עובדים</h2>

        <div id="ui-login">
            <input type="text" id="u" placeholder="שם משתמש">
            <input type="password" id="p" placeholder="סיסמה">
            <button class="btn-main" onclick="login()">כניסה</button>
        </div>

        <div id="ui-sec" class="hidden">
            <div class="lang-bar">
                <button onclick="setL('he')">עברית</button><button onclick="setL('en')">EN</button>
                <button onclick="setL('ru')">RU</button><button onclick="setL('ar')">AR</button><button onclick="setL('fr')">FR</button>
            </div>
            <div id="sec-form">
                <input type="text" id="cName" placeholder="שם המועמד">
                <input type="text" id="cDob" placeholder="תאריך לידה">
                <button class="btn-main" onclick="goQuiz()">המשך לשאלון</button>
            </div>
            <div id="quiz-area" class="hidden"></div>
        </div>

        <div id="ui-man" class="hidden">
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>מועמד</th>
                            <th>התאמה</th>
                            <th>מחלקה ומשרה</th>
                            <th>יחסים עם המנהל (דרישות)</th>
                        </tr>
                    </thead>
                    <tbody id="mTable"></tbody>
                </table>
            </div>
            <button onclick="location.reload()">התנתק</button>
        </div>
    </div>

    <script>
        let curL = 'he';
        const dict = {
            he: { q: ["סבלנות?","צוות?","לחץ?","סדר?","משמרות?","יוזמה?","שירות?","דייקנות?","פיזי?","למה MAX?"], a: ["גבוהה","בינונית","נמוכה"], msg: "התשובות ממתינות לאישור המנהל" },
            en: { q: ["Patience?","Team?","Pressure?","Order?","Shifts?","Initiative?","Service?","Punctual?","Physical?","Why MAX?"], a: ["High","Mid","Low"], msg: "Answers pending manager approval" },
            ru: { q: ["Терпение?","Команда?","Давление?","Порядок?","Смены?","Инициатива?","Сервис?","Точность?","Физика?","Почему MAX?"], a: ["Высокая","Средняя","Низкая"], msg: "Ответы ожидают одобрения" },
            ar: { q: ["الصبر؟","فريق؟","ضغط؟","نظام؟","وردية؟","مبادرة؟","خدمة؟","دقة؟","جسدي؟","لماذا MAX؟"], a: ["عالي","متوسط","منخفض"], msg: "الإجابات بانتظار موافقة المدير" },
            fr: { q: ["Patience?","Équipe?","Pression?","Ordre?","Shifts?","Initiative?","Service?","Ponctualité?","Physique?","Pourquoi MAX?"], a: ["Haute","Moyenne","Basse"], msg: "Réponses en attente du responsable" }
        };

        function setL(l) { curL = l; if(!document.getElementById('quiz-area').classList.contains('hidden')) goQuiz(); }

        function login() {
            const u = document.getElementById('u').value;
            if(u === 'admin') show('ui-sec');
            else if(u === 'manager') { show('ui-man'); loadM(); }
        }

        function show(id) {
            document.querySelectorAll('div[id^="ui-"]').forEach(d => d.classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden');
        }

        function goQuiz() {
            document.getElementById('sec-form').classList.add('hidden');
            const area = document.getElementById('quiz-area');
            area.classList.remove('hidden');
            let h = '';
            dict[curL].q.forEach((q, i) => {
                h += `<div style="text-align:right;"><label>${q}</label><select id="a${i}">`;
                dict[curL].a.forEach(opt => h += `<option>${opt}</option>`);
                h += `</select></div>`;
            });
            h += `<button class="btn-main" onclick="send()">${dict[curL].msg.split(' ')[0]}...</button>`;
            area.innerHTML = h;
        }

        async function send() {
            const payload = {
                name: document.getElementById('cName').value,
                dob: document.getElementById('cDob').value,
                ans: Array.from({length:10}, (_, i) => document.getElementById('a'+i).value)
            };
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
            alert(dict[curL].msg);
            location.reload();
        }

        function loadM() {
            fetch('/api/list').then(r => r.json()).then(data => {
                document.getElementById('mTable').innerHTML = data.reverse().map(c => `
                    <tr>
                        <td><b>${c.name}</b><br>${c.dob}</td>
                        <td style="color:red; font-weight:bold;">${c.score}%</td>
                        <td>${c.dept}<br><small>${c.job}</small></td>
                        <td style="text-align:right; font-size:11px;">${c.rel}</td>
                    </tr>
                `).join('');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/list')
def get_l():
    if os.path.exists('candidates.json'):
        with open('candidates.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    # חישוב התאמה ומחלקות
    depts = ["טקסטיל", "כלי בית", "חשמל", "צעצועים", "ניקיון", "פארם", "כלי כתיבה", "ימי הולדת", "יצירה", "כלי עבודה", "ספורט", "רכב", "חיות מחמד"]
    jobs = ["סדרן", "אחראי משמרת", "אחראי מחלקה", "אדמיניסטרציה", "מחסנאי", "מנהל מחסן", "בודק סחורה", "עובד כללי", "קופאית ראשית", "קופאית רגילה", "סגן מנהל", "מנהל"]
    
    n_num = get_name_num(d['name'])
    d_num = get_num(d['dob'])
    
    d['dept'] = depts[d_num % len(depts)]
    d['job'] = jobs[n_num % len(jobs)]
    d['score'] = 75 + (n_num + d_num) % 25
    d['rel'] = analyze_rel(d['dob'])
    
    save_db(d)
    return jsonify({"ok":True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
