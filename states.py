from aiogram.filters.state import State, StatesGroup



class Welcome(StatesGroup):
    start = State()
    invite = State()
    workday = State()


class RegisterNewUser(StatesGroup):
    name = State()
    sname = State()
    lname = State()
    team = State()
    conform = State()


class ChekInn(StatesGroup):
    chek_in = State()
    get_location = State()
    get_photo = State()

class ChekOutt(StatesGroup):
    chek_out = State()
    get_location_out = State()
    get_photo = State()
    get_sales = State()

class SVDesk(StatesGroup):
    sv_choise = State()
    sv_choise_team = State()
    sv_choise_aktivate = State()
    sv_choise_aktivate_choise = State()
    sv_choise_fier = State()
    sv_choise_fier_choise = State()
    sv_choise_deaktivate = State()
    sv_choise_deaktivate_choise = State()
    sv_start = State()
    sv_sales = State()



