<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
    <title>MAX STOCK - OREN PROTOCOL</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        :root { --gold: #c9a84c; --dark: #0f1a2e; --card: #16213e; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: var(--dark); color: #fff; line-height: 1.6; overflow-x: hidden; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .glass-card { background: var(--card); border-radius: 20px; padding: 30px; border: 1px solid rgba(201, 168, 76, 0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: var(--gold); font-size: 2.5rem; margin-bottom: 20px; font-weight: 900; }
        .section-title { color: var(--gold); margin: 20px 0 10px; border-bottom: 1px solid rgba(201,168,76,0.3); padding-bottom: 5px; }
        .form-control { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #ccc; font-size: 16px; color: #000; }
        .q-card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 4px solid var(--gold); }
        .btn-main { width: 100%; padding: 18px; background: linear-gradient(135deg, var(--gold), #a38637); border: none; border-radius: 12px; color: #fff; font-size: 1.2rem; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .btn-main:hover { opacity: 0.9; transform: translateY(-2px); }
        .admin-item { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 3px solid var(--gold); }
        .badge { background: var(--gold); color: #000; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; float: left; }
        .lang-btn { background: transparent; border: 1px solid var(--gold); color: var(--gold); padding: 5px 10px; margin: 0 5px; border-radius: 5px; cursor: pointer; }
        .lang-btn.active { background: var(--gold); color: #000; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        const DEPARTMENTS = ["כלי בית ומטבח", "טקסטיל ונוי", "צעצועים ופנאי", "חומרי ניקוי ופארם", "יצירה וציוד משרדי", "חשמל ואלקטרוניקה", "ריהוט וגן", "קמפינג וטיולים", "עולם הילד והתינוק", "כלי עבודה ותחזוקה", "אחסון וארגון הבית", "מוצרי מסיבות ואירועים", "עונתי"];
        const POSITIONS = ["מנהל סניף", "סגן מנהל", "אחראי משמרת", "מנהל מחלקה", "קופאי/ת ראשי/ת", "קופאי/ת", "סדרן/ית סחורה", "מחסנאי/ת", "מלגזן/ית", "איש אחזקה", "נציג שירות", "אחראי ליקוט", "מניעת אובדן מלאי", "עובד כללי", "מזכיר/ת סניף"];

        const QUESTIONS = [
            { id: 1, q: "לקוח מחפש מוצר שחסר על המדף. מה תעשה?", a: ["אבדוק במחסן ואביא לו אישית", "אבדוק במחשב אם קיים במלאי", "אגיד שחסר ואכוון למוצר דומה", "אמשיך בעבודתי הרגילה"] },
            { id: 2, q: "יש תור ארוך מאוד בקופות ואתה בסידור מדף?", a: ["אגש מיד לעזור בקופה בלי שיקראו לי", "אחכה שיקראו לי לעזור", "אמשיך לסדר עד שאסיים את המשימה", "אלך למחסן כדי לא להפריע"] },
            { id: 3, q: "ראית מוצר שבור או נוזל על הרצפה במעבר?", a: ["אנקה מיד ואדאג לבטיחות הלקוחות", "אדווח למנהל המשמרת", "אקרא לעובד ניקיון שיגיע", "אעקוף את המפגע ואמשיך כרגיל"] },
            { id: 4, q: "לקוח מתלונן בקול רם על מחיר גבוה של מוצר?", a: ["אקשיב בסבלנות ואנסה להסביר בנועם", "אפנה אותו למנהל הסניף", "אגיד שזה המחיר ואין מה לעשות", "אתעלם ואעבור למחלקה אחרת"] },
            { id: 5, q: "המנהל נתן לך משימה שאתה פחות אוהב לבצע?", a: ["אבצע אותה הכי טוב ומהר שאפשר", "אבצע ואז אבקש לגוון במשימה אחרת", "אעשה אותה לאט כדי שלא יבקשו שוב", "אנסה למצוא עובד אחר שיחליף אותי"] },
            { id: 6, q: "גילית שחבר לעבודה טעה בסידור המחלקה?", a: ["אעזור לו לתקן את הטעות בנעימות", "אסב את תשומת ליבו לטעות", "אדווח למנהל על הטעות", "לא ענייני, כל אחד אחראי על שלו"] },
            { id: 7, q: "הגעת למשמרת והמחלקה הפוכה לגמרי?", a: ["אתחיל לסדר מיד לפי סדר דחיפות", "אשאל את המנהל מאיפה להתחיל", "אסדר רק את האזור הקטן שלי", "אחכה שמישהו יגיד לי מה לעשות"] },
            { id: 8, q: "לקוח מתלבט זמן רב לגבי קניית מתנה?", a: ["אציע לו אפשרויות ואעזור לו לבחור", "אכוון אותו לאזור המתנות הכללי", "אגיד שזה עניין של טעם אישי", "אפנה אותו לעובד אחר"] },
            { id: 9, q: "מצאת שטר כסף על הרצפה בתוך החנות?", a: ["אמסור מיד למנהל או לקופה ראשית", "אשאל לקוחות מסביב אם מישהו איבד", "אשים אותו בקופת צדקה", "אשמור אותו בכיס"] },
            { id: 10, q: "איזו צורת עבודה אתה הכי מעדיף?", a: ["עבודה עם אחריות שבה אני רץ לבד", "עבודה בצוות עם שיתוף פעולה מלא", "עבודה שבה אומרים לי בדיוק מה לעשות", "עבודה שקטה במחסן בלי לקוחות"] },
            { id: 11, q: "לקוח דורש הנחה שאי אפשר לתת במערכת?", a: ["אסביר בנימוס את מדיניות הרשת", "אבדוק אם יש מבצע חלופי", "אשלח אותו להתווכח עם המנהל", "אגיד פשוט 'אין הנחות'"] },
            { id: 12, q: "סימנת מחיר טעות על קבוצת מוצרים?", a: ["אתקן מיד את הכל ואדווח למנהל", "אשאל את המנהל מה לעשות כעת", "אקווה שאף אחד לא ישים לב", "אשאיר את זה ככה"] },
            { id: 13, q: "המשמרת נגמרה והחנות עמוסה מאוד?", a: ["אשאר עוד כמה דקות לעזור", "אסיים את המשימה ואלך", "אצא מיד - השעה הגיעה", "אלך להחתים כרטיס בלי להגיד"] },
            { id: 14, q: "עובד אחר מבקש ממך לעשות משהו לא תקין?", a: ["אסרב בנימוס ואסביר לו את הנוהל", "אדווח על כך מיד למנהל", "אזרום איתו באופן חד פעמי", "אעשה מה שהוא ביקש"] },
            { id: 15, q: "מה הדבר שהכי חשוב לך במקום העבודה?", a: ["להתקדם לתפקידי ניהול ולהצליח", "שירות מעולה שגורם ללקוח לחייך", "סדר, ארגון ודיוק במשימות", "המשכורת והשקט הנפשי"] }
        ];

        const App = () => {
            const [view, setView] = useState('landing');
            const [answers, setAnswers] = useState(Array(15).fill(null));
            const [formData, setFormData] = useState({ name: '', dob: '', dept: '', pos: '' });
            const [adminData, setAdminData] = useState([]);

            useEffect(() => {
                const saved = JSON.parse(localStorage.getItem('oren_protocol_v5') || '[]');
                setAdminData(saved);
            }, []);

            const handleSave = () => {
                if (!formData.name || !formData.dob || !formData.dept || !formData.pos || answers.includes(null)) {
                    alert('נא למלא את כל הפרטים ולענות על כל 15 השאלות');
                    return;
                }
                
                const score = answers.filter(a => a === 0).length;
                let profile = "מבצע משימות";
                if (score >= 10) profile = "יוזמה גבוהה (ראש גדול)";
                else if (score >= 6) profile = "ביצועיסט אחראי";

                const [d, m] = formData.dob.split('.').map(Number);
                const signs = ["גדי","דלי","דגים","טלה","שור","תאומים","סרטן","אריה","בתולה","מאזניים","עקרב","קשת"];
                const sign = (d && m) ? signs[m % 12] : "לא ידוע";

                const newEntry = { ...formData, profile, sign, ts: new Date().toLocaleString() };
                const updated = [...adminData, newEntry];
                setAdminData(updated);
                localStorage.setItem('oren_protocol_v5', JSON.stringify(updated));
                alert('השאלון נשלח בהצלחה!');
                setView('landing');
            };

            if (view === 'admin') {
                return (
                    <div className="container">
                        <div className="glass-card">
                            <h1>לוח ניהול</h1>
                            <button onClick={() => setView('landing')} className="lang-btn">חזרה</button>
                            <div style={{marginTop:'20px'}}>
                                {adminData.length === 0 ? <p>אין נתונים עדיין</p> : adminData.map((item, i) => (
                                    <div key={i} className="admin-item">
                                        <span className="badge">{item.profile}</span>
                                        <p><strong>שם:</strong> {item.name}</p>
                                        <p><strong>תפקיד:</strong> {item.pos} | <strong>מחלקה:</strong> {item.dept}</p>
                                        <p><strong>מזל:</strong> {item.sign} | <strong>תאריך הגשה:</strong> {item.ts}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                );
            }

            if (view === 'quiz') {
                return (
                    <div className="container">
                        <div className="glass-card">
                            <h1>שאלון מועמד</h1>
                            <div className="section-title">פרטים אישיים</div>
                            <input className="form-control" placeholder="שם מלא" onChange={e => setFormData({...formData, name: e.target.value})} />
                            <input className="form-control" placeholder="תאריך לידה (למשל: 15.04)" onChange={e => setFormData({...formData, dob: e.target.value})} />
                            <select className="form-control" onChange={e => setFormData({...formData, dept: e.target.value})}>
                                <option value="">בחר מחלקה מועדפת (13 אפשרויות)...</option>
                                {DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                            <select className="form-control" onChange={e => setFormData({...formData, pos: e.target.value})}>
                                <option value="">בחר תפקיד מבוקש (15 אפשרויות)...</option>
                                {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
                            </select>

                            <div className="section-title">15 שאלות התאמה</div>
                            {QUESTIONS.map((q, i) => (
                                <div key={i} className="q-card">
                                    <p><strong>{i+1}. {q.q}</strong></p>
                                    <select style={{marginTop:'10px'}} onChange={e => {
                                        const newAns = [...answers];
                                        newAns[i] = parseInt(e.target.value);
                                        setAnswers(newAns);
                                    }}>
                                        <option value="">בחר תשובה...</option>
                                        {q.a.map((txt, idx) => <option key={idx} value={idx}>{txt}</option>)}
                                    </select>
                                </div>
                            ))}
                            <button className="btn-main" onClick={handleSave}>שלח שאלון</button>
                        </div>
                    </div>
                );
            }

            return (
                <div className="container">
                    <h1>MAX STOCK</h1>
                    <div className="glass-card" style={{textAlign:'center'}}>
                        <div style={{marginBottom:'20px'}}>
                            {['HE','EN','RU','AR','TH'].map(l => <button key={l} className="lang-btn">{l}</button>)}
                        </div>
                        <button className="btn-main" onClick={() => setView('quiz')}>התחל פרוטוקול גיוס</button>
                        <div style={{marginTop:'50px', opacity:0.2}} onClick={() => {
                            const p = prompt("סיסמת מנהל:");
                            if(p === "1234") setView('admin');
                        }}>ניהול</div>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
