from pyknow import *

YES = 'Да'
NO = 'Нет'

ACTION_TURN_AROUND = 'Развернуться'
ACTION_CONTINUE_DRIVING_STRAIGHT = 'Продолжать движение вперёд по правилам'
ACTION_CONTINUE_DRIVING_CROSSROAD = 'Следуем правилам проезда на перекрёстке'
ACTION_END = 'Мы доехали'
ACTION_STRAIGHT_CROSSROAD_TURN = 'Ехать до ближайшего перекрёстка и повернуть в направлении пункта назначения'
ACTION_CROSSROAD_TURN = 'Развернуться на ближайшем перекрёстке'

class Navigator(KnowledgeEngine):
    def declare_facts(self, facts):
        for fact in facts:
            self.declare(fact)

    @Rule(AND(Fact(navigator_direction = 'Прямо'),
              Fact(forbidden_sign = NO)))
    def forbidden_false(self):
        self.declare(Fact(final_action = ACTION_CONTINUE_DRIVING_STRAIGHT))

    @Rule(OR(Fact(navigator_direction = 'Направо'),
             Fact(navigator_direction = 'Налево')))
    def navigator_direction_right_left(self):
        self.declare(Fact(final_action = ACTION_CONTINUE_DRIVING_CROSSROAD))

    @Rule(Fact(navigator_direction = NO))
    def navigator_turn_around_false(self):
        self.declare(Fact(final_action = ACTION_END))

    @Rule(AND(Fact(navigator_direction = 'Назад'), 
              Fact(ban_on_turning = YES),
              Fact(one_way_traffic = YES)))
    def all_right_turn(self):
        self.declare(Fact(final_action = ACTION_STRAIGHT_CROSSROAD_TURN))

    @Rule(OR(
          AND(Fact(navigator_direction = 'Назад'),
              Fact(ban_on_turning = YES),
              Fact(one_way_traffic = NO)),
          AND(Fact(navigator_direction = 'Назад'),
              Fact(ban_on_turning = NO),
              Fact(stop_15_meters = YES))))
    def crossroad_turn(self):
        self.declare(Fact(final_action = ACTION_CROSSROAD_TURN))

    @Rule(OR(
          AND(Fact(navigator_direction = 'Прямо'), 
              Fact(forbidden_sign = YES)),
          AND(Fact(navigator_direction = 'Назад'),
              Fact(ban_on_turning = NO),
              Fact(stop_15_meters = NO))))
    def turn_true(self):
        self.declare(Fact(final_action = ACTION_TURN_AROUND))

    def factz(self,l):
        for x in l:
            self.declare(x)

    @Rule(Fact(final_action = MATCH.action), salience = 1)
    def what_to_do(self, action):
        print(action)