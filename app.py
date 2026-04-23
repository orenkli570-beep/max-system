import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- לוגיקה עסקית (ללא שינוי) ---
DEPARTMENTS = ["פלסטיקה", "ביוטי", "דקורציה", "עונה", "כלי מטבח", "יצירה", "צעצועים", "טקסטיל", "ניקיון", "חזרה לבית הספר", "מחסן", "חשמל", "קופות"]
ROLES = ["סדרן/ית", "קופאי/ת", "מחסנאי/ת", "סגן/ית מנהל", "אחראי/ת משמרת", "אחראי/ת מחלקה", "מלגזן/ית", "עובד/ת ניקיון", "נציג/ת שירות", "בודק/ת חשבוניות", "אחראי/ת החזרות", "סופר/ת מלאי", "מתפעל/ת מבצעים", "עובד/ת לילה", "תומך/ת טכני"]

def generate_full_analysis(data):
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    if counts['A'] >= 8:
        char_text = "מועמד בעל יוזמה יוצאת דופן. מזהה הזדמנויות לשיפור באופן עצמאי. אנרגטי וביצועיסט."
    elif counts['B'] >= 8:
        char_text = "מועמד שירותי במיוחד. רואה את הלקוח במרכז, סבלני מאוד ונעים הליכות."
    else:
        char_text = "עובד משימתי וממוקד. מצטיין בדיוק, עקביות וביצוע מטלות שגרתיות ברמה גבוהה."

    if counts['B'] + counts['A'] >= 10:
        social_text = "שחקן נשמה. תורם המון לאווירה בצוות, עוזר לאחרים בטבעיות ומונע חיכוכים."
    else:
        social_text = "עצמאי וממוקד. מעדיף 'שקט תעשייתי', עבודה בגיזרה שלו ופחות אינטראקציה חברתית."

    if counts['A'] >= 7:
        manager_text = "ניהול באמון: תן לו את האחריות ושחרר. הוא יביא תוצאות טובות יותר תחת ניהול עצמאי."
    else:
        manager_text = "ניהול תומך: זקוק להנחיות ברורות וסדר יום מוגדר. מומלץ שימוש ברשימות צ'ק-ליסט."

    return {"character": char_text, "social": social_text, "manager_protocol": manager_text}

# --- ממשק משתמש משודרג ---
INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX STOCK | מערכת ניהול חכמה</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --max-red: #e31e24;
            --max-red-dark: #b91c1c;
            --max-blue: #1e3a8a;
            --bg: #f3f4f6;
            --card-bg: #ffffff;
            --text: #1f2937;
        }

        body {
            font-family: 'Heebo', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, var(--max-red) 0%, var(--max-red-dark) 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-bottom-left-radius: 40px;
            border-bottom-right-radius: 40px;
        }

        .header h1 { margin: 0; font-weight: 900; font-size: 2.5rem; letter-spacing: -1px; }
        .header p { margin-top: 10px; opacity: 0.9; font-weight: 300; }

        .container {
            max-width: 800px;
            width: 90%;
            margin: -30px auto 50px auto;
        }

        .glass-card {
            background: var(--card-bg);
            border-radius: 24px;
            padding: 35px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.8);
        }

        /* פס התקדמות */
        .progress-container {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 10px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        .progress-bar {
            width: 0%;
            height: 100%;
            background: var(--max-red);
            transition: width 0.4s ease;
        }

        .question-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .question-card:hover { transform: translateY(-2px); border-color: var(--max-red); }
        .question-card b { display: block; margin-bottom: 12px; font-size: 1.1rem; color: var(--max-blue); }

        select, input {
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: 2px solid #e5e7eb;
            font-size: 1rem;
            outline: none;
            transition: 0.2s;
            font-family: 'Heebo', sans-serif;
        }
        select:focus, input:focus { border-color: var(--max-red); }

        .btn {
            cursor: pointer;
            border: none;
            border-radius: 14px;
            padding: 16px 30px;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s;
            font-family: 'Heebo', sans-serif;
            width: 100%;
        }
        .btn-primary { background: var(--max-red); color: white; box-shadow: 0 4px 14px rgba(227, 30, 36, 0.3); }
        .btn-primary:hover { background: var(--max-red-dark); transform: translateY(-2px); }

        .insight-box {
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 15px;
            border-right: 6px solid var(--max-red);
            background: #fff5f5;
        }

        .hidden { display: none; }

        /* אנימציות כניסה */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeIn 0.5s ease forwards; }

    </style>
</head>
<body>

<div class="header">
    <h1>MAX STOCK</h1>
    <p>מערכת חכמה לניהול חוויית העובד</p>
</div>

