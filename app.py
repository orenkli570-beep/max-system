import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- לוגיקה של הגילוי הפנימי ---
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

def calculate_dob_num(dob_str):
    digits = [int(d) for d in dob_str if d.isdigit()]
    if not digits: return 0
    total = sum(digits)
    while total > 9 and total not in [11, 22]:
        total = sum(int(digit) for digit in str(total))
    return total

def save_candidate(data):
    file_path = 'candidates.json'
    existing = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    existing.append(data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=4)

# --- ממשק משתמש ---
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX Recruitment</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; direction: rtl; text-align: center; padding: 20px; }
        .box { background: white; max-width: 600px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h1 { color: #e31e24; font-size: 2.2rem; margin-bottom: 5px; }
        h2 { color: #475569; font-size: 1.2rem; border-bottom: 2px solid #e31e24; padding-bottom: 10px; margin-bottom: 25px; }
        .field { text-align: right; margin-bottom: 15px; }
        label { font-weight: bold; display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }
        button { background: #e31e24; color: white; border: none; padding: 15px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 1.1rem; margin-top: 20px; }
        .hidden { display: none; }
        .q-row { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-right: 4px solid #e31e24; text-align: right; }
    </style>
</head>
<body>
    <div class="box">
        <h1>MAX כאן קונים בכיף</h1>
        <h2>מערכת גיוס והתאמת עובדים</h2>

        <div id="step1">
            <div class="field">
                <label>שם המועמד (פרטי בלבד):</label>
                <input type="text" id="cName" placeholder="הכנס שם פרטי">
            </div>
            <div class="field">
                <label>תאריך לידה:</label>
                <input type="text" id="cDob" placeholder="למשל: 01.01.1990">
            </div>
            <button onclick="showStep2()">המשך לשאלון התאמה</button>
        </div>

        <div id="step2" class="hidden">
            <div id="questions-container"></div>
            <button onclick="finalize()">שלח נתונים לניתוח</button>
        </div>

        <div id="success" class="hidden">
            <h3 style="color: green;">✓ הנתונים נשלחו בהצלחה למנהל</h3>
            <button onclick="location.reload()">מועמד חדש</button>
        </div>
    </div>

    <script>
        const questions = [
            "מידת הסבלנות שלך בעבודה עם לקוחות?",
            "איך היכולת שלך לעבוד בצוות?",
            "מהי רמת העמידה שלך במצבי לחץ?",
            "עד כמה חשוב לך סדר וארגון בסביבת העבודה?",
            "מהי הזמינות שלך למשמרות (בוקר/ערב/לילה)?",
            "מידת היוזמה האישית שלך להגדלת ראש?",
            "איך היית מגדיר את תודעת השירות שלך?",
            "מידת הדייקנות שלך בזמנים?",
            "האם יש לך יכולת לעבודה פיזית מתונה?",
            "מהי המוטיבציה שלך לעבוד דווקא ב-MAX?"
        ];

        function showStep2() {
            if(!document.getElementById('cName').value || !document.getElementById('cDob').value) {
                alert("אנא מלא שם ותאריך לידה");
                return;
            }
            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step2').classList.remove('hidden');
            
            let html = "";
            questions.forEach((q, i) => {
                html += `
                <div class="q-row">
                    <label>${i+1}. ${q}</label>
                    <select id="q${i}">
                        <option value="גבוהה">גבוהה</option>
                        <option value="בינונית">בינונית</option>
                        <option value="נמוכה">נמוכה</option>
                    </select>
                </div>`;
            });
            document.getElementById('questions-container').innerHTML = html;
        }

        async function finalize() {
            const name = document.getElementById('cName').value;
            const dob = document.getElementById('cDob').value;
            const answers = [];
            for(let i=0; i<10; i++) {
                answers.push(document.getElementById('q'+i).value);
            }

            const res = await fetch('/api/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name, dob, answers })
            });

            if(res.ok) {
                document.getElementById('step2').classList.add('hidden');
                document.getElementById('success').classList.remove('hidden');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CONTENT)

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    name = data['name']
    dob = data['dob']
    
    # חישוב הנתונים של הגילוי הפנימי
    name_num = calculate_name_num(name)
    dob_num = calculate_dob_num(dob)
    
    record = {
        "name": name,
        "dob": dob,
        "answers": data['answers'],
        "name_num": name_num,
        "dob_num": dob_num
    }
    
    save_candidate(record)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
