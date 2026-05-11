from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

# In-memory sessions keyed by chat_id
sessions = {}
START, ADD_PERSON, ADD_EXPENSE_PERSON, ADD_EXPENSE_AMOUNT, IDLE = range(5)

def get_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt)] for opt in options],
        resize_keyboard=True, one_time_keyboard=True
    )

def calc_report(session):
    people = session["people"]
    n = len(people)
    if n < 2 or not session["expenses"]:
        return "Недостаточно данных для расчёта."

    totals = {p: 0 for p in people}
    for it in session["expenses"]:
        totals[it["payer"]] += it["amount"]

    full_total = sum(totals.values())
    share = full_total / n
    diffs = {p: totals[p] - share for p in people}

    transactions = []
    debtors = [p for p in people if diffs[p] < -0.01]
    creditors = [p for p in people if diffs[p] > 0.01]

    i, j = 0, 0
    debtors.sort(key=lambda x: diffs[x])
    creditors.sort(key=lambda x: -diffs[x])

    d = {p: round(diffs[p], 2) for p in people}
    while i < len(debtors) and j < len(creditors):
        debtor, creditor = debtors[i], creditors[j]
        owe = min(-d[debtor], d[creditor])
        if owe < 0.01: break
        transactions.append((debtor, creditor, owe))
        d[debtor] += owe
        d[creditor] -= owe
        if abs(d[debtor]) < 0.01: i += 1
        if abs(d[creditor]) < 0.01: j += 1

    lines = []
    lines.append("Итоговые траты:\n" + "\n".join(
        [f"• {p}: {totals[p]:.2f}₽ (отклонение от среднего: {diffs[p]:+.2f}₽)" for p in people]
    ))
    lines.append(f"\n🧾 Всего потрачено: {full_total:.2f}₽\n"
                 f"Доля на каждого: {share:.2f}₽\n")
    if transactions:
        lines.append("Переводы для баланса:")
        for debtor, creditor, amount in transactions:
            lines.append(f"— {debtor}  →  {creditor}: {amount:.2f}₽")
    else:
        lines.append("Все уравнены, никто никому ничего не должен 🎉")

    return "\n".join(lines)

def basic_message_handler(update, bot, default_reply="Скоро бот заработает…"):
    try:
        message = update.get("message") or update.get("edited_message")
        if not message:
            return 'ok'    # Ignore service, inline, etc

        chat_id = message['chat']['id']
        text = message.get('text', '').strip()

        # Сессия и состояние
        if chat_id not in sessions:
            sessions[chat_id] = {
                "state": START,
                "people": [],
                "expenses": [],
                "temp": {}
            }
        session = sessions[chat_id]
        state = session["state"]

        def send(text, options=None, remove_keyboard=False):
            if options:
                bot.sendMessage(chat_id, text, reply_markup=get_keyboard(options))
            elif remove_keyboard:
                bot.sendMessage(chat_id, text, reply_markup={'remove_keyboard': True})
            else:
                bot.sendMessage(chat_id, text)

        # /start и повторный старт
        if text in ('/start', 'Начать', 'Старт', 'Start'):
            sessions[chat_id] = {
                "state": ADD_PERSON,
                "people": [],
                "expenses": [],
                "temp": {}
            }
            send(
                "👋 Привет! Этот бот поможет разделить траты между друзьями.\n"
                "1. Добавьте всех участников отдыха кнопкой ниже.\n"
                "2. Затем добавляйте траты.\n"
                "3. Посмотрите, кто кому сколько должен!\n\n"
                "Нажми «Добавить участника», чтобы начать.",
                ["Добавить участника"]
            )
            return 'ok'

        if text == "Сбросить всё":
            sessions[chat_id] = {
                "state": ADD_PERSON,
                "people": [],
                "expenses": [],
                "temp": {}
            }
            send("Данные сброшены! Добавьте участников.", ["Добавить участника"])
            return 'ok'

        if text == "Показать итог":
            report = calc_report(session)
            send(report, ["Добавить трату", "Сбросить всё"])
            return 'ok'

        if session["state"] == ADD_PERSON:
            if text == "Добавить участника":
                session["state"] = ADD_PERSON
                send("Напишите имя участника:", remove_keyboard=True)
            elif text == "Добавить трату":
                if len(session["people"]) < 2:
                    send("Добавьте хотя бы двух участников!", ["Добавить участника"])
                    return 'ok'
                session["state"] = ADD_EXPENSE_PERSON
                send("Кто оплатил трату?", session["people"])
            elif text and text not in (
                "Добавить участника", "Добавить трату", "Показать итог", "Сбросить всё"
            ):
                name = text
                if name in session["people"]:
                    send(f"Участник {name} уже есть! (Можно ввести другое имя.)")
                else:
                    session["people"].append(name)
                    send(f"Добавлен: {name}", ["Добавить участника", "Добавить трату", "Показать итог", "Сбросить всё"])
            else:
                send("Выберите действие кнопкой.")
        elif session["state"] == ADD_EXPENSE_PERSON:
            if text in session["people"]:
                session["temp"]["payer"] = text
                session["state"] = ADD_EXPENSE_AMOUNT
                send("На какую сумму (₽)? Например: 1234", remove_keyboard=True)
            else:
                send("Выберите, кто оплатил, кнопкой из списка.")
        elif session["state"] == ADD_EXPENSE_AMOUNT:
            try:
                amount = float(text.replace(",", "."))
                session["expenses"].append({"payer": session["temp"]["payer"], "amount": amount})
                session["state"] = ADD_PERSON
                send(
                    f"Добавлено: {session['temp']['payer']} оплатил {amount:.2f}₽",
                    ["Добавить трату", "Показать итог", "Сбросить всё"])
                session["temp"] = {}
            except:
                send("Пожалуйста, введите сумму числом. Например: 1234")
        else:
            # неизвестное состояние — ресет
            sessions[chat_id] = {
                "state": ADD_PERSON,
                "people": [],
                "expenses": [],
                "temp": {}
            }
            send("Ошибка состояния. Всё сброшено!", ["Добавить участника"])
        return 'ok'
    except Exception as e:
        print(e)
        if 'message' in locals():
            chat_id = message['chat']['id']
            bot.sendMessage(chat_id, default_reply)
        return 'ok'
