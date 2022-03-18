from pyknow import *

YES = 'Да'
NO = 'Нет'
FOLLOW_TRAFFIC_LIGHTS = 'Следовать сигналам светофора'
MAIN_ROAD = 'Мы на главной дороге'
NOT_MAIN_ROAD = 'Мы на второстепенной дороге'
CHECK_RIGHT = 'Воспользоваться правилом \"помеха справа\"'
ACTION_GO = 'Можно ехать'
ACTION_GO_LEFT = 'Повернуть налево, иначе остановиться и ждать'
ACTION_GO_RIGHT = 'Повернуть направо, иначе остановиться и ждать'
ACTION_STOP = 'Остановиться и ждать'
ACTION_CHECK_AND_GO = 'Уступить дорогу, если есть другие ТС, иначе можно ехать'

class CrossroadPassage(KnowledgeEngine):
    
    #@DefFacts()
    #def _initial_action(self):
    #    yield Fact(action='greet')
    
    # Если палка смотрит влево, проезжай как королева
    @Rule(AND(Fact(regulator = YES),
              Fact(regulator_direction = 'Влево')))
    def regulator_action_l(self):
        self.declare(Fact(final_action = ACTION_GO))
    
    # Если палка смотрит вправо, ехать не имеешь права
    @Rule(AND(Fact(regulator = YES),
              Fact(regulator_direction = 'Вправо')))
    def regulator_action_r(self):
        self.declare(Fact(final_action = ACTION_STOP))
    
    # Если палка смотрит в рот, делай правый поворот
    @Rule(AND(Fact(regulator = YES),
              Fact(regulator_direction = 'На нас')))
    def regulator_action_o(self):
        self.declare(Fact(final_action = ACTION_GO_RIGHT))
   
    # Если мент стоит спиной, то не рыпайся и стой
    @Rule(AND(Fact(regulator = YES),
              Fact(regulator_direction = 'От нас')))
    def regulator_action_a(self):
        self.declare(Fact(final_action = ACTION_STOP))

    @Rule(AND(Fact(traffic_lights = YES),
              Fact(regulator = NO)))
    def traf_lights_check(self):
        self.declare(Fact(action = FOLLOW_TRAFFIC_LIGHTS))
        
    @Rule(AND(Fact(action = FOLLOW_TRAFFIC_LIGHTS),
              Fact(light = 'Красный')))
    def traf_lights_action_stop(self):
        self.declare(Fact(final_action = ACTION_STOP))
    
    @Rule(AND(Fact(action = FOLLOW_TRAFFIC_LIGHTS),
              Fact(light = 'Зелёный'),
              Fact(light_type = 'Стрелка влево')))
    def traf_lights_action_left(self):
        self.declare(Fact(final_action = ACTION_GO_LEFT))
    
    @Rule(AND(Fact(action = FOLLOW_TRAFFIC_LIGHTS),
              Fact(light = 'Зелёный'),
              Fact(light_type = 'Стрелка вправо')))
    def traf_lights_action_right(self):
        self.declare(Fact(final_action = ACTION_GO_RIGHT))
    
    @Rule(AND(Fact(action = FOLLOW_TRAFFIC_LIGHTS),
              Fact(light = 'Зелёный'),
              NOT(OR(Fact(light_type = 'Стрелка влево'),
                     Fact(light_type = 'Стрелка вправо')))))
    def traf_lights_action_go(self):
        self.declare(Fact(final_action = ACTION_GO))
    
    @Rule(OR(AND(Fact(traffic_lights = NO),
                 Fact(regulator = NO)),
             AND(Fact(action = FOLLOW_TRAFFIC_LIGHTS),
              OR(Fact(light = 'Мигающий жёлтый'),
                 Fact(light = NO))  )))
    def check_prior_signs(self):
        self.declare(Fact(action = 'Проверить знаки приоритета'))
    
    @Rule(AND(Fact(action = 'Проверить знаки приоритета'),
              Fact(prior_signs = YES)))
    def prior_signs_action(self):
        self.declare(Fact(action = 'Следовать знакам приоритета'))
    
    @Rule(AND(Fact(action = 'Следовать знакам приоритета'),
              Fact(prior_sign = 'Главная дорога')))
    def prior_signs_action1(self):
        self.declare(Fact(action = MAIN_ROAD))
    
    @Rule(AND(Fact(action = 'Следовать знакам приоритета'),
              Fact(prior_sign = 'Уступи дорогу')))
    def prior_signs_action2(self):
        self.declare(Fact(action = NOT_MAIN_ROAD))
    
    @Rule(AND(Fact(action = 'Следовать знакам приоритета'),
              Fact(prior_sign = 'Преимущество перед встречным движением')))
    def prior_signs_action3(self):
        self.declare(Fact(action = MAIN_ROAD))
    
    @Rule(AND(Fact(action = 'Следовать знакам приоритета'),
              Fact(prior_sign = 'Преимущество встречного движения')))
    def prior_signs_action4(self):
        self.declare(Fact(action = NOT_MAIN_ROAD))
    
    @Rule(Fact(action = MAIN_ROAD))
    def prior_sign_main_road(self):
        self.declare(Fact(final_action = ACTION_GO))
    
    @Rule(Fact(action = NOT_MAIN_ROAD))
    def prior_sign_not_main_road(self):
        self.declare(Fact(final_action = ACTION_CHECK_AND_GO))
    
    @Rule(AND(Fact(action = 'Проверить знаки приоритета'),
              Fact(prior_signs = NO)))
    def check_road_type(self):
        self.declare(Fact(action = 'Проверить покрытие дороги'))

    @Rule(Fact(my_road = L('Асфальт') | L('Булыжник') | L('Бетон') | L('Щебёнка')))
    def determine_road_type(self):
        self.declare(Fact(road_type = 'Твёрдое покрытие'))
    
    @Rule(AND(Fact(action = 'Проверить покрытие дороги'), Fact(road_type = 'Твёрдое покрытие')))
    def final_check_road_main(self):
        self.declare(Fact(action = MAIN_ROAD))
    
    @Rule(AND(Fact(action = 'Проверить покрытие дороги'), NOT(Fact(road_type = 'Твёрдое покрытие'))))
    def final_check_road_not_main(self):
        self.declare(Fact(action = NOT_MAIN_ROAD))
    
    @Rule(Fact(spec_trans = YES))
    def spec_trans_action(self):
        self.declare(Fact(final_action = 'Уступить дорогу транспорту'))
    
    @Rule(AND(Fact(action = 'Проверить покрытие дороги'), Fact(my_road = W()), Fact(another_road = W()), ))
    def check_trans_type(self):
        self.declare(Fact(action = 'Проверить тип ТС'))
    
    @Rule(AND(Fact(action = 'Проверить тип ТС'), Fact(car_type = 'Трамвай')))
    def check_car_type(self):
        self.declare(Fact(action = MAIN_ROAD))

    @Rule(AND(Fact(action = 'Проверить тип ТС'), NOT(Fact(car_type ='Трамвай'))))
    def use_inter_on_right(self):
        self.declare(Fact(action = CHECK_RIGHT))

    @Rule(AND(Fact(action = CHECK_RIGHT), Fact(inter_side = 'Справа')))
    def final_action3(self):
        self.declare(Fact(action = NOT_MAIN_ROAD))
    
    @Rule(AND(Fact(action = CHECK_RIGHT), Fact(inter_side = 'Слева')))
    def final_action4(self):
        self.declare(Fact(action = MAIN_ROAD))
    
    
    
    def factz(self,l):
        for x in l:
            self.declare(x)
    
    @Rule(Fact(final_action = MATCH.action), salience = 1)
    def what_to_do(self, action):
        print(action)