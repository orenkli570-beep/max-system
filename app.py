<!DOCTYPE html>
<html lang="he">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>מערכת קליטת עובדים</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',Arial,sans-serif;min-height:100vh}
  input,select,button{font-family:inherit}
  button:hover{opacity:.9}
  ::-webkit-scrollbar{width:6px}
  ::-webkit-scrollbar-track{background:#0f1a2e}
  ::-webkit-scrollbar-thumb{background:#c9a84c;border-radius:3px}
</style>
</head>
<body>
<div id="root"></div>
<script type="text/babel">
const {useState,useEffect} = React;

// ─── STORAGE (localStorage fallback) ────────────────────────────────────
const DB = {
  load: () => { try { return JSON.parse(localStorage.getItem("rct_candidates")||"[]"); } catch(e){return[];} },
  save: (list) => { try { localStorage.setItem("rct_candidates", JSON.stringify(list)); } catch(e){} },
  add: (item) => { const l=DB.load(); l.push({...item,id:Date.now(),submittedAt:new Date().toISOString()}); DB.save(l); },
  update: (id,updates) => { const l=DB.load(); const i=l.findIndex(c=>c.id===id); if(i!==-1)l[i]={...l[i],...updates}; DB.save(l); }
};

// ─── LANGUAGE DATA ───────────────────────────────────────────────────────
const LANGS = {
  he: {
    dir:"rtl", label:"עברית",
    title:"ברוך הבא", subtitle:"אנא מלא את הפרטים הבאים",
    fullName:"שם מלא", dob:"תאריך לידה (DD.MM.YYYY)",
    next:"הבא", send:"שלח",
    thanks:"תודה! הפרטים הועברו למנהל.",
    required:"יש למלא את כל השדות", allRequired:"יש לענות על כל השאלות", dobInvalid:"תאריך לידה לא תקין",
    questions:[
      {q:"לקוח נכנס לחנות ונראה אבוד. מה תעשה?",a:["אגש מיד ואציע עזרה בחיוך","אחכה שיפנה אליי","אחפש עובד אחר שיעזור לו","אמשיך בעבודתי"]},
      {q:"המדף שאתה אחראי עליו לא מסודר. מה קודם?",a:["אסדר אותו מיד לפני כל דבר","אסיים משימה נוכחית ואז אסדר","אדווח למנהל","אשאיר לתורן הבא"]},
      {q:"מנהל ביקש ממך לעשות X, אך לדעתך Y עדיף. מה תעשה?",a:["אעשה X כפי שביקש","אציע Y ואסביר למנהל","אעשה Y בלי לשאול","אשאל עמית לדעתו"]},
      {q:"יש פגישה דחופה ואתה באמצע עזרה ללקוח. מה עדיף?",a:["אסיים עם הלקוח ואז אגיע","אלך מיד לפגישה","אבקש עמית להחליף אותי","אדחה את הפגישה"]},
      {q:"ראית שגיאת מחיר על מוצר. מה תעשה?",a:["אתקן מיד ואדווח למנהל","אדווח רק למנהל","אתקן בלי לדווח","אשאיר – זה לא תפקידי"]},
      {q:"לקוח כועס ומדבר בקול. מה תעשה?",a:["אקשיב בשקט ואנסה לפתור","אקרא מנהל מיד","אדבר בחזרה בקול","אתנצל ואסגור"]},
      {q:"הגעת לעבודה ורואה שעמית לא הגיע. מה תעשה?",a:["אדווח למנהל ואציע לכסות","אמשיך בתפקידי בלבד","אשאל עמיתים מה קרה","אחכה להוראות"]},
      {q:"המלאי ריק ולקוח מבקש מוצר. מה תגיד?",a:["אבדוק אם יש בחדר מלאי ואציע חלופה","אגיד שנגמר ואסיים","אבטיח שיגיע מחר","אפנה אותו לחנות אחרת"]},
      {q:"קיבלת ביקורת מהמנהל בפומבי. מה תרגיש ותעשה?",a:["אקבל, אלמד ואשתפר","ארגיש פגוע אך לא אגיב","אסביר את עצמי בציבור","אדבר עם המנהל בצד לאחר מכן"]},
      {q:"שעת השיא וכולם עסוקים. לקוח מבקש עזרה דחופה. מה תעשה?",a:["אגש מיד ואטפל","אגיד לו לחכות","אמצא עמית פנוי","אסמן ואחזור בהקדם"]},
      {q:"יש לך רעיון לשיפור שיטת עבודה. מה תעשה?",a:["אציג למנהל בפגישה הבאה","איישם בעצמי בלי לשאול","אשאר שקט – לא תפקידי","אשתף עמית בלבד"]},
      {q:"נגמרה המשמרת אך יש עבודה שלא הסתיימה. מה תעשה?",a:["אסיים לפני שאצא","אעביר לתורן הבא בעדכון","אצא – המשמרת הסתיימה","אשאל מנהל"]},
      {q:"לקוח שאל שאלה שאינך יודע עליה. מה תגיד?",a:["אודה שאיני יודע ואמצא את התשובה","אנחש ואגיד","אפנה לעמית","אגיד שאין לי זמן"]},
      {q:"שמת לב שעמית לא עושה את עבודתו. מה תעשה?",a:["אדבר איתו בעדינות","אדווח למנהל מיד","אתעלם – לא עסקי","אכסה אותו בשקט"]},
      {q:"קיבלת שתי משימות בו-זמנית. מה תעשה?",a:["אסדר לפי דחיפות ואעדכן","אתחיל עם האחרונה","אבקש עזרה מיד","אעשה שתיהן במקביל"]}
    ]
  },
  en: {
    dir:"ltr", label:"English",
    title:"Welcome", subtitle:"Please fill in your details",
    fullName:"Full Name", dob:"Date of Birth (DD.MM.YYYY)",
    next:"Next", send:"Submit",
    thanks:"Thank you! Your details have been forwarded to the manager.",
    required:"Please fill in all fields", allRequired:"Please answer all questions", dobInvalid:"Invalid date of birth",
    questions:[
      {q:"A customer enters the store and looks lost. What do you do?",a:["Approach immediately and offer help with a smile","Wait for them to approach me","Find another employee to assist","Continue my current task"]},
      {q:"The shelf you're responsible for is messy. What's first?",a:["Tidy it immediately before anything else","Finish current task then tidy","Report to manager","Leave it for the next shift"]},
      {q:"Manager asked for X, but you think Y is better. What do you do?",a:["Do X as requested","Suggest Y and explain to manager","Do Y without asking","Ask a colleague for opinion"]},
      {q:"Urgent meeting but you're helping a customer. What do you prioritize?",a:["Finish with customer then attend","Go immediately to meeting","Ask a colleague to take over","Postpone the meeting"]},
      {q:"You notice a price error on a product. What do you do?",a:["Fix it immediately and report to manager","Report only to manager","Fix it without reporting","Leave it — not my job"]},
      {q:"An angry customer is speaking loudly. What do you do?",a:["Listen calmly and try to resolve","Call manager immediately","Speak back loudly","Apologize and end conversation"]},
      {q:"You arrive and see a colleague hasn't shown up. What do you do?",a:["Report to manager and offer to cover","Continue your own tasks only","Ask colleagues what happened","Wait for instructions"]},
      {q:"Stock is empty and a customer requests a product. What do you say?",a:["Check stockroom and offer alternative","Say it's out of stock and end","Promise it'll arrive tomorrow","Redirect to another store"]},
      {q:"Manager criticized you publicly. How do you react?",a:["Accept it, learn and improve","Feel hurt but say nothing","Explain yourself publicly","Speak to manager privately later"]},
      {q:"Peak hour, everyone busy, customer needs urgent help. What do you do?",a:["Approach and handle immediately","Tell them to wait","Find a free colleague","Acknowledge and return quickly"]},
      {q:"You have an idea to improve a work method. What do you do?",a:["Present it to manager next meeting","Implement it yourself without asking","Stay silent — not my place","Share only with a colleague"]},
      {q:"Shift ended but work isn't finished. What do you do?",a:["Finish before leaving","Hand off to next shift with update","Leave — shift is over","Ask manager"]},
      {q:"Customer asks a question you don't know. What do you say?",a:["Admit I don't know and find the answer","Guess and answer","Refer to a colleague","Say I don't have time"]},
      {q:"You notice a colleague not doing their work. What do you do?",a:["Talk to them gently","Report to manager immediately","Ignore it — not my business","Cover for them quietly"]},
      {q:"You receive two tasks simultaneously. What do you do?",a:["Prioritize by urgency and update","Start with the latest one","Ask for help immediately","Do both in parallel"]}
    ]
  },
  ru: {
    dir:"ltr", label:"Русский",
    title:"Добро пожаловать", subtitle:"Пожалуйста, заполните данные",
    fullName:"Полное имя", dob:"Дата рождения (ДД.ММ.ГГГГ)",
    next:"Далее", send:"Отправить",
    thanks:"Спасибо! Ваши данные переданы менеджеру.",
    required:"Заполните все поля", allRequired:"Ответьте на все вопросы", dobInvalid:"Неверная дата рождения",
    questions:[
      {q:"Покупатель входит в магазин и выглядит растерянно. Что вы сделаете?",a:["Немедленно подойду и предложу помощь","Подожду, пока обратится сам","Найду другого сотрудника","Продолжу текущую работу"]},
      {q:"Полка, за которую вы отвечаете, не в порядке. Что сначала?",a:["Уберу немедленно перед всем остальным","Закончу текущую задачу, потом уберу","Доложу менеджеру","Оставлю следующей смене"]},
      {q:"Менеджер просит X, но вы считаете Y лучше. Что делать?",a:["Сделаю X, как просили","Предложу Y и объясню менеджеру","Сделаю Y без спроса","Спрошу коллегу"]},
      {q:"Срочное совещание, но вы помогаете клиенту. Что важнее?",a:["Закончу с клиентом, потом приду","Сразу уйду на совещание","Попрошу коллегу заменить","Перенесу совещание"]},
      {q:"Заметили ошибку в цене товара. Что делать?",a:["Исправлю и сообщу менеджеру","Только сообщу менеджеру","Исправлю без уведомления","Оставлю — не моё дело"]},
      {q:"Злой клиент говорит громко. Что делать?",a:["Спокойно выслушаю и постараюсь решить","Сразу позову менеджера","Отвечу в том же тоне","Извинюсь и закончу разговор"]},
      {q:"Пришли на работу, коллега не явился. Что делать?",a:["Сообщу менеджеру и предложу прикрыть","Продолжу только свою работу","Спрошу коллег","Подожду указаний"]},
      {q:"Товар закончился, клиент просит его. Что скажете?",a:["Проверю склад и предложу альтернативу","Скажу, что нет, и закончу","Обещу, что завтра будет","Направлю в другой магазин"]},
      {q:"Менеджер покритиковал вас публично. Как реагируете?",a:["Приму, учтю и улучшусь","Обижусь, но промолчу","Объяснюсь публично","Поговорю с менеджером наедине потом"]},
      {q:"Час пик, все заняты, клиент срочно нуждается. Что делать?",a:["Сразу подойду и помогу","Попрошу подождать","Найду свободного коллегу","Отмечу и вернусь скорее"]},
      {q:"У вас есть идея улучшения рабочего процесса. Что делать?",a:["Представлю менеджеру на встрече","Внедрю сам без спроса","Промолчу — не моё дело","Поделюсь только с коллегой"]},
      {q:"Смена закончилась, работа не выполнена. Что делать?",a:["Закончу перед уходом","Передам следующей смене с обновлением","Уйду — смена кончилась","Спрошу менеджера"]},
      {q:"Клиент задал вопрос, ответа на который вы не знаете. Что скажете?",a:["Признаюсь и найду ответ","Угадаю и отвечу","Направлю к коллеге","Скажу, что нет времени"]},
      {q:"Заметили, что коллега не выполняет работу. Что делать?",a:["Поговорю с ним мягко","Сразу сообщу менеджеру","Проигнорирую — не моё дело","Тихо прикрою"]},
      {q:"Получили две задачи одновременно. Что делать?",a:["Расставлю приоритеты и сообщу","Начну с последней","Сразу попрошу помощи","Буду делать обе параллельно"]}
    ]
  },
  ar: {
    dir:"rtl", label:"العربية",
    title:"أهلاً وسهلاً", subtitle:"يرجى تعبئة البيانات التالية",
    fullName:"الاسم الكامل", dob:"تاريخ الميلاد (DD.MM.YYYY)",
    next:"التالي", send:"إرسال",
    thanks:"شكراً! تم إرسال بياناتك إلى المدير.",
    required:"يرجى تعبئة جميع الحقول", allRequired:"يرجى الإجابة على جميع الأسئلة", dobInvalid:"تاريخ ميلاد غير صالح",
    questions:[
      {q:"دخل عميل المتجر ويبدو تائهاً. ماذا ستفعل؟",a:["سأتوجه فوراً وأعرض المساعدة بابتسامة","سأنتظر حتى يتوجه إليّ","سأجد موظفاً آخر ليساعده","سأكمل عملي الحالي"]},
      {q:"الرف الذي تتحمل مسؤوليته غير مرتب. ما الأولوية؟",a:["سأرتبه فوراً قبل أي شيء","سأنهي المهمة الحالية ثم أرتبه","سأبلغ المدير","سأتركه للوردية القادمة"]},
      {q:"المدير طلب X لكنك تعتقد أن Y أفضل. ماذا تفعل؟",a:["سأنفذ X كما طُلب","سأقترح Y وأشرح للمدير","سأنفذ Y دون أن أسأل","سأستشير زميلاً"]},
      {q:"اجتماع عاجل وأنت تساعد عميلاً. ما الأهم؟",a:["سأنهي مع العميل ثم أحضر","سأذهب للاجتماع فوراً","سأطلب من زميل أن يأخذ مكاني","سأؤجل الاجتماع"]},
      {q:"لاحظت خطأ في سعر منتج. ماذا تفعل؟",a:["سأصحح فوراً وأبلغ المدير","سأبلغ المدير فقط","سأصحح دون إبلاغ","سأتركه – ليس من مهامي"]},
      {q:"عميل غاضب يتحدث بصوت عالٍ. ماذا تفعل؟",a:["سأستمع بهدوء وأحاول الحل","سأستدعي المدير فوراً","سأرد بنفس الأسلوب","سأعتذر وأنهي الحديث"]},
      {q:"وصلت للعمل ولاحظت غياب زميل. ماذا تفعل؟",a:["سأبلغ المدير وأعرض التغطية","سأكمل مهامي فقط","سأسأل الزملاء","سأنتظر التعليمات"]},
      {q:"المخزون فارغ وعميل يطلب منتجاً. ماذا تقول؟",a:["سأتحقق من المستودع وأقترح بديلاً","سأقول إنه غير متوفر وأنهي","سأعده بوصوله غداً","سأوجهه لمتجر آخر"]},
      {q:"المدير انتقدك علناً. كيف تتصرف؟",a:["سأقبل وأتعلم وأتحسن","سأشعر بالإهانة لكن لن أرد","سأدافع عن نفسي أمام الجميع","سأتحدث مع المدير بشكل خاص لاحقاً"]},
      {q:"ساعة الذروة والكل مشغول، عميل يحتاج مساعدة عاجلة. ماذا تفعل؟",a:["سأتوجه وأتعامل فوراً","سأطلب منه الانتظار","سأجد زميلاً فارغاً","سأشير وأعود بأسرع وقت"]},
      {q:"لديك فكرة لتحسين طريقة العمل. ماذا تفعل؟",a:["سأعرضها على المدير في الاجتماع القادم","سأطبقها بنفسي دون إذن","سأصمت – ليس من شأني","سأشاركها مع زميل فقط"]},
      {q:"انتهت وردية العمل لكن المهمة لم تكتمل. ماذا تفعل؟",a:["سأكمل قبل المغادرة","سأسلم للوردية القادمة مع تحديث","سأغادر – الوردية انتهت","سأسأل المدير"]},
      {q:"عميل سألك سؤالاً لا تعرف إجابته. ماذا تقول؟",a:["سأعترف وأجد الإجابة","سأخمن وأجيب","سأحوله لزميل","سأقول إنه ليس لدي وقت"]},
      {q:"لاحظت أن زميلاً لا يؤدي عمله. ماذا تفعل؟",a:["سأتحدث معه بلطف","سأبلغ المدير فوراً","سأتجاهل – ليس من شأني","سأغطيه بهدوء"]},
      {q:"تلقيت مهمتين في وقت واحد. ماذا تفعل؟",a:["سأرتب حسب الأولوية وأحدّث","سأبدأ بالأخيرة","سأطلب مساعدة فوراً","سأعمل على كلتيهما بالتوازي"]}
    ]
  },
  th: {
    dir:"ltr", label:"ภาษาไทย",
    title:"ยินดีต้อนรับ", subtitle:"กรุณากรอกข้อมูลของคุณ",
    fullName:"ชื่อ-นามสกุล", dob:"วันเกิด (DD.MM.YYYY)",
    next:"ถัดไป", send:"ส่ง",
    thanks:"ขอบคุณ! ข้อมูลของคุณถูกส่งถึงผู้จัดการแล้ว",
    required:"กรุณากรอกข้อมูลให้ครบ", allRequired:"กรุณาตอบทุกคำถาม", dobInvalid:"วันเกิดไม่ถูกต้อง",
    questions:[
      {q:"ลูกค้าเดินเข้ามาในร้านและดูเหมือนหลงทาง คุณจะทำอะไร?",a:["เดินเข้าหาทันทีและเสนอความช่วยเหลือด้วยรอยยิ้ม","รอให้เขาเดินมาหาเอง","หาพนักงานคนอื่นมาช่วย","ทำงานต่อไป"]},
      {q:"ชั้นวางที่คุณดูแลไม่เป็นระเบียบ อะไรก่อน?",a:["จัดทันทีก่อนสิ่งอื่น","ทำงานปัจจุบันให้เสร็จก่อน","รายงานผู้จัดการ","ทิ้งไว้ให้กะถัดไป"]},
      {q:"ผู้จัดการขอ X แต่คุณคิดว่า Y ดีกว่า คุณจะทำอะไร?",a:["ทำ X ตามที่ขอ","แนะนำ Y และอธิบายให้ผู้จัดการฟัง","ทำ Y โดยไม่ถาม","ถามเพื่อนร่วมงาน"]},
      {q:"มีประชุมด่วนแต่คุณกำลังช่วยลูกค้า อะไรสำคัญกว่า?",a:["เสร็จกับลูกค้าแล้วค่อยไปประชุม","ไปประชุมทันที","ขอให้เพื่อนแทน","เลื่อนประชุม"]},
      {q:"เห็นราคาสินค้าผิด คุณจะทำอะไร?",a:["แก้ทันทีและรายงานผู้จัดการ","รายงานผู้จัดการเท่านั้น","แก้โดยไม่รายงาน","ทิ้งไว้ — ไม่ใช่หน้าที่"]},
      {q:"ลูกค้าโกรธและพูดเสียงดัง คุณจะทำอะไร?",a:["ฟังอย่างสงบและพยายามแก้ไข","เรียกผู้จัดการทันที","ตอบกลับด้วยน้ำเสียงเดียวกัน","ขอโทษและจบการสนทนา"]},
      {q:"มาทำงานแล้วเพื่อนร่วมงานไม่มา คุณจะทำอะไร?",a:["รายงานผู้จัดการและเสนอช่วย","ทำงานของตัวเองต่อไป","ถามเพื่อน","รอคำสั่ง"]},
      {q:"สินค้าหมดและลูกค้าต้องการ คุณจะพูดอะไร?",a:["ตรวจสต็อกและเสนอทางเลือก","บอกว่าหมดแล้วและจบ","สัญญาว่าจะมีพรุ่งนี้","แนะนำร้านอื่น"]},
      {q:"ผู้จัดการวิจารณ์คุณต่อหน้าคนอื่น คุณรู้สึกและทำอะไร?",a:["รับ เรียนรู้ และพัฒนา","รู้สึกเจ็บปวดแต่ไม่พูด","อธิบายตัวเองต่อหน้าทุกคน","คุยกับผู้จัดการส่วนตัวทีหลัง"]},
      {q:"ชั่วโมงเร่งด่วน ทุกคนยุ่ง ลูกค้าต้องการความช่วยเหลือด่วน คุณจะทำอะไร?",a:["เดินเข้าหาและดูแลทันที","บอกให้รอ","หาเพื่อนที่ว่าง","รับทราบและกลับมาเร็วที่สุด"]},
      {q:"คุณมีไอเดียปรับปรุงวิธีทำงาน คุณจะทำอะไร?",a:["นำเสนอผู้จัดการในการประชุมครั้งหน้า","ทำด้วยตัวเองโดยไม่ขออนุญาต","เงียบ — ไม่ใช่หน้าที่","แชร์กับเพื่อนเท่านั้น"]},
      {q:"กะงานจบแล้วแต่งานยังไม่เสร็จ คุณจะทำอะไร?",a:["ทำให้เสร็จก่อนกลับ","ส่งต่อกะถัดไปพร้อมอัปเดต","กลับบ้าน — กะจบแล้ว","ถามผู้จัดการ"]},
      {q:"ลูกค้าถามคำถามที่คุณไม่รู้คำตอบ คุณจะพูดอะไร?",a:["ยอมรับและหาคำตอบ","เดาและตอบ","แนะนำให้ไปถามเพื่อน","บอกว่าไม่มีเวลา"]},
      {q:"สังเกตว่าเพื่อนร่วมงานไม่ทำงาน คุณจะทำอะไร?",a:["พูดคุยด้วยความอ่อนโยน","รายงานผู้จัดการทันที","เพิกเฉย — ไม่ใช่เรื่องของฉัน","ช่วยปิดบังอย่างเงียบๆ"]},
      {q:"ได้รับสองงานพร้อมกัน คุณจะทำอะไร?",a:["จัดลำดับความสำคัญและแจ้งให้ทราบ","เริ่มงานล่าสุด","ขอความช่วยเหลือทันที","ทำทั้งสองพร้อมกัน"]}
    ]
  }
};

const DEPTS = ["פלסטיקה","ביוטי","קופאי","סדרן","עונה","חשמל","מזון","אחר"];
const MANAGER_PASS = "1234";

// ─── ANALYSIS ────────────────────────────────────────────────────────────
function getSign(dob) {
  const [d,m] = dob.split(".").map(Number);
  const signs = [
    {sign:"גדי",from:[12,22],to:[1,19],traits:"שאפתן, ממושמע ויסודי. עמיד ללחץ וחרוץ מאוד.",work:"מצטיין בסביבה עם כללים ברורים ויעדים מדידים. נאמן ומסור."},
    {sign:"דלי",from:[1,20],to:[2,18],traits:"חדשני, חושב מחוץ לקופסה, אוהב שינוי.",work:"מתפקד מצוין בסביבות דינמיות. אוהב לפתור בעיות בדרכים חדשות."},
    {sign:"דגים",from:[2,19],to:[3,20],traits:"אמפתי, רגיש ויצירתי. קולט אנשים בקלות.",work:"מצטיין בשירות לקוחות. זקוק לסביבה תומכת."},
    {sign:"טלה",from:[3,21],to:[4,19],traits:"אנרגטי, יוזם ומהיר תגובה.",work:"מצטיין בתפקידים דינמיים הדורשים פעולה מהירה."},
    {sign:"שור",from:[4,20],to:[5,20],traits:"יציב, מהימן וסבלני. מוכוון-פרטים.",work:"עובד יציב ואיכותי. אינו נשחק ממשימות חוזרות. מחויב ונאמן."},
    {sign:"תאומים",from:[5,21],to:[6,20],traits:"תקשורתי, גמיש וסקרן.",work:"מצטיין בממשקי לקוחות ובמולטיטסקינג. זקוק לגיוון."},
    {sign:"סרטן",from:[6,21],to:[7,22],traits:"מטפח, נאמן ורגיש.",work:"עובד צוות מצוין. שומר על אווירה חיובית."},
    {sign:"אריה",from:[7,23],to:[8,22],traits:"כריזמטי, בעל נוכחות ומוכוון-הישגים.",work:"מצטיין בפנים לקהל. מניע ומעורר השראה."},
    {sign:"בתולה",from:[8,23],to:[9,22],traits:"אנליטי, מדויק ומוכוון-פרטים.",work:"מצטיין במשימות הדורשות דיוק. מזהה בעיות מוקדם."},
    {sign:"מאזניים",from:[9,23],to:[10,22],traits:"צודק, דיפלומטי ושואף לאיזון.",work:"מצטיין בפתרון קונפליקטים. יוצר אווירה נעימה."},
    {sign:"עקרב",from:[10,23],to:[11,21],traits:"עמוק, ממוקד ובעל חוכמה אינטואיטיבית.",work:"מצטיין בתפקידים הדורשים ריכוז. נאמן מאוד."},
    {sign:"קשת",from:[11,22],to:[12,21],traits:"אופטימי, ישיר ואוהב לימוד.",work:"מצטיין בסביבות משתנות הדורשות גמישות."},
  ];
  for (const s of signs) {
    const [fm,fd]=s.from, [tm,td]=s.to;
    if (fm <= tm) { if ((m===fm&&d>=fd)||(m>fm&&m<tm)||(m===tm&&d<=td)) return s; }
    else { if ((m===fm&&d>=fd)||(m<tm)||(m===tm&&d<=td)) return s; }
  }
  return signs[0];
}

function analyze(answers) {
  let big=0, small=0;
  answers.forEach(a => { if(a===0)big++; if(a>=2)small++; });
  const style = big>=9?"ראש גדול":big>=5?"מאוזן":"ראש קטן";
  const styleDesc = style==="ראש גדול"
    ? "המועמד הוא טיפוס 'ראש גדול' — פועל מיוזמה, מזהה בעיות לפני שמדווחים לו ולוקח אחריות."
    : style==="מאוזן"
    ? "המועמד מציג פרופיל מאוזן — יוזם כשנדרש, אך יודע גם לפעול לפי הנחיות."
    : "המועמד נוטה לפעול לפי הנחיות. מצטיין בביצוע מדויק. זקוק למסגרת ברורה.";
  return {style, styleDesc, big, small};
}

function buildReport(name, dob, answers) {
  const sign = getSign(dob);
  const an = analyze(answers);
  const [d,m,y] = dob.split(".");
  const age = new Date().getFullYear() - parseInt(y);
  const portrait = `לפניך מועמד בשם ${name}, בן/בת ${age}. ${sign.traits} ${sign.work}`;
  const interaction = `${an.styleDesc} ${an.style==="ראש גדול"?"מומלץ לתת אחריות על מחלקה ולהגדיר יעדים שבועיים. מיקרו-ניהול עלול לתסכל.":an.style==="מאוזן"?"מומלץ לשלב הנחיות ברורות עם מרחב לביטוי עצמאי.":"מומלץ לספק מסגרת עבודה ברורה עם הנחיות מפורטות."}`;
  const placement = an.style==="ראש גדול"
    ? "המחלקה האידיאלית: עונה, פלסטיקה, או כל מחלקה דינמית. פחות מתאים לקופה."
    : an.style==="מאוזן"
    ? "מתאים לרוב המחלקות. יפרח במחלקת ביוטי או מזון."
    : "מתאים לקופה, סדרן, או משימות מדויקות.";
  return {portrait, interaction, placement, sign, an, age};
}

// ─── STYLES ──────────────────────────────────────────────────────────────
const S = {
  page: {minHeight:"100vh", fontFamily:"'Segoe UI',Arial,sans-serif"},
  cardLight: {background:"#fff", borderRadius:20, padding:32, boxShadow:"0 4px 24px rgba(0,0,0,.08)"},
  cardDark: {background:"#16213e", borderRadius:20, padding:28, boxShadow:"0 4px 24px rgba(0,0,0,.4)"},
  btnGold: {width:"100%", padding:"14px", background:"linear-gradient(135deg,#c9a84c,#e8c97a)", border:"none", borderRadius:12, color:"#fff", fontSize:17, fontWeight:700, cursor:"pointer"},
  input: {width:"100%", padding:"12px 16px", border:"2px solid #e0d5c0", borderRadius:12, fontSize:16, outline:"none", boxSizing:"border-box", color:"#4a3520"},
  err: {color:"#d9534f", fontWeight:600, margin:"8px 0"}
};

// ─── CANDIDATE ───────────────────────────────────────────────────────────
function CandidateApp() {
  const [lang,setLang]=useState("he");
  const [step,setStep]=useState("info");
  const [name,setName]=useState("");
  const [dob,setDob]=useState("");
  const [answers,setAnswers]=useState(Array(15).fill(null));
  const [qi,setQi]=useState(0);
  const [err,setErr]=useState("");
  const L=LANGS[lang];

  function validDob(d){
    if(!/^\d{2}\.\d{2}\.\d{4}$/.test(d))return false;
    const[dd,mm,yy]=d.split(".").map(Number);
    return dd>=1&&dd<=31&&mm>=1&&mm<=12&&yy>=1950&&yy<=2010;
  }

  function goNext(){
    if(!name.trim()||!dob.trim())return setErr(L.required);
    if(!validDob(dob))return setErr(L.dobInvalid);
    setErr(""); setStep("q");
  }

  function pick(i){
    const a=[...answers]; a[qi]=i; setAnswers(a);
    if(qi<14)setTimeout(()=>setQi(qi+1),220);
  }

  function submit(){
    if(answers.includes(null))return setErr(L.allRequired);
    const report=buildReport(name,dob,answers);
    DB.add({name,dob,lang,answers,report});
    setStep("done");
  }

  if(step==="done") return (
    <div style={{...S.page, background:"linear-gradient(135deg,#fdf8ee,#f5edda)", display:"flex", alignItems:"center", justifyContent:"center"}}>
      <div style={{textAlign:"center",padding:48}}>
        <div style={{fontSize:72,marginBottom:16}}>✅</div>
        <h2 style={{color:"#6b5c3e",fontSize:22}}>{L.thanks}</h2>
      </div>
    </div>
  );

  return (
    <div dir={L.dir} style={{...S.page, background:"linear-gradient(135deg,#fdf8ee,#f5edda)"}}>
      <div style={{maxWidth:560,margin:"0 auto",padding:"28px 16px"}}>
        <div style={{textAlign:"center",marginBottom:28}}>
          <div style={{fontSize:44,marginBottom:8}}>🏪</div>
          <h1 style={{fontSize:26,fontWeight:800,color:"#4a3520"}}>{L.title}</h1>
          <p style={{color:"#9b8b6e",marginTop:4}}>{L.subtitle}</p>
        </div>

        {/* Lang picker */}
        <div style={{display:"flex",gap:8,flexWrap:"wrap",justifyContent:"center",marginBottom:28}}>
          {Object.entries(LANGS).map(([k,v])=>(
            <button key={k} onClick={()=>{setLang(k);setErr("");}} style={{
              padding:"7px 16px", borderRadius:20, border: lang===k?"2px solid #c9a84c":"2px solid #e0d5c0",
              background:lang===k?"#c9a84c":"#fff", color:lang===k?"#fff":"#6b5c3e",
              fontWeight:600, fontSize:13, cursor:"pointer"
            }}>{v.label}</button>
          ))}
        </div>

        {step==="info" && (
          <div style={S.cardLight}>
            <label style={{display:"block",fontWeight:600,color:"#6b5c3e",marginBottom:8}}>{L.fullName}</label>
            <input value={name} onChange={e=>setName(e.target.value)} style={{...S.input,marginBottom:20}}/>
            <label style={{display:"block",fontWeight:600,color:"#6b5c3e",marginBottom:8}}>{L.dob}</label>
            <input value={dob} onChange={e=>setDob(e.target.value)} placeholder="DD.MM.YYYY" style={{...S.input,marginBottom:20}}/>
            {err&&<p style={S.err}>{err}</p>}
            <button onClick={goNext} style={S.btnGold}>{L.next}</button>
          </div>
        )}

        {step==="q" && (
          <div style={S.cardLight}>
            {/* Progress */}
            <div style={{marginBottom:24}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:6}}>
                <span style={{fontSize:12,color:"#9b8b6e",fontWeight:600}}>{qi+1}/15</span>
                <span style={{fontSize:12,color:"#9b8b6e"}}>{Math.round(((qi+1)/15)*100)}%</span>
              </div>
              <div style={{height:6,background:"#f0e8d5",borderRadius:99}}>
                <div style={{height:"100%",width:`${((qi+1)/15)*100}%`,background:"linear-gradient(90deg,#c9a84c,#e8c97a)",borderRadius:99,transition:"width .4s"}}/>
              </div>
            </div>
            <p style={{fontSize:17,fontWeight:700,color:"#4a3520",lineHeight:1.6,marginBottom:20,minHeight:60}}>{L.questions[qi].q}</p>
            <div style={{display:"flex",flexDirection:"column",gap:10,marginBottom:20}}>
              {L.questions[qi].a.map((ans,i)=>(
                <button key={i} onClick={()=>pick(i)} style={{
                  padding:"13px 16px", border:"2px solid", textAlign:L.dir==="rtl"?"right":"left",
                  borderColor:answers[qi]===i?"#c9a84c":"#e0d5c0",
                  background:answers[qi]===i?"#fffbf0":"#fff",
                  borderRadius:12, fontSize:14, color:answers[qi]===i?"#8a6a00":"#4a3520",
                  fontWeight:answers[qi]===i?700:400, cursor:"pointer"
                }}>{ans}</button>
              ))}
            </div>
            {qi===14&&<>
              {err&&<p style={S.err}>{err}</p>}
              <button onClick={submit} style={S.btnGold}>{L.send}</button>
            </>}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── MANAGER ─────────────────────────────────────────────────────────────
function ManagerApp() {
  const [auth,setAuth]=useState(false);
  const [pass,setPass]=useState("");
  const [passErr,setPassErr]=useState("");
  const [candidates,setCandidates]=useState([]);
  const [sel,setSel]=useState(null);
  const [dept,setDept]=useState("");
  const [role,setRole]=useState("");
  const [msg,setMsg]=useState("");

  function login(){
    if(pass===MANAGER_PASS){setAuth(true);setCandidates(DB.load());}
    else setPassErr("סיסמה שגויה");
  }

  function open(c){setSel(c);setDept(c.dept||"");setRole(c.role||"");setMsg("");}

  function save(){
    if(!sel)return;
    DB.update(sel.id,{dept,role,assigned:true});
    const fresh=DB.load(); setCandidates(fresh);
    setSel({...sel,dept,role,assigned:true});
    setMsg("✅ המועמד שובץ בהצלחה!");
    setTimeout(()=>setMsg(""),3000);
  }

  if(!auth) return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"#1a1a2e"}}>
      <div style={{background:"#16213e",padding:44,borderRadius:24,width:320,textAlign:"center"}}>
        <div style={{fontSize:44,marginBottom:12}}>🔐</div>
        <h2 style={{color:"#e8c97a",marginBottom:24}}>כניסת מנהל</h2>
        <input type="password" value={pass} onChange={e=>setPass(e.target.value)}
          onKeyDown={e=>e.key==="Enter"&&login()} placeholder="סיסמה" dir="ltr"
          style={{width:"100%",padding:"12px",borderRadius:10,border:"none",background:"#0f3460",color:"#fff",fontSize:18,textAlign:"center",outline:"none",marginBottom:12,boxSizing:"border-box"}}/>
        {passErr&&<p style={{color:"#e74c3c",marginBottom:12}}>{passErr}</p>}
        <button onClick={login} style={S.btnGold}>כניסה</button>
        <p style={{color:"#4a4a6a",marginTop:12,fontSize:12}}>סיסמה: 1234</p>
      </div>
    </div>
  );

  const pending=candidates.filter(c=>!c.assigned);
  const assigned=candidates.filter(c=>c.assigned);

  // Detail
  if(sel) {
    const r=sel.report;
    return (
      <div dir="rtl" style={{...S.page,background:"#1a1a2e",padding:"20px 16px"}}>
        <div style={{maxWidth:680,margin:"0 auto"}}>
          <button onClick={()=>setSel(null)} style={{background:"transparent",border:"2px solid #2e4a6a",borderRadius:10,color:"#a0b0c0",padding:"8px 18px",cursor:"pointer",marginBottom:20,fontSize:14}}>← חזרה</button>
          <div style={S.cardDark}>
            <div style={{display:"flex",alignItems:"center",gap:14,marginBottom:24,flexWrap:"wrap"}}>
              <div style={{width:52,height:52,borderRadius:"50%",background:"linear-gradient(135deg,#c9a84c,#e8c97a)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:22,flexShrink:0}}>👤</div>
              <div>
                <h2 style={{color:"#e8c97a",margin:0,fontSize:20}}>{sel.name}</h2>
                <p style={{color:"#6b7aaa",margin:0,fontSize:13}}>{sel.dob} · {LANGS[sel.lang]?.label}</p>
              </div>
              {sel.assigned&&<span style={{marginRight:"auto",background:"#0d4f2e",color:"#4caf7f",padding:"4px 12px",borderRadius:20,fontSize:12,fontWeight:700}}>✓ משובץ</span>}
            </div>

            {[
              {title:"👤 דיוקן אופי", color:"#c9a84c", body:r.portrait, tags:[`מזל: ${r.sign.sign}`,`גיל: ${r.age}`,r.an.style]},
              {title:"🤝 פרוטוקול אינטראקציה", color:"#7c5cbf", body:r.interaction},
              {title:"📍 המלצת שיבוץ", color:"#2e86ab", body:r.placement},
            ].map(sec=>(
              <div key={sec.title} style={{marginBottom:16,background:"#0f1a2e",borderRadius:14,padding:18,borderRight:`4px solid ${sec.color}`}}>
                <h3 style={{color:sec.color,margin:"0 0 10px",fontSize:15}}>{sec.title}</h3>
                <p style={{color:"#d0d0e8",lineHeight:1.8,margin:0}}>{sec.body}</p>
                {sec.tags&&<div style={{display:"flex",gap:8,marginTop:10,flexWrap:"wrap"}}>
                  {sec.tags.map((t,i)=><span key={i} style={{background:i===2?"rgba(201,168,76,.2)":"rgba(255,255,255,.06)",color:i===2?"#e8c97a":"#a0b0c0",padding:"3px 12px",borderRadius:20,fontSize:12,fontWeight:600}}>{t}</span>)}
                </div>}
              </div>
            ))}

            <div style={{background:"#0f1a2e",borderRadius:14,padding:18,borderRight:"4px solid #4caf7f"}}>
              <h3 style={{color:"#4caf7f",margin:"0 0 14px",fontSize:15}}>✍️ שיבוץ ותפקיד</h3>
              <div style={{display:"flex",gap:12,flexWrap:"wrap",marginBottom:14}}>
                <div style={{flex:1,minWidth:140}}>
                  <label style={{display:"block",color:"#a0b0c0",marginBottom:6,fontSize:13}}>מחלקה</label>
                  <select value={dept} onChange={e=>setDept(e.target.value)} style={{width:"100%",padding:"10px",borderRadius:10,border:"none",background:"#0f3460",color:"#fff",fontSize:14,outline:"none"}}>
                    <option value="">בחר...</option>
                    {DEPTS.map(d=><option key={d}>{d}</option>)}
                  </select>
                </div>
                <div style={{flex:1,minWidth:140}}>
                  <label style={{display:"block",color:"#a0b0c0",marginBottom:6,fontSize:13}}>תפקיד</label>
                  <input value={role} onChange={e=>setRole(e.target.value)} placeholder="למשל: קופאי.ת" style={{width:"100%",padding:"10px",borderRadius:10,border:"none",background:"#0f3460",color:"#fff",fontSize:14,outline:"none",boxSizing:"border-box"}}/>
                </div>
              </div>
              {msg&&<p style={{color:"#4caf7f",fontWeight:700,marginBottom:10}}>{msg}</p>}
              <button onClick={save} style={S.btnGold}>💾 שמירה ושיבוץ</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // List
  return (
    <div dir="rtl" style={{...S.page,background:"#1a1a2e",padding:"20px 16px"}}>
      <div style={{maxWidth:780,margin:"0 auto"}}>
        <div style={{textAlign:"center",marginBottom:28}}>
          <h1 style={{color:"#e8c97a",fontSize:26,fontWeight:800}}>🏪 ניהול מועמדים</h1>
          <p style={{color:"#6b7aaa"}}>פרוטוקול קליטה וניתוח</p>
        </div>

        <div style={{display:"flex",gap:14,marginBottom:28,flexWrap:"wrap"}}>
          {[["ממתינים",pending.length,"#c9a84c"],["משובצים",assigned.length,"#4caf7f"],["סה״כ",candidates.length,"#2e86ab"]].map(([l,v,c])=>(
            <div key={l} style={{flex:1,minWidth:120,background:"#16213e",borderRadius:14,padding:"18px 20px",textAlign:"center",borderTop:`3px solid ${c}`}}>
              <div style={{fontSize:28,fontWeight:800,color:c}}>{v}</div>
              <div style={{color:"#6b7aaa",fontSize:13,marginTop:4}}>{l}</div>
            </div>
          ))}
        </div>

        {pending.length>0&&<>
          <h3 style={{color:"#e8c97a",marginBottom:12}}>⏳ ממתינים לעיון</h3>
          {pending.map(c=>(
            <div key={c.id} onClick={()=>open(c)} style={{background:"#16213e",borderRadius:14,padding:"14px 18px",marginBottom:10,cursor:"pointer",border:"2px solid #1e2d50",display:"flex",alignItems:"center",gap:14}}>
              <div style={{width:42,height:42,borderRadius:"50%",background:"linear-gradient(135deg,#c9a84c,#e8c97a)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:18,flexShrink:0}}>👤</div>
              <div style={{flex:1,minWidth:0}}>
                <p style={{color:"#e0e0f0",fontWeight:700,margin:0}}>{c.name}</p>
                <p style={{color:"#6b7aaa",margin:0,fontSize:12}}>{c.dob} · {LANGS[c.lang]?.label}</p>
              </div>
              <span style={{background:"rgba(201,168,76,.2)",color:"#e8c97a",padding:"3px 12px",borderRadius:20,fontSize:12,fontWeight:600,flexShrink:0}}>{c.report?.an?.style}</span>
            </div>
          ))}
        </>}

        {assigned.length>0&&<>
          <h3 style={{color:"#4caf7f",margin:"24px 0 12px"}}>✅ טבלת שיבוץ צוות</h3>
          <div style={{background:"#16213e",borderRadius:16,overflow:"hidden"}}>
            <div style={{overflowX:"auto"}}>
              <table style={{width:"100%",borderCollapse:"collapse",minWidth:400}}>
                <thead>
                  <tr style={{background:"#0f3460"}}>
                    {["שם","מחלקה","תפקיד","סגנון"].map(h=><th key={h} style={{padding:"12px 14px",color:"#e8c97a",textAlign:"right",fontSize:13}}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {assigned.map((c,i)=>(
                    <tr key={c.id} onClick={()=>open(c)} style={{cursor:"pointer",borderBottom:"1px solid #0f3460",background:i%2===0?"transparent":"#131d33"}}>
                      <td style={{padding:"12px 14px",color:"#e0e0f0"}}>{c.name}</td>
                      <td style={{padding:"12px 14px",color:"#a0b0d0"}}>{c.dept}</td>
                      <td style={{padding:"12px 14px",color:"#a0b0d0"}}>{c.role}</td>
                      <td style={{padding:"12px 14px"}}><span style={{background:"rgba(201,168,76,.2)",color:"#e8c97a",padding:"3px 10px",borderRadius:20,fontSize:12,fontWeight:600}}>{c.report?.an?.style}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>}

        {candidates.length===0&&(
          <div style={{textAlign:"center",padding:60,color:"#4a4a6a"}}>
            <div style={{fontSize:44,marginBottom:12}}>📋</div>
            <p>עדיין אין מועמדים שמילאו את השאלון</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── ROOT ─────────────────────────────────────────────────────────────────
function App() {
  const [mode,setMode]=useState("select");
  if(mode==="candidate") return <CandidateApp/>;
  if(mode==="manager") return <ManagerApp/>;

  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"linear-gradient(135deg,#1a1a2e,#16213e,#0f3460)"}}>
      <div style={{textAlign:"center",padding:32}}>
        <div style={{fontSize:52,marginBottom:12}}>🏪</div>
        <h1 style={{color:"#e8c97a",fontSize:28,fontWeight:900,marginBottom:6}}>מערכת קליטת עובדים</h1>
        <p style={{color:"#6b7aaa",marginBottom:40}}>בחר את הממשק המתאים</p>
        <div style={{display:"flex",gap:16,flexWrap:"wrap",justifyContent:"center"}}>
          {[
            {icon:"📝",label:"אני מועמד",sub:"מילוי שאלון קליטה",m:"candidate",gold:true},
            {icon:"👔",label:"אני מנהל",sub:"צפייה וניהול מועמדים",m:"manager",gold:false}
          ].map(b=>(
            <button key={b.m} onClick={()=>setMode(b.m)} style={{
              width:185,padding:"24px 16px",borderRadius:20,
              border:b.gold?"none":"2px solid #2e4a6a",
              background:b.gold?"linear-gradient(135deg,#c9a84c,#e8c97a)":"#16213e",
              color:b.gold?"#1a1a2e":"#a0b0d0",cursor:"pointer",textAlign:"center",
              boxShadow:b.gold?"0 8px 28px rgba(201,168,76,.3)":"none"
            }}>
              <div style={{fontSize:36,marginBottom:8}}>{b.icon}</div>
              <div style={{fontSize:17,fontWeight:800}}>{b.label}</div>
              <div style={{fontSize:12,marginTop:4,opacity:.8}}>{b.sub}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
</script>
</body>
</html>
