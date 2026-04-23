<!doctype html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מערכת גיוס MAX | הגילוי הפנימי</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root { --max-red: #e31e24; --text-dark: #1e293b; --bg-light: #f8fafc; --success-green: #22c55e; }
        body { font-family: 'Heebo', sans-serif; background: #ffffff; color: var(--text-dark); margin: 0; padding: 20px; display: flex; justify-content: center; }
        .card { width: 100%; max-width: 800px; background: var(--bg-light); border-radius: 15px; padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        header { text-align: center; border-bottom: 2px solid var(--max-red); padding-bottom: 20px; margin-bottom: 25px; }
        
        /* Login */
        #login-screen { max-width: 400px; margin-top: 100px; text-align: center; }
        .login-input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; text-align: center; }
        .login-btn { width: 100%; padding: 12px; background: var(--text-dark); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }

        /* Form Elements */
        .form-group { margin-bottom: 20px; }
        .row { display: flex; gap: 15px; }
        .row > div { flex: 1; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #334155; }
        input, select { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-family: 'Heebo'; font-size: 1rem; }
        .submit-btn { width: 100%; padding: 15px; background: var(--max-red); color: white; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .submit-btn:hover { opacity: 0.9; transform: translateY(-2px); }

        /* Table */
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: var(--text-dark); color: white; }
        
        #questionnaire, #manager-panel, #main-form, #success-screen, #details-view { display: none; }
        .lang-switcher { float: left; background: var(--text-dark); color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
        
        /* Success Box */
        .success-box { text-align: center; padding: 40px 20px; }
        .success-icon { font-size: 60px; color: var(--success-green); margin-bottom: 20px; }
    </style>
</head>
<body>

<div id="login-screen" class="card">
    <h2 style="color: black;">כניסה למערכת MAX</h2>
    <input type="text" id="username" class="login-input" placeholder="User Name">
    <input type="password" id="password" class="login-input" placeholder="Password">
    <button onclick="checkLogin()" class="login-btn">Login</button>
    <p id="login-error" style="color: red; display: none; margin-top: 10px;">פרטים שגויים</p>
</div>

<div id="main-form" class="card">
    <header>
        <select class="lang-switcher" onchange="switchLanguage(this.value)">
            <option value="he">עברית</option>
            <option value="en">English</option>
        </select>
        <h1>גיוס והתאמת עובדים</h1>
        <h2 style="color:var(--max-red)">MAX כאן קונים בכיף</h2>
    </header>

    <div id="step-1">
        <div class="row">
            <div class="form-group"><label id="lbl-fname">שם פרטי:</label><input type="text" id="firstName"></div>
            <div class="form-group"><label id="lbl-lname">שם משפחה:</label><input type="text" id="lastName"></div>
        </div>
        <div class="form-group">
            <label id="lbl-dob">תאריך לידה (הקלדה חופשית):</label>
            <input type="text" id="dob" placeholder="DD/MM/YYYY">
        </div>
        <button onclick="showQuestionnaire()" class="submit-btn" id="btn-next">המשך לשאלון ההתאמה</button>
    </div>

    <div id="questionnaire">
        <h3 style="color: var(--max-red); border-bottom: 1px solid #ddd; padding-bottom: 10px;">שאלון אופי והתאמה</h3>
        <div id="questions-area"></div>
        <button onclick="finishAndSave()" class="submit-btn">סיום ושליחה למנהל</button>
    </div>

    <div id="success-screen" class="success-box">
        <div class="success-icon">✓</div>
        <h2>הנתונים הועברו בהצלחה!</h2>
        <p style="font-size: 1.1rem; color: #64748b;">
            תודה על שיתוף הפעולה. הפרטים נשלחו למנהל לצורך ניתוח ברוח "הגילוי הפנימי". <br>
            <b>אנחנו מאחלים לך המון בהצלחה בדרך החדשה!</b>
        </p>
        <button onclick="location.reload()" class="submit-btn" style="background: var(--text-dark); max-width: 200px;">מועמד חדש</button>
    </div>
</div>

<div id="manager-panel" class="card">
    <header>
        <h1>לוח בקרה לניתוח מועמדים</h1>
        <button onclick="location.reload()" style="background:none; border:none; color:blue; cursor:pointer;">התנתק</button>
    </header>
    <table id="resultsTable">
        <thead>
            <tr>
                <th>שם מלא</th>
                <th>תאריך לידה</th>
                <th>פעולות</th>
            </tr>
        </thead>
        <tbody id="candidates-list"></tbody>
    </table>
    
    <div id="details-view" style="margin-top:30px; padding:20px; border:1px solid #ccc; background:#fff; border-radius:10px;">
        <h3 id="det-name" style="color:var(--max-red)"></h3>
        <p><b>תאריך לידה לניתוח:</b> <span id="det-dob"></span></p>
        <div id="det-answers" style="font-size:0.9rem; line-height:1.6;"></div>
        <button onclick="document.getElementById('details-view').style.display='none'" class="login-btn" style="margin-top:15px;">סגור ניתוח</button>
    </div>
</div>

<script>
    const questions = [
        { q: "איך היית מגדיר/ה את הסבלנות שלך בעבודה?", a: ["גבוהה מאוד", "סבירה", "מאבד/ת סבלנות מהר"] },
        { q: "מה הכי מושך אותך במקום עבודה?", a: ["עבודה עם אנשים", "יציבות ושכר", "אפשרויות קידום"] },
        { q: "איך את/ה מתמודד/ה עם עבודה תחת לחץ?", a: ["מתפקד/ת מצוין", "שומר/ת על קור רוח", "מעדיף/ה קצב רגוע"] },
        { q: "עד כמה חשוב לך סדר וארגון בסביבה?", a: ["קריטי מאוד", "חשוב במידה סבירה", "זורם/ת עם המצב"] },
        { q: "מהי זמינות העבודה המועדפת עליך?", a: ["משמרות בוקר", "משמרות ערב", "גמיש/ה להכל"] },
        { q: "איך את/ה מגיב/ה לשינויים פתאומיים בלו''ז?", a: ["מקבל/ת בגמישות", "זקוק/ה לזמן הסתגלות", "מעדיף/ה הודעה מראש"] },
        { q: "מהי התכונה הכי חשובה לעובד ב-MAX?", a: ["שירותיות וחיוך", "מהירות ויעילות", "אמינות ואחריות"] },
        { q: "האם את/ה מעדיף/ה עבודה פיזית או משרדית?", a: ["אוהב/ת תנועה (פיזי)", "מעדיף/ה ישיבה", "שילוב של שניהם"] },
        { q: "אם תראה/י לקוח שזקוק לעזרה, מה תעשה/י?", a: ["אגש מיד בחיוך", "אחכה שיפנה אליי", "אקרא לעובד אחר"] },
        { q: "איך את/ה רואה את המחויבות שלך למקום העבודה?", a: ["לטווח ארוך", "לשנה הקרובה", "עבודה זמנית"] }
    ];

    function checkLogin() {
        const u = document.getElementById('username').value.toLowerCase();
        const p = document.getElementById('password').value;
        if (u === 'manager' && p === 'max123') {
            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('manager-panel').style.display = 'block';
            loadCandidates();
        } else if (u === 'admin' && p === 'max456') {
            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('main-form').style.display = 'block';
            buildQuestions();
        } else { document.getElementById('login-error').style.display = 'block'; }
    }

    function buildQuestions() {
        let html = '';
        questions.forEach((item, index) => {
            html += `<div class="form-group"><label>${index + 1}. ${item.q}</label><select id="q${index}">`;
            item.a.forEach(opt => html += `<option value="${opt}">${opt}</option>`);
            html += `</select></div>`;
        });
        document.getElementById('questions-area').innerHTML = html;
    }

    function showQuestionnaire() {
        if(document.getElementById('firstName').value && document.getElementById('dob').value) {
            document.getElementById('step-1').style.display = 'none';
            document.getElementById('questionnaire').style.display = 'block';
        } else { alert("נא למלא פרטי מועמד"); }
    }

    function finishAndSave() {
        const candidate = {
            id: Date.now(),
            name: document.getElementById('firstName').value + " " + document.getElementById('lastName').value,
            dob: document.getElementById('dob').value,
            answers: questions.map((_, i) => ({ q: questions[i].q, a: document.getElementById('q'+i).value }))
        };

        // שמירה ל-LocalStorage (זיכרון דפדפן)
        let list = JSON.parse(localStorage.getItem('max_db') || '[]');
        list.push(candidate);
        localStorage.setItem('max_db', JSON.stringify(list));

        document.getElementById('questionnaire').style.display = 'none';
        document.getElementById('success-screen').style.display = 'block';
    }

    function loadCandidates() {
        let list = JSON.parse(localStorage.getItem('max_db') || '[]');
        let html = '';
        list.forEach(c => {
            html += `<tr><td>${c.name}</td><td>${c.dob}</td>
            <td><button class="login-btn" style="padding:5px 10px; font-size:0.8rem;" onclick='showDetails(${JSON.stringify(c)})'>נתח אופי</button></td></tr>`;
        });
        document.getElementById('candidates-list').innerHTML = html;
    }

    function showDetails(c) {
        document.getElementById('det-name').innerText = c.name;
        document.getElementById('det-dob').innerText = c.dob;
        let ansHtml = '';
        c.answers.forEach(item => ansHtml += `<p><b>${item.q}</b><br>תשובה: ${item.a}</p>`);
        document.getElementById('det-answers').innerHTML = ansHtml;
        document.getElementById('details-view').style.display = 'block';
    }

    function switchLanguage(lang) {
        const t = {
            he: { fname: "שם פרטי:", lname: "שם משפחה:", dob: "תאריך לידה (הקלדה חופשית):", next: "המשך לשאלון ההתאמה", dir: "rtl" },
            en: { fname: "First Name:", lname: "Last Name:", dob: "Date of Birth:", next: "Continue to Questionnaire", dir: "ltr" }
        };
        const active = t[lang];
        document.getElementById('lbl-fname').innerText = active.fname;
        document.getElementById('lbl-lname').innerText = active.lname;
        document.getElementById('lbl-dob').innerText = active.dob;
        document.getElementById('btn-next').innerText = active.next;
        document.body.dir = active.dir;
    }
</script>
</body>
</html>
