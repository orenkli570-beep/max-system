<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>MAX STOCK - Recruitment System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;background:#f3f4f6;direction:rtl}
        input,select,button{font-family:inherit}
        button:hover{opacity:.9;cursor:pointer}
        .container{max-width:850px;margin:20px auto;padding:10px}
        .glass-card{background:white;border-radius:20px;padding:30px;box-shadow:0 10px 25px rgba(0,0,0,0.05)}
        .header{background:#e31e24;color:white;padding:25px;text-align:center;border-radius:20px 20px 0 0;margin-bottom:-20px}
        .q-card{background:#f9fafb;border:1px solid #e5e7eb;padding:20px;border-radius:15px;margin-bottom:15px}
        .btn-gold{width:100%;padding:15px;background:linear-gradient(135deg,#c9a84c,#e8c97a);border:none;border-radius:12px;color:#fff;font-weight:bold;font-size:18px}
        .admin-box{border-right:6px solid #e31e24;background:#fff5f5;padding:15px;margin-bottom:15px;border-radius:8px}
        .lang-btn{padding:8px 15px;margin:5px;border-radius:8px;border:1px solid #ddd;background:white;cursor:pointer}
        .lang-active{background:#e31e24;color:white;border-color:#e31e24}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- מנגנון אחסון (LocalStorage) ---
        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_candidates") || "[]"),
            save: (list) => localStorage.setItem("max_candidates", JSON.stringify(list)),
            add: (item) => {
                const l = DB.load();
                l.push({...item, id: Date.now(), submittedAt: new Date().toISOString()});
                DB.save(l);
            }
        };

        // --- נתוני שפות (15 שאלות כפול 5 שפות) ---
        const LANGS = {
            he: { dir:"rtl", label:"עברית", title:"ברוכים הבאים למקס סטוק", subtitle:"אנא מלא את פרטיך", name:"שם מלא", dob:"תאריך לידה (DD.MM.YYYY)", next:"הבא", send:"שלח שאלון", allReq:"נא לענות על כל השאלות", questions: [
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
            en: { dir:"ltr", label:"English", title:"Welcome to MAX", subtitle:"Please fill details", name:"Full Name", dob:"DOB (DD.MM.YYYY)", next:"Next", send:"Submit", allReq:"Answer all questions", questions: [
                {q:"Customer looks for missing item?", a:["Check warehouse immediately","Check computer/Ask manager","Say out of stock","Continue working"]},
                {q:"Long line at registers and you are stocking?", a:["Help immediately","Wait to be called","Keep stocking","Go to warehouse"]},
                {q:"Found broken item on floor?", a:["Clean immediately","Report to manager","Call cleaning staff","Ignore and continue"]},
                {q:"Customer shouting about price?", a:["Listen and calm them","Call manager","Say that's the price","Ignore and move"]},
                {q:"Manager asks for a task you dislike?", a:["Do it best and fast","Do it and ask for variety","Do it slowly","Try to avoid"]},
                {q:"Colleague made a mistake?", a:["Help them fix it","Tell them about it","Report to manager","Not my business"]},
                {q:"Department is a mess when you arrive?", a:["Start organizing by urgency","Ask manager where to start","Fix only my spot","Wait for instructions"]},
                {q:"Customer can't decide on a gift?", a:["Offer options and help","Point to gift area","Say it's a matter of taste","Refer to someone else"]},
                {q:"Found money on store floor?", a:["Give to manager","Ask nearby customers","Put in charity box","Keep it"]},
                {q:"How do you like to work?", a:["With responsibility/Alone","With the team","Being told exactly what to do","Alone in quiet"]},
                {q:"Customer demands impossible discount?", a:["Explain policy politely","Check other deals","Send to manager","Just say no"]},
                {q:"Noticed you marked wrong price?", a:["Fix and report","Ask manager how to fix","Hope no one notices","Leave it"]},
                {q:"Shift over but store is busy?", a:["Stay and help","Finish task and leave","Leave immediately","Hide in warehouse"]},
                {q:"Colleague asks to do something wrong?", a:["Refuse and explain","Report to manager","Help just once","Do what they asked"]},
                {q:"What motivates you?", a:["Success/Promotion","Great service","Perfect order","Salary/Quiet"]}
            ]},
            ru: { dir:"ltr", label:"Русский", title:"Добро пожаловать в MAX", name:"ФИО", dob:"Дата рождения", questions: [
                {q:"Покупатель ищет товар, которого нет?", a:["Проверю на складе","Проверю в системе","Скажу, что нет","Продолжу работу"]},
                {q:"Очередь на кассе, вы на полках?", a:["Пойду помогу","Подожду вызова","Продолжу полки","Уйду на склад"]},
                {q:"Разбитый товар на полу?", a:["Уберу сразу","Сообщу менеджеру","Позову уборщика","Пройду мимо"]},
                {q:"Клиент орет из-за цены?", a:["Выслушаю спокойно","Позову менеджера","Скажу 'такая цена'","Уйду в другое место"]},
                {q:"Менеджер дал скучное задание?", a:["Сделаю быстро и хорошо","Сделаю и попрошу другое","Буду делать медленно","Постараюсь избежать"]},
                {q:"Друг ошибся в раскладке?", a:["Помогу исправить","Скажу ему","Сообщу менеджеру","Не мое дело"]},
                {q:"Отдел в полном беспорядке?", a:["Начну с важного","Спрошу менеджера","Уберу только свое","Жду инструкций"]},
                {q:"Клиент выбирает подарок?", a:["Предложу варианты","Покажу где подарки","Скажу 'дело вкуса'","Передам другому"]},
                {q:"Нашли деньги на полу?", a:["Отдам менеджеру","Спрошу людей рядом","В бокс для пожертвований","Оставлю себе"]},
                {q:"Как вам нравится работать?", a:["Сам по себе","В команде","По четким указаниям","В тишине один"]},
                {q:"Требуют скидку, которой нет?", a:["Объясню правила","Найду акцию","Отправлю к менеджеру","Просто откажу"]},
                {q:"Заметили свою ошибку в цене?", a:["Исправлю и сообщу","Спрошу как быть","Надеюсь не заметят","Оставлю так"]},
                {q:"Смена кончилась, в зале толпа?", a:["Останусь помогу","Закончу дело и уйду","Уйду сразу","Спрячусь на складе"]},
                {q:"Просят сделать не по правилам?", a:["Откажусь","Сообщу менеджеру","Помогу один раз","Сделаю как просят"]},
                {q:"Что вас мотивирует?", a:["Карьера","Довольный клиент","Порядок","Зарплата"]}
            ]},
            ar: { dir:"rtl", label:"العربية", title:"أهلاً بكم في ماكس ستوك", name:"الاسم الكامل", dob:"تاريخ الميلاد", questions: [
                {q:"زبون يبحث عن منتج مفقود؟", a:["أفحص المخزن فوراً","أفحص الحاسوب","أقول إنه غير متوفر","أكمل عملي"]},
                {q:"طابور طويل وأنت ترتب الرفوف؟", a:["أذهب للمساعدة فوراً","أنتظر المناداة","أكمل الرفوف","أذهب للمخزن"]},
                {q:"منتج مكسور على الأرض؟", a:["أنظف فوراً","أبلغ المدير","أنادي عامل النظافة","أكمل طريقي"]},
                {q:"زبون يصرخ بسبب السعر؟", a:["أستمع بصبر","أنادي المدير","أقول هذا هو السعر","أتجاهل وأبتعد"]},
                {q:"المدير يطلب مهمة لا تحبها؟", a:["أنفذها بأفضل شكل","أنفذ ثم أطلب التغيير","أعمل ببطء","أحاول التهرب"]},
                {q:"زميل أخطأ في الترتيب؟", a:["أساعده بلطف","أنبهه للخطأ","أبلغ المدير","ليس من شأني"]},
                {q:"وصلت والقسم في فوضى؟", a:["أبدأ بالترتيب حسب الأهمية","أسأل المدير من أين أبدأ","أرتب منطقتي فقط","أنتظر التعليمات"]},
                {q:"زبون محتار في هدية؟", a:["أقترح خيارات","أوجهه لقسم الهدايا","أقول هذا ذوق شخصي","أحوله لموظف آخر"]},
                {q:"وجدت نقوداً على الأرض؟", a:["أسلمها للمدير","أسأل الزبائن","أضعها في صندوق الصدقة","أضعها في جيبي"]},
                {q:"كيف تحب أن تعمل؟", a:["مسؤولية شخصية وحدي","مع الفريق","تلقي أوامر مباشرة","وحدي بهدوء"]},
                {q:"طلب خصم غير ممكن؟", a:["أشرح سياسة المحل","أبحث عن عرض بديل","أرسله للمدير","أقول لا ببساطة"]},
                {q:"أخطأت في وضع السعر؟", a:["أصحح وأبلغ المدير","أسأل كيف أصحح","أمل ألا يلاحظ أحد","أتركها كما هي"]},
                {q:"انتهى الوقت والمحل مزدحم؟", a:["أبقى للمساعدة","أنهي المهمة وأرحل","أرحل فوراً","أختفي في المخزن"]},
                {q:"موظف يطلب شيئاً غير قانوني؟", a:["أرفض وأشرح القانون","أبلغ المدير","أساعد لمرة واحدة","أفعل ما طلب"]},
                {q:"ما الذي يحفزك؟", a:["الترقية والنجاح","خدمة الزبائن","النظام والترتيب","المعاش والهدوء"]}
            ]},
            th: { dir:"ltr", label:"ภาษาไทย", title:"ยินดีต้อนรับสู่ MAX", name:"ชื่อ-นามสกุล", dob:"วันเกิด", questions: [
                {q:"ลูกค้ามองหาสินค้าที่ไม่มีบนชั้น?", a:["เช็คในโกดังทันที","เช็คคอมพิวเตอร์/ถามหัวหน้า","บอกว่าหมดสต็อก","ทำงานต่อ"]},
                {q:"คิวยาวที่แคชเชียร์และคุณกำลังจัดของ?", a:["ไปช่วยทันที","รอให้เรียก","จัดของต่อ","ไปที่โกดัง"]},
                {q:"พบสินค้าแตกบนพื้น?", a:["ทำความสะอาดทันที","รายงานหัวหน้ากะ","เรียกพนักงานทำความสะอาด","เดินผ่านไป"]},
                {q:"ลูกค้าตะโกนเรื่องราคา?", a:["ฟังอย่างอดทน","เรียกผู้จัดการทันที","บอกว่าเป็นราคานี้","ไม่สนใจและเดินหนี"]},
                {q:"หัวหน้าสั่งงานที่คุณไม่ชอบ?", a:["ทำให้ดีและเร็วที่สุด","ทำแล้วขอสลับงาน","ทำช้าๆ","พยายามเลี่ยง"]},
                {q:"เพื่อนร่วมงานจัดของผิด?", a:["ช่วยเขาแก้ไข","บอกเขาตรงๆ","รายงานหัวหน้า","ไม่ใช่เรื่องของฉัน"]},
                {q:"มาถึงแล้วแผนกวุ่นวายมาก?", a:["เริ่มจัดตามความด่วน","ถามหัวหน้าว่าเริ่มตรงไหน","จัดเฉพาะโซนตัวเอง","รอคำสั่งละเอียด"]},
                {q:"ลูกค้าตัดสินใจเลือกของขวัญไม่ได้?", a:["เสนอทางเลือกและช่วย","ชี้ไปที่โซนของขวัญ","บอกว่าเป็นเรื่องของรสนิยม","ให้พนักงานคนอื่นช่วย"]},
                {q:"พบเงินบนพื้นร้าน?", a:["ส่งให้หัวหน้า","ถามลูกค้ารอบๆ","ใส่กล่องบริจาค","เก็บใส่กระเป๋า"]},
                {q:"คุณชอบทำงานแบบไหน?", a:["รับผิดชอบเอง/ทำคนเดียว","ทำร่วมกับทีม","รอคำสั่งที่ชัดเจน","ทำคนเดียวเงียบๆ"]},
                {q:"ลูกค้าขอส่วนลดที่ให้ไม่ได้?", a:["อธิบายกฎอย่างสุภาพ","เช็คโปรโมชั่นอื่น","ส่งให้ผู้จัดการ","บอกว่าไม่ได้"]},
                {q:"ติดป้ายราคาผิด?", a:["แก้ทันทีและรายงาน","ถามหัวหน้าวิธีแก้","หวังว่าจะไม่มีใครเห็น","ทิ้งไว้แบบนั้น"]},
                {q:"หมดกะแล้วแต่ร้านยังยุ่ง?", a:["อยู่ช่วยจนกว่าจะซา","ทำงานให้เสร็จแล้วกลับ","กลับทันที","แอบไปที่โกดัง"]},
                {q:"เพื่อนขอให้ทำสิ่งที่ผิดกฎ?", a:["ปฏิเสธและอธิบายกฎ","รายงานหัวหน้า","ช่วยแค่ครั้งเดียว","ทำตามที่ขอ"]},
                {q:"อะไรคือแรงจูงใจของคุณ?", a:["ความก้าวหน้า","บริการที่ดีลูกค้าพอใจ","ความเป็นระเบียบ","เงินเดือนและความสงบ"]}
            ]}
        };

        // --- פונקציות ניתוח (תמיד בעברית למנהל) ---
        function analyze(ans) {
            let aCount = ans.filter(x => x === 0).length;
            let bCount = ans.filter(x => x === 1).length;
            const style = aCount >= 8 ? "יוזם (ראש גדול)" : bCount >= 7 ? "שירותי (שחקן נשמה)" : "ביצועיסט (צייתן)";
            const desc = aCount >= 8 ? "מועמד עצמאי שדוחף קדימה. לא לחנוק אותו במיקרו-ניהול." : "מתאים מאוד לעבודה עם אנשים. סבלני ונעים.";
            return { style, desc };
        }

        // --- קומפוננטת האפליקציה ---
        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [name, setName] = useState("");
            const [dob, setDob] = useState("");
            const [answers, setAnswers] = useState(Array(15).fill(null));
            const [adminData, setAdminData] = useState([]);

            const L = LANGS[lang];

            const submitQuiz = () => {
                if(!name || !dob || answers.includes(null)) return alert(L.allReq);
                const analysis = analyze(answers);
                DB.add({ name, dob, answers, analysis });
                alert("Success / תודה רבה");
                setView("home");
                setAnswers(Array(15).fill(null));
                setName(""); setDob("");
            };

            const openAdmin = () => {
                const pass = prompt("Password:");
                if(pass === "1234") {
                    setAdminData(DB.load());
                    setView("admin");
                }
            };

            if (view === "home") return (
                <div className="container" style={{textAlign:'center', marginTop:'100px'}}>
                    <div className="header"><h1>MAX STOCK</h1></div>
                    <div className="glass-card">
                        <h2>Select Language / בחר שפה</h2>
                        <div style={{margin:'20px 0'}}>
                            {Object.keys(LANGS).map(k => (
                                <button key={k} onClick={()=>setLang(k)} className={`lang-btn ${lang===k?'lang-active':''}`}>{LANGS[k].label}</button>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={()=>setView("quiz")}>התחל שאלון / Start</button>
                        <button onClick={openAdmin} style={{marginTop:'30px', background:'none', border:'none', color:'#999', cursor:'pointer'}}>Admin</button>
                    </div>
                </div>
            );

            if (view === "quiz") return (
                <div className="container" style={{direction: L.dir}}>
                    <div className="header"><h1>{L.title}</h1></div>
                    <div className="glass-card">
                        <div className="q-card">
                            <input type="text" placeholder={L.name} value={name} onChange={e=>setName(e.target.value)} style={{marginBottom:'10px', width:'100%', padding:'10px'}} />
                            <input type="text" placeholder={L.dob} value={dob} onChange={e=>setDob(e.target.value)} style={{width:'100%', padding:'10px'}} />
                        </div>
                        {L.questions.map((q, i) => (
                            <div key={i} className="q-card">
                                <strong>{i+1}. {q.q}</strong>
                                <select onChange={e=> {
                                    const newAns = [...answers];
                                    newAns[i] = parseInt(e.target.value);
                                    setAnswers(newAns);
                                }} style={{width:'100%', marginTop:'10px', padding:'5px'}}>
                                    <option value="">--</option>
                                    {q.a.map((opt, idx) => <option key={idx} value={idx}>{opt}</option>)}
                                </select>
                            </div>
                        ))}
                        <button className="btn-gold" onClick={submitQuiz}>{L.send}</button>
                    </div>
                </div>
            );

            if (view === "admin") return (
                <div className="container">
                    <div className="header"><h1>ניהול מועמדים (עברית)</h1></div>
                    <div className="glass-card">
                        <button onClick={()=>setView("home")} style={{marginBottom:'20px'}}>חזרה לתפריט</button>
                        {adminData.length === 0 ? <p>אין מועמדים רשומים</p> : adminData.map((c, i) => (
                            <div key={i} className="admin-box">
                                <h3>{c.name} | {c.dob}</h3>
                                <p><strong>סיווג:</strong> {c.analysis.style}</p>
                                <p><strong>ניתוח:</strong> {c.analysis.desc}</p>
                                <small>הוגש ב: {new Date(c.submittedAt).toLocaleString()}</small>
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
