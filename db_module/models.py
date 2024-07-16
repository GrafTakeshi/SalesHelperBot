import sqlalchemy as sc
from datetime import datetime
from sqlalchemy.orm import relationship, as_declarative
from sqlalchemy import create_engine
DSN = "postgresql://postgres:postgres@localhost:5432/postgres"
engine = create_engine(DSN, echo=True)


@as_declarative()
class SimpleBase:
    id = sc.Column(sc.Integer, autoincrement=True, primary_key=True)


class Users(SimpleBase):
    __tablename__ = "users"

    tg_user_id = sc.Column(sc.BIGINT, unique=True, nullable=False)



class UserProffile(SimpleBase):
    __tablename__ = "userprofile"

    tg_user_id = sc.Column(sc.Integer, sc.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = sc.Column(sc.String(length=80), unique=False, nullable=False)
    sname = sc.Column(sc.String(length=80), unique=False, nullable=False)
    lname = sc.Column(sc.String(length=80), unique=False, nullable=False)
    team = sc.Column(sc.Integer, sc.ForeignKey("team.id", ondelete="CASCADE"))
    role = sc.Column(sc.Integer, sc.ForeignKey("role.id", ondelete="CASCADE"), nullable=False)
    tt_code = sc.Column(sc.Integer, sc.ForeignKey("tt_code.id", ondelete="CASCADE"))
    status = sc.Column(sc.BOOLEAN, unique=False, default=False)

    children = relationship("Users", cascade="all,delete", backref="profile")



class Role(SimpleBase):
    __tablename__ = "role"

    role_name = sc.Column(sc.String(length=80), unique=True)

class Team(SimpleBase):
    __tablename__ = "team"
    team_name = sc.Column(sc.String(length=80), unique=True)
    sv_id = sc.Column(sc.Integer, sc.ForeignKey("users.id", ondelete="CASCADE"))


class TT(SimpleBase):
    __tablename__ = "tt_code"

    codename = sc.Column(sc.String(length=5))


class CheckIn(SimpleBase):
    __tablename__ = "check_in"

    created_at = sc.Column(sc.DateTime, default=datetime.utcnow)
    tg_user_id = sc.Column(sc.Integer, sc.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tt_code = sc.Column(sc.Integer, sc.ForeignKey("tt_code.id", ondelete="CASCADE"), nullable=False)
    photo = sc.Column(sc.String(length=256), unique=True)
    geo_lat = sc.Column(sc.FLOAT())
    geo_long = sc.Column(sc.FLOAT())


class CheckOut(SimpleBase):
    __tablename__ = "check_out"

    created_at = sc.Column(sc.DateTime, default=datetime.utcnow)
    tg_user_id = sc.Column(sc.Integer, sc.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tt_code = sc.Column(sc.Integer, sc.ForeignKey("tt_code.id", ondelete="CASCADE"), nullable=False)
    photo = sc.Column(sc.String(length=256), unique=True)
    geo_lat = sc.Column(sc.FLOAT())
    geo_long = sc.Column(sc.FLOAT())

class SalesReport(SimpleBase):
    __tablename__ = "sales_reports"

    created_at = sc.Column(sc.DateTime, default=datetime.utcnow)
    tg_user_id = sc.Column(sc.Integer, sc.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tt_code = sc.Column(sc.Integer, sc.ForeignKey("tt_code.id", ondelete="CASCADE"), nullable=False)
    team = sc.Column(sc.Integer, sc.ForeignKey("team.id", ondelete="CASCADE"))
    pics = sc.Column(sc.Integer, nullable=False)
    sellout = sc.Column(sc.BIGINT, nullable=False)

#
def create_tables(engine):
    SimpleBase.metadata.create_all(engine)

create_tables(engine)