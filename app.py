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
    m_num = 5 # 14.9 = 5
    c_num = get_num(c_dob)
    rel_score = get_num(m_num + c_num)
    map_rel = {
        1: "סמכות וביצוע מהיר.", 2: "שיתוף פעולה רגיש.", 3: "דינמיקה יצירתית.",
        4: "עבודה פרקטית ומסודרת.", 5: "תקשורת מהירה ודינמית.", 6: "אחריות והרמוניה.",
        7: "צורך בשקט והסברים.", 8: "הישגיות וכוח.", 9: "שירותיות רחבה.",
        11: "הבנה אינטואיטיבית.", 22: "ביצועיסט על."
    }
    return map_rel.get(rel_score, "עבודה זורמת.")

# --- ניהול נתונים בטוח ---
def get_db(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

def save_to_db(filename, data):
    db = get_db(filename)
    db.append(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- ממשק HTML ---
HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX System</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; direction: rtl; padding: 20px; text-align: center; }
        .card { background: white; max-width: 800px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; margin-bottom: 5px; }
        h2 { color: #475569; border-bottom: 2px solid #e31e24; padding-bottom: 10px; margin-bottom: 20px; font-weight: normal; }
        .lang-bar { display: flex; gap: 5px; margin-bottom: 20px; }
        .lang-bar button { flex: 1; padding: 8px; background: #64748b; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        input, select, button.main-btn { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ddd; font-size: 16px; }
        button.main-btn { background: #e31e24; color: white; font-weight: bold; cursor: pointer; border: none; }
        .hidden { display: none; }
        .tab-btn { padding: 10px; cursor: pointer; background: #eee; border: 1px solid #ccc; margin: 5px; display: inline-block; }
        .active { background: #e31e24; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        th, td { border: 1px solid #ddd; padding: 10px; }
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
            <button class="main-btn" onclick="login()">כניסה למערכת</button>
        </div>

        <div id="ui-sec" class="hidden">
            <div class="lang-bar">
                <button onclick="setL('he')">עברית</button>
                <button onclick="setL('en')">English</button>
                <button onclick="setL('ru')">Русский</button>
                <button onclick="setL('ar')">العربية</button>
                <button onclick="setL('th')">ไทย (תאילנדית)</button>
            </div>
            <div id="sec-form">
                <input type="text" id="cName" placeholder="שם המועמד">
                <input type="text" id="cDob" placeholder="תאריך לידה (למשל 10.05.1995)">
                <button class="main-btn" onclick="goQuiz()">המשך לשאלון</button>
            </div>
            <div id="quiz-area" class="hidden"></div>
        </div>

        <div id="ui-man" class="hidden">
            <div class="tabs">
                <button class="tab-btn active" onclick="switchTab('c')">מועמדים</button>
                <button class="tab-btn" onclick="switchTab('s')">צוות ותיק</button>
            </div>
            <div id="tab-c">
                <table>
                    <thead><tr><th>שם</th><th>התאמה</th><th>מחלקה/משרה</th><th>יחסים (דרישות)</th></tr></thead>
                    <tbody id="cTable"></tbody>
                </table>
            </div>
            <div id="tab-s" class="hidden">
                <input type="text" id="sName" placeholder="שם עובד ותיק">
                <input type="text" id="sDob" placeholder="תאריך לידה">
                <button class="main-btn" onclick="addStaff()">הוסף לצוות</button>
                <div id="sList"></div>
            </div>
            <button onclick="location.reload()" style="margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        let curL = 'he';
        const dict = {
            he: { q: ["סבלנות?","צוות?","לחץ?","סדר?","משמרות?","יוזמה?","שירות?","דייקנות?","פיזי?","למה MAX?"], a: ["גבוהה","בינונית","נמוכה"], finish: "התשובות ממתינות לאישור המנהל" },
            en: { q: ["Patience?","Team?","Pressure?","Order?","Shifts?","Initiative?","Service?","Punctual?","Physical?","Why MAX?"], a: ["High","Mid","Low"], finish: "Pending Manager Approval" },
            ru: { q: ["Терпение?","Команда?","Давление?","Порядок?","Смены?","Инициатива?","Сервис?","Точность?","Физика?","Почему MAX?"], a: ["Высокая","Средняя","Низкая"], finish: "Ожидает одобрения" },
            ar: { q: ["الصبر؟","فريق؟","ضغط؟","نظام؟","وردية؟","مبادرة؟","خدمة؟","دقة؟","جسدي؟","لماذا MAX؟"], a: ["عالي","متوسط","منخفض"], finish: "بانتظار موافقة المدير" },
            th: { q: ["ความอดทน?","ทีมงาน?","ความกดดัน?","ความเป็นระเบียบ?","กะงาน?","ความคิดริเริ่ม?","การบริการ?","ความตรงต่อเวลา?","ร่างกาย?","ทำไมต้อง MAX?"], a: ["สูง","ปานกลาง","ต่ำ"], finish: "รอการอนุมัติจากผู้จัดการ" }
        };

        function setL(l) { curL = l; if(!document.getElementById('quiz-area').classList.contains('hidden')) goQuiz(); }

        function login() {
            const u = document.getElementById('u').value;
            if(u==='admin') show('ui-sec');
            else if(u==='manager') { show('ui-man'); loadData(); }
        }

        function show(id) { 
            document.querySelectorAll('div[id^="ui-"]').forEach(d=>d.classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden'); 
        }

        function switchTab(t) {
            document.getElementById('tab-c').classList.toggle('hidden', t!=='c');
            document.getElementById('tab-s').classList.toggle('hidden', t!=='s');
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.innerText.includes(t==='c'?'מועמדים':'צוות')));
        }

        function goQuiz() {
            document.getElementById('sec-form').classList.add('hidden');
            const area = document.getElementById('quiz-area'); area.classList.remove('hidden');
            let h = '';
            dict[curL].q.forEach((q, i) => {
                h += `<div style="text-align:right;"><label>${q}</label><select id="ans${i}">`;
                dict[curL].a.forEach(opt => h += `<option>${opt}</option>`);
                h += `</select></div>`;
            });
            h += `<button class="main-btn" onclick="sendAll()">שלח נתונים</button>`;
            area.innerHTML = h;
        }

        async function sendAll() {
            const payload = {
                name: document.getElementById('cName').value,
                dob: document.getElementById('cDob').value,
                ans: Array.from({length:10}, (_,i)=>document.getElementById('ans'+i).value)
            };
            await fetch('/api/save_candidate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
            alert(dict[curL].finish);
            location.reload();
        }

        async function addStaff() {
            const payload = { name: document.getElementById('sName').value, dob: document.getElementById('sDob').value };
            await fetch('/api/add_staff', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) });
            loadData();
        }

        function loadData() {
            fetch('/api/get_all').then(r=>r.json()).then(data => {
                document.getElementById('cTable').innerHTML = data.candidates.reverse().map(c => `
                    <tr><td><b>${c.name}</b><br>${c.dob}</td><td>${c.score}%</td><td>${c.dept}<br><small>${c.job}</small></td><td>${c.rel}</td></tr>
                `).join('');
                document.getElementById('sList').innerHTML = data.staff.map(s => `<div>${s.name} - ${s.dob}</div>`).join('');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/save_candidate', methods=['POST'])
def save_c():
    d = request.json
    n_num = get_name_num(d['name'])
    d_num = get_num(d['dob'])
    
    depts = ["טקסטיל", "כלי בית", "חשמל", "צעצועים", "ניקיון", "פארם", "כלי כתיבה", "ימי הולדת", "יצירה", "כלי עבודה", "ספורט", "רכב", "חיות מחמד"]
    jobs = ["סדרן", "אחראי מחלקה", "מחסנאי", "קופאית", "סגן מנהל", "מנהל"]
    
    d['dept'] = depts[d_num % len(depts)]
    d['job'] = jobs[n_num % len(jobs)]
    d['score'] = 70 + (n_num + d_num) % 30
    d['rel'] = analyze_rel(d['dob'])
    
    save_to_db('candidates.json', d)
    return jsonify({"ok":True})

@app.route('/api/add_staff', methods=['POST'])
def add_s():
    save_to_db('staff.json', request.json)
    return jsonify({"ok":True})

@app.route('/api/get_all')
def get_all():
    return jsonify({
        "candidates": get_db('candidates.json'),
        "staff": get_db('staff.json')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
