<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>MAX STOCK - OREN PROTOCOL</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Segoe UI',Arial,sans-serif; background:#0f1a2e; color:#fff; direction:rtl; min-height:100vh;}
        .container{max-width:850px; margin:20px auto; padding:15px}
        .glass-card{background:#16213e; border-radius:20px; padding:30px; border:1px solid rgba(201,168,76,0.2); box-shadow:0 10px 30px rgba(0,0,0,0.5)}
        .header h1{text-align:center; font-size:2.5rem; background:linear-gradient(135deg,#c9a84c,#e8c97a); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-weight:900; margin-bottom:20px}
        .lang-bar{display:flex; justify-content:center; gap:8px; margin-bottom:20px}
        .btn-lang{padding:6px 12px; border-radius:8px; border:1px solid #c9a84c; background:transparent; color:#c9a84c; cursor:pointer; font-weight:bold}
        .btn-lang.active{background:#c9a84c; color:#fff}
        .form-group{margin-bottom:15px}
        label{display:block; margin-bottom:5px; color:#c9a84c; font-weight:bold}
        input, select{width:100%; padding:12px; border-radius:10px; border:2px solid #e0d5c0; font-size:16px; background:#fff; color:#000}
        .q-item{background:rgba(255,255,255,0.04); border-radius:15px; padding:20px; margin-bottom:15px; border-right:5px solid #c9a84c}
        .btn-gold{width:100%; padding:18px; background:linear-gradient(135deg,#c9a84c,#a38637); border:none; border-radius:14px; color:#fff; font-size:19px; font-weight:800; cursor:pointer; margin-top:20px}
        .admin-row{background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:10px; border:1px solid rgba(201,168,76,0.2)}
        .badge{background:#c9a84c; color:#000; padding:3px 8px; border-radius:5px; font-weight:bold; font-size:12px}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState } = React;

        const DEPARTMENTS = ["כלי בית ומטבח","טקסטיל ונוי","צעצועים ופנאי","חומרי ניקוי ופארם","יצירה וציוד משרדי","חשמל ואלקטרוניקה","ריהוט וגן","קמפינג וטיולים","עולם הילד והתינוק","כלי עבודה ותחזוקה","אחסון וארגון הבית","מוצרי מסיבות ואירועים","עונתי"];
        const POSITIONS = ["מנהל סניף","סגן מנהל","אחראי משמרת","מנהל מחלקה","קופאי/ת ראשי/ת","קופאי/ת","סדרן/ית סחורה","מחסנאי/ת","מלגזן/ית","איש אחזקה","נציג שירות","אחראי ליקוט","מניעת אובדן מלאי","עובד כללי","מזכיר/ת סניף"];

        const QUESTIONS = [
            {q: "לקוח מחפש מוצר שחסר על המדף. מה תעשה?", a: ["אבדוק במחסן ואביא לו אישית", "אבדוק במחשב אם קיים במלאי", "אגיד שחסר ואכוון למוצר דומה", "אמשיך בעבודתי הרגילה"]},
            {q: "יש תור ארוך מאוד בקופות ואתה בסידור מדף?", a: ["אגש מיד לעזור בקופה בלי שיקראו לי", "אחכה שיקראו לי לעזור", "אמשיך לסדר עד שאסיים את המשימה", "אלך למחסן כדי לא להפריע"]},
            {q: "ראית מוצר שבור או נוזל על הרצפה במעבר?", a: ["אנקה מיד ואדאג לבטיחות הלקוחות", "אדווח למנהל המשמרת", "אקרא לעובד ניקיון שיגיע", "אעקוף את המפגע ואמשיך כרגיל"]},
            {q: "לקוח מתלונן בקול רם על מחיר גבוה של מוצר?", a: ["אקשיב בסבלנות ואנסה להסביר בנועם", "אפנה אותו למנהל הסניף", "אגיד שזה המחיר ואין מה לעשות", "אתעלם ואעבור למחלקה אחרת"]},
            {q: "המנהל נתן לך משימה שאתה פחות אוהב לבצע?", a: ["אבצע אותה הכי טוב ומהר שאפשר", "אבצע ואז אבקש לגוון במשימה אחרת", "אעשה אותה לאט כדי שלא יבקשו שוב", "אנסה למצוא עובד אחר שיחליף אותי"]},
            {q: "גילית שחבר לעבודה טעה בסידור המחלקה?", a: ["אעזור לו לתקן את הטעות בנעימות", "אסב את תשומת ליבו לטעות", "אדווח למנהל על הטעות", "לא ענייני, כל אחד אחראי על שלו"]},
            {q: "הגעת למשמרת והמחלקה הפוכה לגמרי?", a: ["אתחיל לסדר מיד לפי סדר דחיפות", "אשאל את המנהל מאיפה להתחיל", "אסדר רק את האזור הקטן שלי", "אחכה שמישהו יגיד לי מה לעשות"]},
            {q: "לקוח מתלבט זמן רב לגבי קניית מתנה?", a: ["אציע לו אפשרויות ואעזור לו לבחור", "אכוון אותו לאזור המתנות הכללי", "אגיד שזה עניין של טעם אישי", "אפנה אותו לעובד אחר"]},
            {q: "מצאת שטר כסף על הרצפה בתוך החנות?", a: ["אמסור מיד למנהל או לקופה ראשית", "אשאל לקוחות מסביב אם מישהו איבד", "אשים אותו בקופת צדקה", "אשמור אותו בכיס"]},
            {q: "איזו צורת עבודה אתה הכי מעדיף?", a: ["עבודה עם אחריות שבה אני רץ לבד", "עבודה בצוות עם שיתוף פעולה מלא", "עבודה שבה אומרים לי בדיוק מה לעשות", "עבודה שקטה במחסן בלי לקוחות"]},
            {q: "לקוח דורש הנחה שאי אפשר לתת במערכת?", a: ["אסביר בנימוס את מדיניות הרשת", "אבדוק אם יש מבצע חלופי", "אשלח אותו להתווכח עם המנהל", "אגיד פשוט 'אין הנחות'"]},
            {q: "סימנת מחיר טעות על קבוצת מוצרים?", a: ["אתקן מיד את הכל ואדווח למנהל", "אשאל את המנהל מה לעשות כעת", "אקווה שאף אחד לא ישים לב", "אשאיר את זה ככה"]},
            {q: "המשמרת נגמרה והחנות עמוסה מאוד?", a: ["אשאר עוד כמה דקות לעזור", "אסיים את המשימה ואלך", "אצא מיד - השעה הגיעה", "אלך להחתים כרטיס בלי להגיד"]},
            {q: "עובד אחר מבקש ממך לעשות משהו לא תקין?", a: ["אסרב בנימוס ואסביר לו את הנוהל", "אדווח על כך מיד למנהל", "אזרום איתו באופן חד פעמי", "אעשה מה שהוא ביקש"]},
            {q: "מה הדבר שהכי חשוב לך במקום העבודה?", a: ["להתקדם לתפקידי ניהול ולהצליח", "שירות מעולה שגורם ללקוח לחייך", "סדר, ארגון ודיוק במשימות", "המשכורת והשקט הנפשי"]}
        ];

        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [ans, setAns] = useState(Array(15).fill(null));
            const [info, setInfo] = useState({name:"", dob:"", dept:"", pos:""});
            const [db, setDb] = useState(JSON.parse(localStorage.getItem("max_protocol_db") || "[]"));

            const getSign = (dob) => {
                if(!dob.includes('.')) return "לא צוין";
                const [d, m] = dob.split('.').map(Number);
                const signs = ["גדי","דלי","דגים","טלה","שור","תאומים","סרטן","אריה","בתולה","מאזניים","עקרב","קשת"];
                return signs[m % 12];
            };

            const save = () => {
                if(!info.name || !info.dob || !info.dept || !info.pos || ans.includes(null)) return alert("חובה למלא את כל השדות והשאלות");
                const bigScore = ans.filter(a => a === 0).length;
                const style = bigScore >= 10 ? "יוזמה גבוהה" : bigScore >= 6 ? "ביצועיסט אחראי" : "מבצע משימות";
                const newEntry = {...info, style, sign: getSign(info.dob), ts: new Date().toLocaleString()};
                const newDb = [...db, newEntry];
                setDb(newDb); localStorage.setItem("max_protocol_db", JSON.stringify(newDb));
                alert("השאלון הוגש בהצלחה!"); setView("home");
            };

            if(view === "admin") return (
                <div className="container">
                    <div className="glass-card">
                        <h2 style={{color:'#c9a84c', marginBottom:20}}>לוח מנהל - פרוטוקול אורן</h2>
                        <button onClick={()=>setView("home")} style={{background:'none', border:'none', color:'#fff', cursor:'pointer'}}>→ חזרה</button>
                        {db.map((item, idx) => (
                            <div key={idx} className="admin-row">
                                <p><strong>{item.name}</strong> <span className="badge">{item.style}</span></p>
                                <p>תפקיד: {item.pos} | מחלקה: {item.dept}</p>
                                <p>מזל: {item.sign} | הגשה: {item.ts}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );

            if(view === "quiz") return (
                <div className="container">
                    <div className="glass-card">
                        <div className="form-group">
                            <label>שם מלא</label>
                            <input type="text" onChange={e=>setInfo({...info, name:e.target.value})} />
                        </div>
                        <div className="form-group">
                            <label>תאריך לידה (DD.MM)</label>
                            <input type="text" placeholder="לדוגמה: 12.05" onChange={e=>setInfo({...info, dob:e.target.value})} />
                        </div>
                        <div className="form-group">
                            <label>מחלקה מועדפת (13 אפשרויות)</label>
                            <select onChange={e=>setInfo({...info, dept:e.target.value})}>
                                <option value="">בחר מחלקה...</option>
                                {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label>תפקיד מבוקש (15 אפשרויות)</label>
                            <select onChange={e=>setInfo({...info, pos:e.target.value})}>
                                <option value="">בחר תפקיד...</option>
                                {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>
                        <hr style={{margin:'20px 0', opacity:0.2}} />
                        {QUESTIONS.map((q, i) => (
                            <div key={i} className="q-item">
                                <p><strong>{i+1}. {q.q}</strong></p>
                                <select onChange={e=>{const n=[...ans]; n[i]=parseInt(e.target.value); setAns(n)}}>
                                    <option value="">בחר תשובה...</option>
                                    {q.a.map((txt, idx) => <option key={idx} value={idx}>{txt}</option>)}
                                </select>
                            </div>
                        ))}
                        <button className="btn-gold" onClick={save}>שלח שאלון למערכת</button>
                    </div>
                </div>
            );

            return (
                <div className="container" style={{textAlign:'center'}}>
                    <div className="header"><h1>MAX STOCK</h1></div>
                    <div className="glass-card">
                        <div className="lang-bar">
                            {["he","en","ru","ar","th"].map(l => (
                                <button key={l} className={`btn-lang ${lang===l?'active':''}`} onClick={()=>setLang(l)}>{l.toUpperCase()}</button>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={()=>setView("quiz")}>התחל פרוטוקול גיוס</button>
                        <button onClick={()=>{if(prompt("Pass:")==="1234")setView("admin")}} style={{marginTop:60, opacity:0.05, background:'none', border:'none', color:'#fff'}}>Admin</button>
                    </div>
                </div>
            );
        }
        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
