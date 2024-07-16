import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from config import TOKEN, SICRET_CODE, ADMIN_ID
from db_module.db_func import welcome, registr_new_user_data, add_check_in, add_check_out, add_sales, get_info, get_id
from keyboards.keybords import y_n_kb, start_kb, send_geo, sv_team, sv_start_kb, sv_Sales
from aiogram.fsm.context import FSMContext
from states import Welcome, RegisterNewUser, ChekInn, ChekOutt, SVDesk
from db_module.supervisor import get_team, get_ids, get_info_id, \
    get_tt_list, activate, deactivate, get_sale_day, get_sale_petiod, get_sv_id
import logging
import asyncio
import requests

dp = Dispatcher()
bot = Bot(token=TOKEN, parse_mode='HTML')


@dp.message(Command('start', 'Start'))
async def start(message: Message, state: FSMContext):
    await state.set_state(Welcome.start)
    await welcome(message, state)


@dp.message(Command('help', 'Help'))
async def start(message: Message):
    await message.answer(text='Я бот-помощник комманды продаж Artel \n '
                              'Используйте комманду <b>\Start</b> для начала работы \n \n '
                              'Текущий функционал позволяет отслеживать приход/уход '
                              'а так же собирать данные о продажах!\n \n'
                              ' Функционал доробатывается и пополняется', reply_markup=start_kb)


# Регистрация нового пользователя
@dp.message(Welcome.invite)
async def invite(message: Message, state: FSMContext):
    if message.text == SICRET_CODE:
        await message.answer(text=f'Добро пожаловать в команду {message.from_user.first_name} Давай зарегистрируем тебя'
                                  f'. Для Начала представься и введи свое имя!')
        await state.set_state(RegisterNewUser.name)
    else:
        await message.answer(text=f'Код не верный, попробуйте еще раз или запросите код у своего супервайзера')
        await state.set_state(Welcome.invite)


@dp.message(RegisterNewUser.name)
async def registr_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterNewUser.sname)
    await message.answer(text='Отлеично теперь введи свою фамилию')


@dp.message(RegisterNewUser.sname)
async def registr_sname(message: Message, state: FSMContext):
    await state.update_data(sname=message.text)
    await state.set_state(RegisterNewUser.lname)
    await message.answer(text='Отлеично теперь отчество')


@dp.message(RegisterNewUser.lname)
async def registr_lname(message: Message, state: FSMContext):
    await state.update_data(lname=message.text)
    await state.set_state(RegisterNewUser.team)
    await message.answer(text='Еще последний вопрос: введи номер твоей комманды?')


@dp.message(RegisterNewUser.team)
async def registr_team(message: Message, state: FSMContext):
    await state.update_data(team=message.text)
    data = await state.get_data()

    await message.answer(text=f'Давай проверим твои данные? \n'
                              f'Твое Имя:<b> {data["name"]}</b> \n'
                              f'Твоя Фамилия: <b>{data["sname"]}</b> \n'
                              f'Твое отчество: <b>{data["lname"]}</b> \n'
                              f'Выбранная комманда: <b>{data["team"]}</b> ', reply_markup=y_n_kb)
    await state.set_state(RegisterNewUser.conform)


@dp.message(RegisterNewUser.conform)
async def registr_team(message: Message, state: FSMContext):
    if message.text.lower() == 'да':
        await message.answer(text='Вы успешно завершили регистрацию! обратитесь к супервайзуеру для активации Аккаунта'
                                  'после активации возобновите работу с ботом', reply_markup=start_kb)
        data = await state.get_data()
        name = data["name"]
        sname = data["sname"]
        lname = data["lname"]
        await registr_new_user_data(message, state, name, sname, lname)
        inf = await get_info(message.from_user.id)
        await bot.send_message(chat_id=await get_sv_id(inf['team']), text=f'пользователь'
                                                                          f' {sname} {name}'
                                                                          f' зарегистрирован в вашу команду')

    else:
        await message.answer(text='Повтарите процедуру регистрации с начала', reply_markup=start_kb)
        await state.clear()
        await state.set_state(Welcome.start)


