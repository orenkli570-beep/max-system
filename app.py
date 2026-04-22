import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# פונקציית חישוב נוסחת השם (גימטריה מצומצמת)
def calculate_name_num(name):
    gematria_map = {
        'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
        'י': 1, 'כ': 2, 'ל': 3, 'מ': 4, 'נ': 5, 'ס': 6, 'ע': 7, 'פ': 8, 'צ': 9,
        'ק': 1, 'ר': 2, 'ש': 3, 'ת': 4, 'ך': 2, 'ם': 4, 'ן': 5, 'ף': 8, 'ץ': 9
    }
    total = sum(gematria_map.get(char, 0) for char in name)
    while total > 9 and total not in [11, 22]:
        total = sum(int(digit) for digit in str(total))
    return total

# פונקציית חישוב תאריך לידה (ספרות 1-9 ומאסטר)
def calculate_dob_num(dob_str):
    digits = [int(d) for d in dob_str if d.isdigit()]
    total = sum(digits)
    while total > 9 and total not in [11, 22]:
        total = sum(int(digit) for digit in str(total))
    return total

def load_data():
    if not os.path.exists('candidates.json'): return []
    try:
        with open('candidates.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_data(data):
    with open('candidates.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX - Internal Discovery System</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f9; direction: rtl; padding: 20px; }
        .card { background: white; max-width: 1000px; margin: auto; padding: 25px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; text-align: center; }
        .hidden { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }
        th { background: #f8fafc; }
        .master-num { color: #e31e24; font-weight: bold; }
        .result-box { background: #e0f2fe; padding: 5px; border-radius: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX - ניתוח נתונים משולב</h1>
        
        <div id="ui-login">
            <input type="text" id="u" placeholder="שם משתמש" style="width:100%; padding:10px; margin:5px 0;">
            <input type="password" id="p" placeholder="סיסמה" style="width:100%; padding:10px; margin:5px 0;">
            <button onclick="login()" style="width:100%; padding:10px; background:#e31e24; color:white; border:none; cursor:pointer;">כניסה</button>
        </div>

        <div id="ui-admin" class="hidden">
            <h3>הזנת מועמד</h3>
            <input type="text" id="cName" placeholder="שם פרטי (ללא משפחה)" style="width:100%; padding:10px; margin:5px 0;">
            <input type="text" id="cDob" placeholder="תאריך לידה (למשל: 12.05.1990)" style="width:100%; padding:10px; margin:5px 0;">
            <button onclick="startQuiz()" style="width:100%; padding:10px; background:#e31e24; color:white; border:none; cursor:pointer;">המשך לשאלון</button>
        </div>

        <div id="ui-quiz" class="hidden">
            <div id="qArea"></div>
            <button onclick="submit()" style="width:100%; padding:10px; background:#e31e24; color:white; border:none; cursor:pointer;">סיים ונתח נתונים</button>
        </div>

        <div id="ui-manager" class="hidden">
            <h3>לוח מנהל - ניתוח אישיות ונוסחת השם</h3>
            <table>
                <thead>
                    <tr>
                        <th>מועמד</th>
                        <th>תאריך לידה</th>
                        <th>ספרת שם</th>
                        <th>ספרת גורל</th>
                        <th>מחלקה מומלצת</th>
                        <th>אחוז התאמה</th>
                    </tr>
                </thead>
                <tbody id="mTable"></tbody>
            </table>
            <button onclick="location.reload()" style="margin-top:20px;">התנתק</button>
        </div>
    </div>

    <script>
        function login() {
            const u = document.getElementById('u').value;
            const p = document.getElementById('p').value;
            if(u==='admin' && p==='max456') { show('ui-admin'); }
            else if(u==='manager' && p==='max123') { show('ui-manager'); loadM(); }
        }

        function show(id) {
            document.querySelectorAll('div[id^="ui-"]').forEach(d => d.classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden');
        }

        function startQuiz() {
            show('ui-quiz');
            // כאן יופיעו 10 השאלות שדיברנו עליהן...
            document.getElementById('qArea').innerHTML = "<h4>שאלון בטעינה...</h4>";
            setTimeout(() => {
                let h = '';
                for(let i=0; i<10; i++) { h += `<p>שאלה ${i+1}: <select id="a${i}"><option>גבוהה</option><option>בינונית</option><option>נמוכה</option></select></p>`; }
                document.getElementById('qArea').innerHTML = h;
            }, 100);
        }

        async function submit() {
            const ans = [];
            for(let i=0; i<10; i++) ans.push(document.getElementById('a'+i).value);
            
            const payload = {
                name: document.getElementById('cName').value,
                dob: document.getElementById('cDob').value,
                ans: ans
            };

            await fetch('/api/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            alert("נשלח לניתוח");
            location.reload();
        }

        function loadM() {
            fetch('/api/list').then(r => r.json()).then(data => {
                document.getElementById('mTable').innerHTML = data.map(c => `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.dob}</td>
                        <td class="${[11,22].includes(c.nameNum) ? 'master-num' : ''}">${c.nameNum}</td>
                        <td class="${[11,22].includes(c.dobNum) ? 'master-num' : ''}">${c.dobNum}</td>
                        <td><span class="result-box">${c.recDept}</span></td>
                        <td><b>${c.score}%</b></td>
                    </tr>
                `).join('');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_CONTENT)

@app.route('/api/list')
def get_l(): return jsonify(load_data())

@app.route('/api/save', methods=['POST'])
def save():
    d = load_data()
    item = request.json
    # חישוב הנתונים לפי "הגילוי הפנימי" בשרת
    item['nameNum'] = calculate_name_num(item['name'])
    item['dobNum'] = calculate_dob_num(item['dob'])
    
    # לוגיקה בסיסית לשילוב (מחלקה מומלצת לפי ספרת גורל)
    mapping = {1: "ניהול/סגן", 2: "שירות/קופאית", 4: "כלי עבודה/מחסן", 8: "ניהול מחסן"}
    item['recDept'] = mapping.get(item['dobNum'], "כללי/סדרן")
    item['score'] = 85 # דוגמה לשקלול
    
    d.append(item)
    save_data(d)
    return jsonify({"s":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
