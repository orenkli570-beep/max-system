import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

# פונקציית ניתוח מקיפה המשלבת אופי + אינטראקציה (עברית בלבד)
def generate_manager_insights(data):
    num = get_num(data['dob'])
    # זיהוי איכות התשובות (ראש גדול/ראש קטן)
    is_proactive = sum(1 for a in data['answers'] if a['idx'] == "1") > 10
    
    traits = {
        1: "טיפוס מנהיגותי, דורש מרחב פעולה ועצמאות.",
        2: "טיפוס שירותי מאוד, זקוק לסביבה הרמונית ועבודת צוות.",
        3: "תקשורתי ודינמי, פורח באינטראקציה עם לקוחות.",
        4: "יסודי ומדויק, מעדיף סדר קבוע ונהלים ברורים.",
        5: "זריז וסתגלן, מתאים לשינויים מהירים במשימות.",
        6: "אחראי ומשפחתי, רואה את טובת החנות כערך עליון.",
        7: "מעמיק ושקט, זקוק להוראות ברורות ולא אוהב רעש מיותר.",
        8: "עמיד בלחץ, משימתי מאוד וקר רוח במצבי דוחק.",
        9: "אדיב וסבלני, ניחן ביכולת הקשבה גבוהה ללקוחות קשים.",
        11: "בעל אינטואיציה גבוהה, קורא אנשים ומצבים במהירות.",
        22: "בעל יכולת ביצוע מרשימה, מסוגל להוביל פרויקטים גדולים (כמו סידור מחלקה מאפס)."
    }
    
    trait_desc = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות גבוהה.")
    
    # ניתוח אינטראקציה מנהל-עובד
    interaction = "המנהל נדרש לתת לעובד זה "
    if is_proactive:
        interaction += "אוטונומיה וגיבוי ליוזמות אישיות. מומלץ לתת לו משימות 'ראש גדול' כי הוא יחפש עבודה גם כשאין עומס."
    else:
        interaction += "הנחיות ברורות ופיקוח צמוד יותר. העובד יבצע את המוטל עליו בצורה טובה אך זקוק להגדרת משימות מסודרת."

    return {
        "character": trait_desc,
        "interaction": interaction,
        "recommendation": "מומלץ לשבץ ב" + ("מחלקות הדורשות תקתוק עבודה (מחסן/פלסטיקה)" if is_proactive else "מחלקות שירותיות שקטות (כתיבה/ביוטי)")
    }

HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX Manager Portal</title>
    <style>
        :root { --red: #e31e24; --blue: #1e40af; --bg: #f1f5f9; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); margin: 0; direction: rtl; }
        .header { background: white; padding: 20px; text-align: center; border-bottom: 5px solid var(--red); }
        .container { max-width: 950px; margin: 20px auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .card { background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        .hidden { display: none; }
        
        h2, h3 { color: var(--blue); border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .insight-section { margin: 15px 0; padding: 15px; border-right: 4px solid var(--red); background: #fdf2f2; }
        .insight-label { font-weight: bold; color: var(--red); display: block; margin-bottom: 5px; }
        
        select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 16px; }
        .btn-save { background: #059669; color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-save:hover { background: #047857; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: #f8fafc; color: #64748b; }
    </style>
</head>
<body>
    <div class="header"><h1>מערכת ניהול מועמדים - צד מנהל</h1></div>
    <div class="container">
        
        <div id="login-area">
            <input type="password" id="pass" placeholder="קוד גישה מנהל">
            <button class="btn-save" style="background:var(--red);" onclick="checkLogin()">כניסה למערכת</button>
        </div>

        <div id="manager-content" class="hidden">
            <div class="card">
                <h3>ניתוח מועמדים ואינטראקציה</h3>
                <label>בחר שם מועמד:</label>
                <select id="candSelect" onchange="loadAnalysis()"></select>
                
                <div id="analysisDisplay">
                    <div class="insight-section">
                        <span class="insight-label">ניתוח אופי המועמד:</span>
                        <div id="charDesc"></div>
                    </div>
                    <div class="insight-section" style="border-right-color: var(--blue); background: #f0f7ff;">
                        <span class="insight-label" style="color:var(--blue);">פרוטוקול אינטראקציה (מנהל-עובד):</span>
                        <div id="interDesc"></div>
                    </div>
                    <div class="insight-section" style="border-right-color: #059669; background: #f0fdf4;">
                        <span class="insight-label" style="color:#059669;">המלצה מקצועית:</span>
                        <div id="recomDesc"></div>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                    <select id="deptSet">
                        <option value="">קבע מחלקה</option>
                        <option>פלסטיקה</option><option>ביוטי</option><option>דקורציה</option>
                        <option>עונה</option><option>כלי מטבח</option><option>יצירה</option>
                    </select>
                    <select id="jobSet">
                        <option value="">קבע תפקיד</option>
                        <option>סדרן/ית</option><option>קופאי/ת</option><option>אחראי מחלקה</option>
                    </select>
                </div>
                <button class="btn-save" onclick="saveToDB()">שמירה ושיבוץ במערכת</button>
            </div>

            <div class="card">
                <h3>רשימת צוות מעודכנת</h3>
                <table>
                    <thead><tr><th>שם</th><th>מחלקה</th><th>תפקיד</th></tr></thead>
                    <tbody id="staffTable"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let currentCandidates = [];

        function checkLogin() {
            if(document.getElementById('pass').value === 'admin456') {
                document.getElementById('login-area').classList.add('hidden');
                document.getElementById('manager-content').classList.remove('hidden');
                refreshData();
            }
        }

        async function refreshData() {
            const res = await fetch('/api/get');
            currentCandidates = await res.json();
            const sel = document.getElementById('candSelect');
            sel.innerHTML = currentCandidates.map((c, i) => `<option value="${i}">${c.firstName}</option>`).join('');
            
            document.getElementById('staffTable').innerHTML = currentCandidates.map(c => `
                <tr><td>${c.firstName}</td><td>${c.dept || '---'}</td><td>${c.job || '---'}</td></tr>
            `).join('');
            
            if(currentCandidates.length > 0) loadAnalysis();
        }

        function loadAnalysis() {
            const idx = document.getElementById('candSelect').value;
            const cand = currentCandidates[idx];
            document.getElementById('charDesc').innerText = cand.insights.character;
            document.getElementById('interDesc').innerText = cand.insights.interaction;
            document.getElementById('recomDesc').innerText = cand.insights.recommendation;
        }

        async function saveToDB() {
            const idx = document.getElementById('candSelect').value;
            const data = {
                index: idx,
                dept: document.getElementById('deptSet').value,
                job: document.getElementById('jobSet').value
            };
            await fetch('/api/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            alert("הנתונים נשמרו בהצלחה");
            refreshData();
        }
    </script>
</body>
</html>
"""

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    # יצירת התובנות מראש בשלב השמירה
    d['insights'] = generate_manager_insights(d)
    # ... לוגיקת שמירה ל-JSON ...
    return jsonify({"ok": True})