# Чек ин пользователя
@dp.message(ChekInn.chek_in)
async def invite(message: Message, state: FSMContext):
    await message.answer(text='Отправь геопозицию', reply_markup=send_geo)
    await state.set_state(ChekInn.get_location)


@dp.message(ChekInn.get_location)
async def invite(message: Message, state: FSMContext):
    if message.content_type == 'location':
        await state.update_data(long=message.location.longitude, lat=message.location.latitude)
        await message.answer(text='Теперь отправь свое фото с рабочего места')
        await state.set_state(ChekInn.get_photo)
    else:
        await message.reply(text='То что вы отправили не содержит данных геолокации,'
                                 ' отправьте свою геопозицию', reply_markup=send_geo)
        await state.set_state(ChekInn.get_location)


@dp.message(ChekInn.get_photo)
async def invite(message: Message, state: FSMContext):
    if message.content_type == 'photo':
        name = message.from_user.first_name
        p_id = message.photo[3].file_id
        URI = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id='
        resp = requests.get(URI + p_id)
        img_path = resp.json()['result']['file_path']
        # задел на загрузку фоток в базу.
        # img = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        # print(f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        await state.update_data(photo_url=f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        data = await state.get_data()
        ph_url = data["photo_url"]
        lat = data["lat"]
        long = data["long"]
        await add_check_in(message.from_user.id, ph_url, lat, long)
        inf = await get_info(message.from_user.id)

        await bot.send_message(chat_id=await get_sv_id(inf['team']), text=f'Пользователь {name} начал рабочий '
                                                                          f'день в {datetime.datetime.now()}'[:-7])
        await bot.forward_message(chat_id=await get_sv_id(inf['team']),
                                  from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(text=f'Отлично ! Уведомомлю вашего супервайзера о том, что вы начали рабочий день!'
                                  f'не забывайте <b>сделать чек-аут</b> а так же <b>Отчет по продажам </b>'
                                  f'без этого рабочая смена <b>не будет учтена</b>', reply_markup=start_kb)
        await state.clear()
        await state.set_state(Welcome.start)

    else:
        await message.reply(text='То что вы отправили не является фотографией, переделайте фото и повторите отправку')
        await state.set_state(ChekInn.get_photo)


# Чек аут пользователя
@dp.message(ChekOutt.chek_out)
async def invite(message: Message, state: FSMContext):
    await message.answer(text='Давай отравим геопозицию, убедись что доступ к геолокации разрешен',
                         reply_markup=send_geo)
    await state.set_state(ChekOutt.get_location_out)


@dp.message(ChekOutt.get_location_out)
async def invite(message: Message, state: FSMContext):
    if message.content_type == 'location':
        await state.update_data(long=message.location.longitude, lat=message.location.latitude)
        await message.answer(text='Теперь отправь свое фото с рабочего места')
        await state.set_state(ChekOutt.get_photo)
    else:
        await message.reply(text='То что вы отправили не содержит данных геолокации,'
                                 ' отправьте свою геопозицию', reply_markup=send_geo)
        await state.set_state(ChekOutt.get_location_out)


@dp.message(ChekOutt.get_photo)
async def invite(message: Message, state: FSMContext):
    if message.content_type == 'photo':
        name = message.from_user.first_name
        p_id = message.photo[3].file_id
        URI = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id='
        resp = requests.get(URI + p_id)
        img_path = resp.json()['result']['file_path']
        # задел на загрузку фоток в базу.
        # img = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        # print(f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        await state.update_data(photo_url=f'https://api.telegram.org/file/bot{TOKEN}/' + img_path)
        data = await state.get_data()
        ph_url = data["photo_url"]
        lat = data["lat"]
        long = data["long"]
        check_in_data = await add_check_out(message.from_user.id, ph_url, lat, long)
        inf = await get_info(message.from_user.id)

        await bot.send_message(chat_id=await get_sv_id(inf['team']), text=f'Пользователь {name} Завершил рабочий '
                                                                          f'день в {datetime.datetime.now()}'[
                                                                          :-7] + f' Всего отработано '
                                                                                 f'{(datetime.datetime.now() - check_in_data)}'[
                                                                                 :-7])
        await bot.forward_message(chat_id=await get_sv_id(inf['team']), from_chat_id=message.chat.id,
                                  message_id=message.message_id)
        await message.answer(text=f'Отлично! Уведомомлю вашего супервайзера о том, что вы завершили рабочий день!'
                                  f'Всего отработано {(datetime.datetime.now() - check_in_data)}'[:-7])
        await message.answer(text='Отправье свои продажи в формате: <b>"количество_в_штуках цена в рублях"</b> \n'
                                  ' например продалось 8 позиций на сумму 245756 Рублей ваш ответ Боту: \n '
                                  '<b>8 24575</b>')
        await state.set_state(ChekOutt.get_sales)

    else:
        await message.reply(text='То что вы отправили не является фотографией, переделайте фото и повторите отправку')
        await state.set_state(ChekOutt.get_photo)


@dp.message(ChekOutt.get_sales)
async def get_sales(message: Message, state: FSMContext):
    if ' ' not in message.text:
        await bot.send_message(chat_id=message.from_user.id, text=f'Некоректный ввод повторите операцию')
        await state.set_state(ChekOutt.get_sales)
    if message.text.split()[0].isdigit() and message.text.split()[1].isdigit():
        pics = int(message.text.split()[0])
        seles = int(message.text.split()[1])
        await add_sales(message.from_user.id, pics, seles)
        await message.answer(text='Ваш отчет записан', reply_markup=start_kb)
        inf = await get_info(message.from_user.id)
        await bot.send_message(chat_id=await get_sv_id(inf['team']), text=f'Пользователь {message.from_user.first_name}'
                                                                          f' продал {pics} Штук, '
                                                                          f'на суммму {seles} Рублей')
        await state.set_state(Welcome.start)
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f'Некоректный ввод повторите операцию')
        await state.set_state(ChekOutt.get_sales)