<div class="container fade-in">
    <div class="glass-card">
        
        <div id="login-view">
            <h2 style="text-align: center;">ברוכים הבאים</h2>
            <button class="btn btn-primary" onclick="showSec()">התחל שאלון מועמד</button>
            <div style="margin-top: 40px; border-top: 1px solid #eee; padding-top: 30px;">
                <input type="password" id="mPass" placeholder="קוד כניסת מנהל">
                <button class="btn" style="background: var(--max-blue); color:white; margin-top:10px;" onclick="showMan()">כניסת מנהל לניתוח</button>
            </div>
        </div>

        <div id="sec-view" class="hidden">
            <div class="progress-container"><div class="progress-bar" id="pBar"></div></div>
            <div id="quizArea"></div>
            <div class="question-card" style="background: #eff6ff;">
                <b>פרטים אישיים</b>
                <input type="text" id="cName" placeholder="שם מלא">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)" style="margin-top:10px;">
            </div>
            <button class="btn btn-primary" onclick="submitQuiz()">שלח שאלון לאישור</button>
        </div>

        <div id="man-view" class="hidden">
            <h2 style="color: var(--max-blue);">ניתוח והמלצות ניהול</h2>
            <select id="candSelect" onchange="render()" style="margin-bottom: 25px;"></select>
            
            <div id="insArea">
                <div class="insight-box"><b><span style="color:var(--max-red)">●</span> דיוקן אישיותי</b><div id="cBox" style="margin-top:8px;"></div></div>
                <div class="insight-box" style="border-color: var(--max-blue); background: #f0f7ff;"><b><span style="color:var(--max-blue)">●</span> אינטראקציה חברתית</b><div id="sBox" style="margin-top:8px;"></div></div>
                <div class="insight-box" style="border-color: #10b981; background: #f0fdf4;"><b><span style="color:#10b981;">●</span> פרוטוקול מנהל-עובד</b><div id="mBox" style="margin-top:8px;"></div></div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-top:20px;">
                <select id="dSet">""" + "".join([f"<option>{d}</option>" for d in DEPARTMENTS]) + """</select>
                <select id="jSet">""" + "".join([f"<option>{r}</option>" for r in ROLES]) + """</select>
            </div>
            <button class="btn" style="background: #10b981; color:white; margin-top:15px;">שמור שיבוץ למערכת</button>
            <button onclick="location.reload()" style="background:none; color:#6b7280; text-decoration:underline; font-size:0.9rem; margin-top:20px;">יציאה וחזרה לתפריט</button>
        </div>

    </div>
</div>

