import asyncio
from operator import and_
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DSN
from db_module.models import Users, UserProffile, Role, Team, TT, CheckIn, CheckOut, create_tables, SalesReport
from db_module.db_func import get_info

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)

cid = 5118763357
id = 7
tt_code = 'A197'
# cid = 5783086540
team = 1
priod = datetime.datetime.today().weekday()

async def get_role(team):
    session = Session()
    query = session.query(UserProffile, Role, Users).join(Role, Role.id == UserProffile.role).join(
        Users, Users.id == UserProffile.tg_user_id).filter(and_(UserProffile.team == team, UserProffile.role == 2))
    for b, c, d in query:
        role_name = d.tg_user_id
    session.close()
    print(role_name)
    return role_name

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

asyncio.run(get_role(team))
inf = asyncio.run(get_info(cid))
print(type(inf['team']))



#
# async def get_role(id):
#     session = Session()
#     query = session.query(Users).filter_by(id=id).delete()
#
#     session.commit()
#     session.close()
#     return
#
#
# asyncio.run(get_role(id))