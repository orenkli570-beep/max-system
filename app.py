<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>MAX STOCK - Recruitment Premium</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        /* עיצוב פרימיום לפי הפרוטוקול */
        *{box-sizing:border-box;margin:0;padding:0}
        body{
            font-family:'Segoe UI',Arial,sans-serif;
            min-height:100vh;
            background: #0f172a; /* כחול כהה עמוק */
            color: #f1f5f9;
            direction: rtl;
        }
        .container{max-width:850px;margin:30px auto;padding:15px}
        
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 28px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
        }

        .header-title {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #c9a84c 0%, #f1d27b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-align: center;
        }

        .q-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 18px;
            padding: 25px;
            margin-bottom: 15px;
            border-right: 4px solid #c9a84c;
            transition: all 0.3s ease;
        }

        .q-card:hover { background: rgba(255, 255, 255, 0.08); transform: scale(1.01); }

        input, select {
            width: 100%;
            padding: 15px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(201, 168, 76, 0.3);
            border-radius: 12px;
            color: #fff;
            font-size: 16px;
            margin-top: 10px;
            outline: none;
        }

        .btn-gold {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #c9a84c 0%, #a38637 100%);
            border: none;
            border-radius: 16px;
            color: #0f172a;
            font-weight: 800;
            font-size: 18px;
            cursor: pointer;
            margin-top: 20px;
            box-shadow: 0 10px 20px -5px rgba(201, 168, 76, 0.4);
        }

        .lang-btn {
            padding: 10px 18px;
            margin: 5px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255,255,255,0.05);
            color: #fff;
            cursor: pointer;
        }

        .lang-active { background: #c9a84c; color: #0f172a; font-weight: bold; }

        .admin-item {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(201, 168, 76, 0.2);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .badge {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            background: #c9a84c;
            color: #0f172a;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- לוגיקת נתונים (LocalStorage) ---
        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_pro_data") || "[]"),
            save: (l) => localStorage.setItem("max_pro_data", JSON.stringify(l)),
            add: (i) => { const l=DB.load(); l.push({...i, id:Date.now(), time:new Date().toLocaleString()}); DB.save(l); }
        };

        // --- נתוני שפות ושאלות ---
        const LANGS = {
            he: { dir:"rtl", label:"עברית", title:"מקס סטוק", start:"התחל שאלון", name:"שם מלא", dob:"תאריך לידה (DD.MM.YYYY)", send:"שלח שאלון", questions: [
                {q:"לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a:["אבדוק מיד במחסן ואנסה להביא לו","אבדוק במחשב או אשאל אחראי","אעדכן שחסר במלאי","אמשיך בעבודתי"]},
                {q:"יש תור ארוך בקופות ואתה בסידור מדף?", a:["אגש מיד לעזור בקופה","אחכה שיקראו לי","אמשיך לסדר מדפים","אלך למחסן"]},
                {q:"ראית מוצר שבור על הרצפה?", a:["אנקה מיד ואדאג לבטיחות","אדווח למנהל המשמרת","אקרא לעובד ניקיון","אעקוף ואמשיך לעבוד"]},
                {q:"לקוח צועק בגלל מחיר של מוצר?", a:["אקשיב בסבלנות ואנסה להרגיע","אקרא מיד למנהל","אגיד שזה המחיר וזהו","אתעלם ואעבור מקום"]},
                {q:"המנהל מבקש משימה שאתה לא אוהב?", a:["אבצע הכי טוב ומהר שאפשר","אבצע ואז אבקש לגוון","אעשה לאט שלא יבקשו שוב","אנסה להתחמק"]},
                {q:"גילית שחבר טעה בסידור המחלקה?", a:["אעזור לו לתקן בנעימות","אסב את תשומת ליבו","אדווח למנהל על הטעות","לא ענייני, אני בשלי"]},
                {q:"הגעת וכל המחלקה הפוכה לגמרי?", a:["אתחיל לסדר לפי הדחיפות","אשאל מנהל מאיפה להתחיל","אסדר רק את האזור שלי","אחכה להוראות מפורטות"]},
                {q:"לקוח מתלבט לגבי מתנה?", a:["אציע אפשרויות ואעזור","אכוון לאזור המתנות","אגיד שזה עניין של טעם","אפנה לעובד אחר"]},
                {q:"מצאת כסף על הרצפה בחנות?", a:["אמסור למנהל/קופה ראשית","אשאל לקוחות מסביב","אשים בקופת צדקה","אשמור בכיס"]},
                {q:"איך אתה הכי אוהב לעבוד?", a:["שיש לי אחריות ואני רץ לבד","בשיתוף פעולה עם הצוות","שיגידו לי בדיוק מה לעשות","לבד בשקט בלי הפרעות"]},
                {q:"לקוח דורש הנחה שאי אפשר לתת?", a:["אסביר בנימוס את המדיניות","אבדוק אם יש מבצע חלופי","אשלח אותו למנהל","אגיד פשוט לא"]},
                {q:"שמת לב שסימנת מחיר טעות?", a:["אתקן מיד ואדווח","אשאל מנהל איך לתקן","אקווה שלא ישימו לב","אשאיר ככה"]},
                {q:"המשמרת נגמרה והחנות עמוסה?", a:["אשאר לעזור עד שיירגע","אסיים משימה ואלך","אצא מיד - נגמר הזמן","אעלם למחסן"]},
                {q:"עובד מבקש לעשות משהו לא תקין?", a:["אסרב ואסביר את הנוהל","אדווח למנהל","אעזור לו באופן חד פעמי","אעשה מה שביקש"]},
                {q:"מה הכי מניע אותך?", a:["להתקדם ולהצליח","שירות מעולה ולקוח מרוצה","סדר וארגון מושלם","משכורת ושקט"]}
            ]},
            en: { dir:"ltr", label:"English", title:"MAX STOCK", start:"Start", name:"Full Name", dob:"DOB (DD.MM.YYYY)", send:"Submit", questions: Array(15).fill({q:"Question text...", a:["Option 1 (Big Head)","Option 2","Option 3","Option 4"]}) }
            // ניתן להוסיף כאן את יתר השפות באותו מבנה
        };

        // --- לוגיקת ניתוח (אסטרולוגיה + ניהול) ---
        function getAnalysis(dob, answers) {
            const bigHead = answers.filter(a => a === 0).length;
            const style = bigHead >= 9 ? "ראש גדול" : bigHead >= 5 ? "מאוזן" : "ראש קטן";
            
            // אסטרולוגיה פשוטה
            const [d, m] = (dob || "01.01").split('.').map(Number);
            const signs = [{s:"טלה", m:3},{s:"שור", m:4},{s:"תאומים", m:5},{s:"סרטן", m:6},{s:"אריה", m:7},{s:"בתולה", m:8},{s:"מאזניים", m:9},{s:"עקרב", m:10},{s:"קשת", m:11},{s:"גדי", m:12},{s:"דלי", m:1},{s:"דגים", m:2}];
            const sign = signs.find(x => x.m === m) || signs[0];

            return { style, bigHead, sign: sign.s };
        }

        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [name, setName] = useState("");
            const [dob, setDob] = useState("");
            const [answers, setAnswers] = useState(Array(15).fill(null));

            const L = LANGS[lang] || LANGS.he;

            const submit = () => {
                if(!name || !dob || answers.includes(null)) return alert("נא למלא הכל");
                DB.add({ name, dob, answers, analysis: getAnalysis(dob, answers) });
                alert("נשמר בהצלחה!");
                setView("home");
            };

            if(view === "home") return (
                <div className="container" style={{textAlign:'center', marginTop:'10vh'}}>
                    <div className="glass-card">
                        <h1 className="header-title">{L.title}</h1>
                        <p style={{marginBottom:'30px', color:'#94a3b8'}}>מערכת אבחון וגיוס מועמדים</p>
                        <div style={{marginBottom:'30px'}}>
                            {Object.keys(LANGS).map(k => (
                                <button key={k} onClick={()=>setLang(k)} className={`lang-btn ${lang===k?'lang-active':''}`}>{LANGS[k].label}</button>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={()=>setView("quiz")}>{L.start}</button>
                        <button onClick={()=>{if(prompt("Pass:")==="1234")setView("admin")}} style={{marginTop:'50px', background:'none', border:'none', color:'rgba(255,255,255,0.1)'}}>Admin</button>
                    </div>
                </div>
            );

            if(view === "quiz") return (
                <div className="container" style={{direction: L.dir}}>
                    <div className="glass-card">
                        <h2 className="header-title" style={{fontSize:'1.8rem'}}>שאלון מועמד</h2>
                        <input type="text" placeholder={L.name} onChange={e=>setName(e.target.value)} />
                        <input type="text" placeholder={L.dob} onChange={e=>setDob(e.target.value)} />
                        <div style={{marginTop:'30px'}}>
                            {L.questions.map((q, i) => (
                                <div key={i} className="q-card">
                                    <p style={{marginBottom:'10px'}}><strong>{i+1}. {q.q}</strong></p>
                                    <select onChange={e=>{const n=[...answers]; n[i]=parseInt(e.target.value); setAnswers(n);}}>
                                        <option value="">בחר תשובה...</option>
                                        {q.a.map((opt,idx)=><option key={idx} value={idx}>{opt}</option>)}
                                    </select>
                                </div>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={submit}>{L.send}</button>
                    </div>
                </div>
            );

            if(view === "admin") return (
                <div className="container" style={{direction:'rtl'}}>
                    <h1 className="header-title">לוח בקרה</h1>
                    <button onClick={()=>setView("home")} style={{color:'#c9a84c', background:'none', border:'none', cursor:'pointer'}}>→ חזרה</button>
                    <div style={{marginTop:'20px'}}>
                        {DB.load().map((c, i) => (
                            <div key={i} className="admin-item">
                                <div style={{display:'flex', justifyContent:'space-between'}}>
                                    <h3>{c.name} <span className="badge">מזל {c.analysis.sign}</span></h3>
                                    <span style={{color:'#c9a84c', fontWeight:'bold'}}>{c.analysis.style}</span>
                                </div>
                                <p style={{fontSize:'14px', marginTop:'10px', color:'#94a3b8'}}>תאריך לידה: {c.dob} | הוגש ב: {c.time}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