<script>
    const questions = [
        {q: "לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a: "אבדוק מיד במחסן ואנסה להביא לו", b: "אבדוק במחשב או אשאל את האחראי", c: "אעדכן אותו שכרגע חסר במלאי", d: "אמשיך בעבודה שלי כרגיל"},
        {q: "יש תור ארוך בקופות ואתה בסידור מדף, מה תגובתך?", a: "אגש מיד לעזור בקופה בלי שיבקשו", b: "אחכה שיקראו לי לעזור לעמיתים", c: "אמשיך לסדר כי זה התפקיד שהוגדר לי", d: "אלך למחסן כדי להימנע מהעומס"},
        {q: "ראית מוצר שבור שנשפך על הרצפה במעבר?", a: "אנקה מיד ואדאג שהמעבר יהיה בטוח", b: "אשים סימון ואדווח למנהל המשמרת", c: "אקרא לעובד הניקיון שיטפל בזה", d: "אעקוף את זה ואמשיך בסידור המדף"},
        {q: "לקוח צועק עליך בגלל מחיר של מוצר?", a: "אקשיב לו בסבלנות ואנסה להרגיע בחיוך", b: "אקרא מיד למנהל שיפתור את הבעיה", c: "אגיד לו שזה המחיר ואין לי מה לעשות", d: "אתעלם ואעבור לעבוד באזור אחר"},
        {q: "המנהל מבקש ממך לעשות משימה שאתה לא אוהב?", a: "אבצע אותה הכי טוב שאפשר ובמהירות", b: "אבצע את המשימה ואז אבקש לגוון", c: "אעשה אותה לאט כדי שלא יבקשו שוב", d: "אנסה להסביר למה עדיף שמישהו אחר יעשה"},
        {q: "גילית שחבר לעבודה טעה בסידור המחלקה שלו?", a: "אעזור לו לתקן את הטעות בנעימות", b: "אסב את תשומת ליבו לטעות שעשה", c: "אלך לעדכן את המנהל על חוסר הדיוק", d: "זה לא ענייני, אני מרוכז רק בשלי"},
        {q: "הגעת למשמרת והמחלקה הפוכה לגמרי?", a: "אתחיל לסדר מיד לפי מה שהכי דחוף", b: "אשאל את המנהל מאיפה הכי כדאי להתחיל", c: "אסדר רק את החלק הקטן שבו אני עובד", d: "אחכה שהמנהל ייתן לי הוראות מפורטות"},
        {q: "לקוח מתלבט לגבי מתנה ולא יודע מה לבחור?", a: "אציע לו כמה אפשרויות ואעזור לו להחליט", b: "אכוון אותו לאזור המתנות הפופולריות", c: "אגיד לו שקשה להמליץ כי זה עניין של טעם", d: "אפנה אותו לעובד אחר שפנוי לזה"},
        {q: "מצאת שטר כסף על הרצפה באמצע החנות?", a: "אמסור אותו מיד למנהל או לקופה הראשית", b: "אשאל לקוחות קרובים אם איבדו כסף", c: "אשים בקופת צדקה ליד הקופה", d: "אכניס לכיס ואחליט מה לעשות בסוף"},
        {q: "איך אתה הכי אוהב שעובדים איתך?", a: "שנותנים לי משימה ואחריות ואני רץ לבד", b: "בשיתוף פעולה מלא עם כל הצוות", c: "שיש מנהל שאומר לי בדיוק מה לעשות", d: "לעבוד לבד בשקט ובלי שאף אחד יפריע"},
        {q: "לקוח דורש הנחה שאתה יודע שאי אפשר לתת?", a: "אסביר לו בנימוס את מדיניות הרשת", b: "אבדוק אם יש מבצע אחר שיוכל לעזור לו", c: "אשלח אותו למנהל שיחליט בעצמו", d: "אגיד לו 'לא' בצורה קצרה ופשוטה"},
        {q: "שמת לב שסימנת מחירים לא נכונים על סחורה?", a: "אתקן הכל מיד ואדווח על הטעות שלי", b: "אשאל את המנהל איך כדאי לתקן את זה", c: "אקווה שזה יעבור בשקט בלי שירגישו", d: "אשאיר את זה ככה, זה לא נורא"},
        {q: "המשמרת נגמרה אבל החנות מלאה בלקוחות?", a: "אשאר לעזור עוד קצת עד שהלחץ יירד", b: "אסיים את מה שהתחלתי ואז אלך הביתה", c: "אחתים כרטיס ואצא מיד, העבודה נגמרה", d: "אעלם למחסן כדי שלא יבקשו ממני להישאר"},
        {q: "עובד אחר מבקש ממך לעשות משהו לא תקין?", a: "אסרב ואסביר לו למה זה נגד הנהלים", b: "אדווח למנהל על הבקשה הלא תקינה", c: "אעזור לו הפעם באופן יוצא מן הכלל", d: "אעשה מה שהוא ביקש כדי לא לריב איתו"},
        {q: "מה הדבר שהכי מניע אותך בעבודה?", a: "להצליח, להתקדם ולהיות הכי טוב בסניף", b: "לתת שירות מעולה ולראות לקוח מרוצה", c: "לראות מחלקה מסודרת, נקייה ומתוקתקת", d: "לסיים את היום בשקט ולקבל משכורת"}
    ];

    function updateProgress() {
        let answered = 0;
        for(let i=0; i<questions.length; i++) {
            if(document.getElementById('q'+i).value) answered++;
        }
        document.getElementById('pBar').style.width = (answered/questions.length)*100 + "%";
    }

    function showSec() { 
        document.getElementById('login-view').classList.add('hidden'); 
        document.getElementById('sec-view').classList.remove('hidden'); 
        renderQuiz(); 
    }

    function renderQuiz() {
        let h = "";
        questions.forEach((item, i) => {
            h += `<div class="question-card"><b>${i+1}. ${item.q}</b>
            <select id="q${i}" onchange="updateProgress()">
                <option value="" disabled selected>בחר תשובה...</option>
                <option value="A">${item.a}</option><option value="B">${item.b}</option><option value="C">${item.c}</option><option value="D">${item.d}</option>
            </select></div>`;
        });
        document.getElementById('quizArea').innerHTML = h;
    }

    async function showMan() {
        if(document.getElementById('mPass').value === 'admin456') {
            document.getElementById('login-view').classList.add('hidden');
            document.getElementById('man-view').classList.remove('hidden');
            const r = await fetch('/api/get'); window.cands = await r.json();
            document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
            if(window.cands.length > 0) render();
        } else alert("קוד שגוי");
    }

    function render() {
        const c = window.cands[document.getElementById('candSelect').value];
        document.getElementById('cBox').innerText = c.full_analysis.character;
        document.getElementById('sBox').innerText = c.full_analysis.social;
        document.getElementById('mBox').innerText = c.full_analysis.manager_protocol;
    }

    async function submitQuiz() {
        const name = document.getElementById('cName').value;
        const dob = document.getElementById('cDob').value;
        if(!name || !dob) return alert("נא למלא שם ותאריך לידה");
        const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+i).value }));
        if(answers.some(a => !a.val)) return alert("נא לענות על כל השאלות");
        await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
        alert("תודה! השאלון הועבר למנהל."); location.reload();
    }
</script>
</body>
</html>
"""

# --- API Routes (זהה לקוד הקודם) ---
@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = []
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
