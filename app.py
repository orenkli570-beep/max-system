import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# --- לוגיקה נומרולוגית מורחבת (הגילוי הפנימי) ---
def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def calculate_match(c_dob, c_name, target_dept, target_job):
    """חישוב אחוז התאמה לפי סוג התפקיד והמחלקה"""
    d_num = get_num(c_dob)
    n_num = sum([ord(c) for c in c_name]) % 9 + 1
    
    # לוגיקה בסיסית: תפקידי ניהול דורשים מספרים מסוימים
    base_score = 70
    if target_job in ["מנהל סניף", "אחראי משמרת"] and d_num in [1, 8, 22]: base_score += 15
    if target_dept in ["כלי עבודה", "חשמל"] and d_num in [4, 7]: base_score += 10
    if target_job == "קופאית" and d_num in [2, 6]: base_score += 12
    
    return min(98, base_score + (n_num % 5))

# --- ממשק HTML מודרני למנהל ---
HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX - ניהול הון אנושי</title>
    <style>
        :root { --max-red: #e31e24; --slate: #1e293b; }
        body { font-family: 'Assistant', sans-serif; background: #f1f5f9; margin: 0; padding: 20px; direction: rtl; }
        .card { background: white; max-width: 1100px; margin: auto; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        h1 { color: var(--max-red); border-bottom: 3px solid var(--max-red); display: inline-block; padding-bottom: 5px; }
        .tabs { display: flex; gap: 10px; margin-top: 20px; border-bottom: 2px solid #ddd; }
        .tab { padding: 10px 20px; cursor: pointer; border-radius: 8px 8px 0 0; background: #e2e8f0; }
        .tab.active { background: var(--max-red); color: white; font-weight: bold; }
        
        .grid-tool { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; background: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        select, input { padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; width: 100%; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; border: 1px solid #e2e8f0; text-align: center; }
        th { background: var(--slate); color: white; }
        .score-badge { padding: 5px 10px; border-radius: 20px; font-weight: bold; color: white; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>MAX - מרכז שליטה למנהל</h1>
        
        <div class="tabs">
            <div class="tab active" id="t1" onclick="showTab(1)">גיוס והתאמה</div>
            <div class="tab" id="t2" onclick="showTab(2)">צוות ותיק וסינרגיה</div>
        </div>

        <div id="view1" class="tab-view">
            <h3>בדיקת התאמה לתפקיד</h3>
            <div class="grid-tool">
                <select id="selCand"></select>
                <select id="selDept">
                    <option>כלי עבודה</option><option>טקסטיל</option><option>כלי בית</option>
                    <option>חשמל</option><option>צעצועים</option><option>ניקיון</option>
                    <option>פארם</option><option>כלי כתיבה</option><option>ימי הולדת</option>
                    <option>יצירה</option><option>ספורט</option><option>רכב</option><option>חיות מחמד</option>
                </select>
                <select id="selJob">
                    <option>מנהל סניף</option><option>סגן מנהל</option><option>אחראי משמרת</option>
                    <option>אחראי מחלקה</option><option>קופאית</option><option>מחסנאי</option><option>סדרן</option>
                </select>
            </div>
            <button onclick="runCheck()" style="width:100%; background:var(--max-red); color:white; padding:15px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">חשב אחוז התאמה</button>
            
            <div id="matchResult" style="margin-top:20px; font-size:24px; text-align:center;"></div>
            <div id="cTable"></div>
        </div>

        <div id="view2" class="tab-view hidden">
            <h3>סינרגיה בין עובדים (הצלבה)</h3>
            <div class="grid-tool">
                <select id="syn1"></select>
                <select id="syn2"></select>
                <button onclick="checkSync()" style="background:black; color:white; border:none; border-radius:8px; cursor:pointer;">בדוק חיבור</button>
            </div>
            <div id="synResult" style="padding:20px; background:#fff1f2; border-radius:10px; border:1px solid var(--max-red);" class="hidden"></div>
        </div>
    </div>

    <script>
        let candidates = [];
        let staff = [];

        async function loadData() {
            const r = await fetch('/api/get_all');
            const data = await r.json();
            candidates = data.candidates;
            staff = data.staff;
            
            // עדכון רשימות לבחירה
            const all = [...candidates, ...staff];
            const opts = all.map(p => `<option value="${p.dob}|${p.name}">${p.name}</option>`).join('');
            document.getElementById('selCand').innerHTML = opts;
            document.getElementById('syn1').innerHTML = opts;
            document.getElementById('syn2').innerHTML = opts;
            
            renderTable();
        }

        function runCheck() {
            const [dob, name] = document.getElementById('selCand').value.split('|');
            const dept = document.getElementById('selDept').value;
            const job = document.getElementById('selJob').value;
            
            fetch('/api/calculate_match', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({dob, name, dept, job})
            }).then(r=>r.json()).then(res => {
                document.getElementById('matchResult').innerHTML = `
                    <div style="padding:20px; border-radius:15px; background:#f0fdf4;">
                        התאמה של <b>${res.name}</b> לתפקיד <b>${res.job}</b> במחלקת <b>${res.dept}</b>: 
                        <span style="color:var(--max-red); font-size:40px;">${res.score}%</span>
                    </div>
                `;
            });
        }

        async function checkSync() {
            const dob1 = document.getElementById('syn1').value.split('|')[0];
            const dob2 = document.getElementById('syn2').value.split('|')[0];
            const r = await fetch('/api/check_synergy', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({dob1, dob2})
            });
            const res = await r.json();
            const div = document.getElementById('synResult');
            div.classList.remove('hidden');
            div.innerHTML = `<strong>תוצאת סינרגיה:</strong><br>${res.result}`;
        }

        function showTab(n) {
            document.querySelectorAll('.tab-view').forEach(v => v.classList.add('hidden'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('view'+n).classList.remove('hidden');
            document.getElementById('t'+n).classList.add('active');
        }

        loadData();
    </script>
</body>
</html>
"""

@app.route('/api/calculate_match', methods=['POST'])
def api_calc():
    d = request.json
    score = calculate_match(d['dob'], d['name'], d['dept'], d['job'])
    return jsonify({"score": score, "name": d['name'], "dept": d['dept'], "job": d['job']})

@app.route('/api/get_all')
def get_all():
    # פונקציה שמחזירה את כל המועמדים והעובדים השמורים
    return jsonify({
        "candidates": get_db('candidates.json'),
        "staff": get_db('staff.json')
    })

# ... שאר הפונקציות (get_db, save_to_db, check_synergy) נשארות כפי שהיו בגרסאות הקודמות
