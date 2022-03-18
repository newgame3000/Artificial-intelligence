import random as rand
import time

from Navigator import Navigator
from CrossroadPassage import CrossroadPassage
from pyknow import *
from time import *

TICKER = 1
YES = 'Да'
NO = 'Нет'


class Generator:
    def __init__(self):
        self.nav = Navigator()
        self.crPass = CrossroadPassage()

#-----------------------------сюды вставлять факты-------------------------------------
        # ----Navigator-----------
        nav_facts = [
            [Fact(navigator_direction='Нет'),
             Fact(navigator_direction='Прямо'),
             Fact(navigator_direction='Направо'),
             Fact(navigator_direction='Налево'),
             Fact(navigator_direction='Назад')],

            [Fact(forbidden_sign=NO),
             Fact(forbidden_sign=YES)],

            [Fact(ban_on_turning=YES),
             Fact(ban_on_turning=NO)],

            [Fact(one_way_traffic=YES),
             Fact(one_way_traffic=NO)],

            [Fact(stop_15_meters=YES),
             Fact(stop_15_meters=NO)]
        ]

        # ----CrossroadPassage----
        crPass_facts = [
            [Fact(regulator=YES),
             Fact(regulator=NO)],

            [Fact(regulator_direction='Влево'),
             Fact(regulator_direction='Вправо'),
             Fact(regulator_direction='На нас'),
             Fact(regulator_direction='От нас')],

            [Fact(traffic_lights=YES),
             Fact(traffic_lights=NO)],

            # ивенты светофора
            [Fact(light='Красный'),
             Fact(light='Зелёный'),
             Fact(light='Мигающий жёлтый'),
             Fact(light=NO)],

            [Fact(light_type='Нет стрелки'),
             Fact(light_type='Стрелка влево'),
             Fact(light_type='Стрелка вправо')],

            # знаки приоритета и правило "правой руки"
            [Fact(prior_sign='Главная дорога'),
             Fact(prior_sign='Уступи дорогу'),
             Fact(prior_sign='Преимущество перед встречным движением'),
             Fact(prior_sign='Преимущество встречного движения')],

            # тип дороги
            [Fact(my_road='Асфальт'),
             Fact(my_road='Булыжник'),
             Fact(my_road='Бетон'),
             Fact(my_road='Щебёнка'),
             Fact(my_road='Вода'),
             Fact(my_road='Грязь'),
             Fact(my_road='Огород'),
             Fact(my_road='Пшеница'),
             Fact(my_road='Трава')],

            [Fact(car_type='Трамвай'),
             Fact(car_type='Автомобиль'),
             Fact(car_type='Мотоцикл'),
             Fact(car_type='Велосипед'),
             Fact(car_type='Автобус')
             ]
        ]

        self.events = [[self.nav, nav_facts], [self.crPass, crPass_facts]]

    def start(self):
        while True:
            event_get = rand.randint(0, len(self.events)-1)
            facts = []

            for item in self.events[event_get][1]:
                facts.append(item[rand.randint(0, len(item) - 1)])

            print(facts)

            self.events[event_get][0].reset()
            sleep(TICKER)
            self.events[event_get][0].factz(facts)
            print('--')
            self.events[event_get][0].run()
            print('--')


gen = Generator()
gen.start()