# Выбор меню супервайзера
@dp.message(SVDesk.sv_choise)
async def sv_ch(message: Message, state: FSMContext):
    if message.text.lower() == 'моя команда':
        await message.answer(text='Меню команды', reply_markup=sv_team)
        await state.set_state(SVDesk.sv_choise_team)
    elif message.text.lower() == 'продажи':
        await message.answer(text='Меню Продажи', reply_markup=sv_Sales)
        await state.set_state(SVDesk.sv_sales)
    elif message.text.lower() == 'визит':
        await message.answer(text='Меню Визит. Здесь будет функционал')
        await state.set_state(SVDesk.sv_start)
    else:
        await message.reply(text='Неверная комманда! Выберете команду из списка', reply_markup=start_kb)
        await state.set_state(Welcome.start)


@dp.message(SVDesk.sv_choise_team)
async def sv_ch(message: Message, state: FSMContext):
    if message.text.lower() == 'мои сотрудники':
        team = await get_team(message.from_user.id, 1)
        await message.answer(text=team, reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)
    elif message.text.lower() == 'активировать сотрудника':
        await message.answer(text='Эти сотрудники ждут активации: ')
        team = await get_team(message.from_user.id, 0)
        await message.answer(text=team, reply_markup=sv_start_kb)
        await message.answer(text='Введите ID сотрудника которого хотите активировать')
        await state.set_state(SVDesk.sv_choise_aktivate)
    elif message.text.lower() == 'деактивировать сотрудника':
        team = await get_team(message.from_user.id, 1)
        await message.answer(text=team, reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise_deaktivate)
    elif message.text.lower() == 'уволить':
        await message.answer(text='Внимание!!! для продолжения введите любое слово', reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise_fier)
    else:
        await message.reply(text='Неверная комманда! Выберете команду из списка', reply_markup=start_kb)
        await state.set_state(Welcome.start)


