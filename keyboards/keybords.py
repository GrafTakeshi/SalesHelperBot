from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

y_n_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да'),
         KeyboardButton(text='Нет')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='/start')]],
    resize_keyboard=True, one_time_keyboard=True
)

work_day_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='CheckIn')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

send_geo = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отправить гео', request_location=True)]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

end_day_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='CheckOut/Продажи')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

sales_report = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отчет по продажам за день')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

sv_start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Моя Команда'),
         KeyboardButton(text='Продажи')],
        [KeyboardButton(text='Визит')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

sv_team = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мои Сотрудники')],
        [KeyboardButton(text='Активировать сотрудника')],
        [KeyboardButton(text='Деактивировать сотрудника')],
        [KeyboardButton(text='Уволить')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

sv_Sales = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='За день')],
        [KeyboardButton(text='За неделю')],
        [KeyboardButton(text='За месяц')]
    ],
    resize_keyboard=True, one_time_keyboard=True
)