from operator import and_

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DSN
import datetime
from db_module.models import Users, UserProffile, Role, Team, TT, CheckIn, CheckOut, create_tables, SalesReport
from aiogram.types import Message, input_text_message_content
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from states import Welcome, RegisterNewUser, ChekInn, ChekOutt
from keyboards.keybords import y_n_kb, start_kb, work_day_kb, end_day_kb
from db_module.db_func import get_info

# cid = 5783086540

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)



async def get_team(cid, status):
    workers = ''
    i = 0
    team = await get_info(cid)
    team = team.get('team')
    session = Session()
    query = session.query(UserProffile, TT).join(TT, TT.id == UserProffile.tt_code).filter(and_(UserProffile.team == team, UserProffile.role == 3))
    for promo, tt in query:
        i += 1
        if promo.status == status:
            temp = f'{i} id-{promo.id} {tt.codename} {promo.sname} {promo.name} \n'
            workers = workers + temp
    return workers

async def get_ids(cid, status):
    workers = []
    i = 0
    team = await get_info(cid)
    team = team.get('team')
    session = Session()
    query = session.query(UserProffile).filter(and_(UserProffile.team == team, UserProffile.role == 3))
    for promo in query:
        i += 1
        if promo.status == status:
            temp = int(promo.id)
            workers.append(temp)
    return workers

async def get_info_id(id):
    session = Session()
    for ID in session.query(Users.tg_user_id).filter_by(id=id):
        tg_id = ID[0]
    return tg_id


async def get_tt_list():
    tt_list = []
    session = Session()
    for ID in session.query(TT.codename).all():
        a = ID[0]
        tt_list.append(a)
    return tt_list

async def activate(tt_code, id):
    session = Session()
    for ID in session.query(TT.id).filter(TT.codename == tt_code):
        tt_id = ID[0]
    query = session.query(UserProffile).filter(UserProffile.id == id)
    for i in query:
        i.status = True
        i.tt_code = tt_id
        session.commit()
    return

async def deactivate(id):
    session = Session()
    query = session.query(UserProffile).filter(UserProffile.id == id)
    for i in query:
        i.status = False
        i.tt_code = 1
        session.commit()
        result = f'Сотрудник {i.sname} {i.name} успешно деактивирован'
    return result

async def get_sale_day(team):
    response = ''
    pic = 0
    sell = 0
    session = Session()
    for sale, store in session.query(SalesReport, TT).join(TT, TT.id == SalesReport.tt_code).filter(and_(SalesReport.team == team, SalesReport.created_at >= (str(datetime.utcnow())[:-16]))):
        string = f'{store.codename} Продал {sale.pics} штук на сумму {sale.sellout} руб \n'
        response += string
        pic += sale.pics
        sell += sale.sellout
    response = response + f'Всего за {datetime.utcnow()}'[:-16] + f'продано: \n {pic} шт на сумму {sell} руб.'
    session.close()
    return response

async def get_sale_petiod(team, period):
    print(period)
    start_day = datetime.datetime.utcnow() - period
    print(start_day)
    response = []
    stores = []
    pic = 0
    sell = 0
    session = Session()
    query = session.query(SalesReport, TT)\
        .join(TT, TT.id == SalesReport.tt_code)\
        .filter(and_(SalesReport.team == team, SalesReport.created_at.between(str(start_day)
                                                                              , str(datetime.datetime.utcnow()))))
    for sale, store in query:
        temp = []
        result = ''
        stores.append(store.codename)
        temp.append(store.codename)
        temp.append(sale.pics)
        temp.append(sale.sellout)
        response.append(temp)
    temp_pics = 0
    temp_sell = 0
    total_pics = 0
    total_sale = 0
    for a in list(set(stores)):
        temp_tt = a
        for b in response:
            if a == b[0]:
                temp_pics = temp_pics + b[1]
                temp_sell = temp_sell + b[2]
        string = f'{temp_tt} Продал {temp_pics} штук на сумму {temp_sell} руб \n'
        total_pics += temp_pics
        total_sale += temp_sell
        result += string
        pic += sale.pics
        sell += sale.sellout
    result = result + f'Всего продано: \n {total_pics} шт на сумму {total_sale} руб.'
    session.close()
    return result


async def get_sv_id(team):
    session = Session()
    query = session.query(UserProffile, Role, Users).join(Role, Role.id == UserProffile.role).join(
        Users, Users.id == UserProffile.tg_user_id).filter(and_(UserProffile.team == team, UserProffile.role == 2))
    for b, c, d in query:
        sv_id = d.tg_user_id
    session.close()
    return sv_id