@dp.message(SVDesk.sv_choise_aktivate)
async def sv_aktivate(message: Message, state: FSMContext):
    id = message.text
    aids = await get_ids(message.from_user.id, 0)
    if id.isdigit() and int(id) in aids:
        worker = await get_info(await get_info_id(id))
        await message.answer(text=f'вы выбрали сотрудника {worker["sname"]} {worker["name"]} \n \n'
                                  f'На какую точку Хотите устроить сотрудника? \n'
                                  f'Введите номер магазина из SAP MVM. допускаются только английские буквы и цифры \n'
                                  f'пример воода "A197" ')
        await state.update_data(id=message.text)
        await state.set_state(SVDesk.sv_choise_aktivate_choise)


@dp.message(SVDesk.sv_choise_aktivate_choise)
async def sv_aktivate_choise(message: Message, state: FSMContext):
    choise = message.text.upper()
    data = await state.get_data()
    if 0 <= len(choise) <= 6 and choise in await get_tt_list():
        await activate(choise, data['id'])
        await message.reply(text='Назначил сотрудника на выбранную вами точку', reply_markup=sv_start_kb)
        await state.clear()
        await state.set_state(SVDesk.sv_choise)
    else:
        await message.reply(text='Что то пошло не так, повтороите процедуру с начала', reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)


@dp.message(SVDesk.sv_choise_fier)
async def sv_fier(message: Message, state: FSMContext):
    await message.answer(text='Сотрудник будет полностью удален из системы, включая отчеты по продажам! \n'
                              'Настоятельно рекомендуется не удалять сотрудников до закрытия рассчетного периода!\n'
                              'Если Хотите приосановить доступ, используйте Деактивировать в меню "МОЯ КОМАНДА"')
    team = await get_team(message.from_user.id, 1)
    await message.answer(text=team)
    await message.answer(text='Введите ID Сотрудника из списка выше для увольнения!')
    await state.set_state(SVDesk.sv_choise_fier_choise)


@dp.message(SVDesk.sv_choise_fier_choise)
async def sv_fier_kill(message: Message, state: FSMContext):
    await message.answer(text='функционал в доработке', reply_markup=sv_start_kb)
    await state.set_state(SVDesk.sv_choise)


@dp.message(SVDesk.sv_choise_deaktivate)
async def sv_deaktivate(message: Message, state: FSMContext):
    id = message.text
    aids = await get_ids(message.from_user.id, 1)
    if id.isdigit() and int(id) in aids:
        text = await deactivate(id)
        await message.answer(text=text, reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)
    else:
        await message.answer(text='Неверный ввод, повторите', reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)


@dp.message(SVDesk.sv_sales)
async def sv_sales(message: Message, state: FSMContext):
    team = await get_info(message.from_user.id)
    team = team['team']
    if message.text.lower() == 'за день':
        await message.answer(text=await get_sale_day(team), reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)
    elif message.text.lower() == 'за неделю':
        period = datetime.datetime.today().weekday()
        priod = datetime.timedelta(days=period)
        await message.answer(text=await get_sale_petiod(team, priod), reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)
    elif message.text.lower() == 'за месяц':
        priod = datetime.datetime.utcnow() - datetime.datetime.today().replace(day=1)
        await message.answer(text=await get_sale_petiod(team, priod), reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)
    else:
        await message.answer(text='Неверный ввод, повторите', reply_markup=sv_start_kb)
        await state.set_state(SVDesk.sv_choise)


@dp.message()
async def all(message: Message, state: FSMContext):
    await message.reply(text='Неверная комманда', reply_markup=start_kb)
    await state.set_state(Welcome.start)


async def starting():
    logging.basicConfig(level=logging.INFO)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(starting())
