from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DSN
from datetime import datetime
from db_module.models import Users, UserProffile, Role, Team, TT, CheckIn, CheckOut, create_tables, SalesReport
from aiogram.types import Message, input_text_message_content
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from states import Welcome, RegisterNewUser, ChekInn, ChekOutt, SVDesk
from keyboards.keybords import y_n_kb, start_kb, work_day_kb, end_day_kb, sv_start_kb


engine = create_engine(DSN)
Session = sessionmaker(bind=engine)


async def welcome(message: Message, state):
    cid = message.from_user.id
    session = Session()
    create_tables(engine)
    userslist = session.query(Users.tg_user_id).all()
    if any(cid in usertyp for usertyp in userslist):
        info = await get_info(cid)
        if info['status']:
            if await get_role(cid) == 'supervisor':
                await message.answer(text='Добро пожаловать в кабинет супервайзера. '
                                          'Функционал в доработке.', reply_markup=sv_start_kb)
                await state.set_state(SVDesk.sv_choise)
            else:
                id = await get_id(cid)
                if await sale_date(id):
                    await message.answer(text='Рабочая смена завершена, Возвращайтесь завтра')
                    await state.set_state(Welcome.start)
                elif await check_in_today(id):
                    await message.answer(text=f'Продолжим? Для завершения дня пора выполнить  '
                                              f'CheckOut, и отчет по продажам', reply_markup=end_day_kb)
                    await state.set_state(ChekOutt.chek_out)
                else:

                    await message.answer(text=f'С возвращением {message.from_user.first_name} давай '
                                              f'начнем рабочий день', reply_markup=work_day_kb)
                    await state.set_state(ChekInn.chek_in)
        else:
            await message.answer(text=f'С возвращением {message.from_user.first_name} твой пройиль еще не активирован! '
                                      f'обратись к своему супервайзеру для активации')
            await state.set_state(Welcome.start)
        session.close()
    else:
        await message.answer(
            text=f'{message.from_user.first_name}! Добро пожаловать в рабочий бот команды Artel-Russ!')
        await message.answer('Введите инвайт код полученый от вашего супервайзера')
        await state.set_state(Welcome.invite)


async def registr_new_user_data(message: Message, state, name, sname, lname):
    cid = message.from_user.id
    session = Session()
    inserted_id = Users(tg_user_id=cid)
    session.add(inserted_id)
    session.flush()
    session.commit()
    q = UserProffile(tg_user_id=inserted_id.id, name=name, sname=sname,
                     lname=lname, team=1, role=3, tt_code=1, status=False)
    session.add(q)
    session.commit()
    session.close()
    await state.clear()
    await state.set_state(Welcome.start)


async def get_id(cid):
    a = ''
    session = Session()
    for ID in session.query(Users.id).filter_by(tg_user_id=cid):
        a = ID[0]
    return a


async def get_info(cid):
    a = ''
    uinfo = {}
    session = Session()
    for ID in session.query(Users.id).filter_by(tg_user_id=cid):
        a = ID[0]
    for info in session.query(UserProffile).filter_by(tg_user_id=a):
        uinfo['name'] = info.name
        uinfo['sname'] = info.sname
        uinfo['lname'] = info.lname
        uinfo['tg_user_id'] = info.tg_user_id
        uinfo['role'] = info.role
        uinfo['tt_code'] = info.tt_code
        uinfo['team'] = info.team
        uinfo['status'] = info.status
    session.close()
    return uinfo


async def add_check_in(cid, ph_url, lat, long):
    info = await get_info(cid)
    session = Session()
    q = CheckIn(tg_user_id=info['tg_user_id'], tt_code=info['tt_code'], photo=ph_url, geo_lat=lat, geo_long=long)
    session.add(q)
    session.commit()
    session.close()
    return 'ok'


async def add_check_out(cid, ph_url, lat, long):
    info = await get_info(cid)
    session = Session()
    id = await get_id(cid)
    for data_check in session.query(CheckIn).filter(CheckIn.tg_user_id == id):
        lastdata = data_check.created_at
    q = CheckOut(tg_user_id=info['tg_user_id'], tt_code=info['tt_code'], photo=ph_url, geo_lat=lat, geo_long=long)
    session.add(q)
    session.commit()
    session.close()
    return lastdata


async def add_sales(cid, pics, sales):
    info = await get_info(cid)
    session = Session()
    q = SalesReport(tg_user_id=info['tg_user_id'], team=info['team'], tt_code=info['tt_code'], pics=pics, sellout=sales)
    session.add(q)
    session.commit()
    session.close()


async def sale_date(id):
    s = ""
    session = Session()
    for sale in session.query(SalesReport).filter(SalesReport.tg_user_id == id):
        s = sale
        s = s.created_at
    if str(s)[:-15] == str(datetime.utcnow())[:-15]:
        return True
    else:
        return False
    session.close


async def check_in_today(id):
    i = ''
    session = Session()
    for info in session.query(CheckIn).filter(CheckIn.tg_user_id == id):
        i = info
        i = i.created_at
    if str(i)[:-15] == str(datetime.utcnow())[:-15]:
        return True
    else:
        return False
    session.close


async def get_role(cid):
    session = Session()
    query = session.query(UserProffile, Role, Users).join(Role, Role.id == UserProffile.role).join(
        Users, Users.id == UserProffile.tg_user_id).filter(Users.tg_user_id == cid).all()
    for b, c, d in query:
        role_name = c.role_name
    session.close()
    return role_name
