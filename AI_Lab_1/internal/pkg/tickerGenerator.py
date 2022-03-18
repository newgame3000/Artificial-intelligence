import random as rand
import Navigator as Nav
import CrossroadPassage as CrPass

TICKER = 1


class Generator(Nav, CrPass):
    def __init__(self):
        self.nav = Nav.Navigator()
        self.crPass = CrPass.CrossroadPassage()

        self.events = [self.nav, self.crPass]

        # ----Navigator-----------
        self.dirraction = ['Нет', 'Прямо', 'Направо', 'Налево', 'Назад']

        # ----CrossroadPassage----
        self.regulator = [False, False, False, False, 'Влево', 'Вправо', 'На нас', 'От нас']

        # ивенты светофора
        self.trafficLight = [False, 'Красный', 'Зеленый', 'Мигающий жёлтый']
        self.arrow = [False, 'Стрелка влево', 'Стрелка вправо']

        # знаки приоритета и правило "правой руки"
        self.prior_sign = [False, 'Уступи дорогу',
                           'Главная дорога',
                           'Преимущество встречного движения',
                           'Преимущество перед встречным движением']

        # тип дороги
        self.road_type = ['Асфальт', 'Булыжник', 'Бетон', 'Щебёнка', 'Вода', 'Грязь', 'Огород', 'Пшеница', 'Трава']

        # тип ТС
        self.car_type = ['Трамвай', 'Автомобиль', 'Мотоцикл', 'Велосипед', 'Автобус']

    async def start(self):
        while(True):
            event_get = rand.randint(0, 1)
