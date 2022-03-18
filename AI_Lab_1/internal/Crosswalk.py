from pyknow import *


class Crosswalk(KnowledgeEngine):    
    @Rule(Fact(action = "Проверить наличие пешеходов"), Fact(pedestrians = "Да"))
    def wait_for_pedestrian(self):
        self.declare(Fact(final_action = "Остановиться и дождаться, пока пешеход пройдет"))
        
    @Rule(Fact(action = "Проверить наличие пешеходов"), NOT(Fact(pedestrians = "Да")))
    def no_pedestrian(self):
        self.declare(Fact(final_action = "Ехать дальше без изменения скорости"))
        
    @Rule(Fact("Пешеходный переход"))
    def crosswalk(self):        
        self.declare(Fact(final_action = "Притормозить"))
        self.declare(Fact(action = "Проверить наличие пешеходов"))
    
    @Rule(Fact(final_action = MATCH.action), salience=1)
    def what_to_do(self, action):
        print(action)

    def factz(self,l):
        for x in l:
            self.declare(x)