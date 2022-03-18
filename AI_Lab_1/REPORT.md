# Отчет по лабораторной работе
## по курсу "Искусственый интеллект"

### Студенты:

| ФИО       | Роль в проекте                                                                                   | Оценка       |
|-----------|--------------------------------------------------------------------------------------------------|--------------|
| Волков Матвей  | Эксперт в области пдд, написал тестирующий модуль работы ЭС                                      |          |
| Ляшун Дмитрий | Проектирование экспертной системы по действиям на перекрестке, реализация кода, написание отчета |       |
| Бирюков Виктор | Визуализация базы знаний, реализация экспертной системы для сценария пешеходного перехода, написание отчета        |      |
| Воронов Кирилл | Реализация действий экспертной системы по данным навигатора, написание отчёта                    |          |
| Инютин Максим | Реализация экспертной системы для случаев с регулировщиком, дополнение случаев с перекрёстком, отладка модуля с перекрёстком, написание отчёта | |

## Результат проверки

| Преподаватель     | Дата         |  Оценка       |
|-------------------|--------------|---------------|
| Сошников Д.В. |              |               |

> *Комментарии проверяющих (обратите внимание, что более подробные комментарии возможны непосредственно в репозитории по тексту программы)*

## Тема работы

Автопилот - программа получает информацию о ситуации на дороге и выдает рекомендации действий в соответствии с правилами дорожного движения.

## Концептуализация предметной области

Опишите результаты концептуализации предметной области:
 - Выделенные понятия: дорожные события (транспортные средства, ограничения, окружение), характеристики ТС, маневры
 - Тип получившейся онтологии - иерархия
 - Cтатические знания предметной области: дорожная ситуация (знаки на дороге, наличие/отсутствие светофора, ...), характеристики автомобиля  и т. д.
 - Динамические знания предметной области: правила дорожного движения

Онтология:
![Онтология](img/ontology.jpg)

Пример части экспертной системы (дорожная ситуация - перекресток):
![Перекресток](img/sample.jpg)

## Принцип реализации системы

Для реалистичной симуляции ситуаций для нашего автопилота, был сконструирован генератор оных. Он был реализован следующим образом:
Есть некоторое разветвление на различные глобальные ситуации (такие как перекресток и контроль движения за навигатором).
Далее рандомайзер выбирает одну из нескольких глобальных ситуаций. 
Далее, как по дереву, идет примерно таким же образом выборка возможных ситуаций. Из-за того, что наши схемы реализованы так, что
факты никак друг с другом не конфликтуют, было принято решение не создавать подробное дерево ситуаций, и наваливать неконфликтующие 
по схеме факты в одну кучу. (Таким образом получаются достаточно веселые ситуации :) ). 


Описанный выше генератор реализовывался в классе `Generator` в файле `internal/tickerGenerator`. В конструкторе класса заданы списки всех
возможных фактов, объединенные так, чтобы генератор мог наипростейшим образом составить различные ситуации, не выбирая факты, которые
могли бы конфликтовать друг с другом.


Также генератор использует классы `Navigator`, `CrossroadPassage` и `Crosswalk` для того, чтобы тут же можно было бы дать ответ на сгенерированные факты.
Сначала планировалось сделать метод запуска генерации асинхронным, чтобы потом через какой-нибудь стрим транслировать главной программе
наши ситуации, но от этой идеи отказались в пользу более простой.

Метод, запускающий генерацию ситуаций:

```python
    def start(self):
        while True:
            event_get = rand.randint(0, len(self.events)-1)
            facts = []

            for item in self.events[event_get][1]:
                facts.append(item[rand.randint(0, len(item) - 1)])

            print(facts)

            self.events[event_get][0].reset()
            self.events[event_get][0].factz(facts)
            print('--')
            self.events[event_get][0].run()
            print('--')
            sleep(TICKER)
```


## Механизм вывода

В нашей работе используется только прямой механизм вывода, поскольку из имеющегося набора фактов (информации о дорожной ситуации) необходимо перейти к заключениям – действиям водителя.  
В библиотеки pyknow механизм вывода строится на основе сформированного экземпляра класса, являющегося подклассом для KnowledgeEngine, хранящего базу знаний – набор условий для вывода новых фактов. В него добавляется набор известных фактов – информации о дорожной ситуации, далее запускается процесс вывода который сообщает о наборе действий, которые необходимо предпринять водителю.  
В качестве примера можно привести реализацию базы знаний для проезда по перекрестку:

```python
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
```

## Извлечение знаний и база знаний

Первоначальное извлечение знаний осуществлялось в формат схем. Участники, более знакомые с предметной областью, консультировали менее знакомых. Пример такой схемы представлен в первом пункте отчета. Составление правил для базы знаний происходило непосредственно со схем. В процессе переноса, а также последующей отладки, схемы неоднократно менялись.

Полное дерево И-ИЛИ, иллюстрирующее связи между всеми фактами ([прямая ссылка](https://github.com/MAILabs-AI-2022/ai_expertsystem-catenjoyersai/raw/main/img/scheme.png)):

![scheme](img/scheme.png)

## Протокол работы системы

Для демонстрации работы системы используется генератор тестов.

Перекрёстки:
```
[Fact(regulator='Да'), Fact(regulator_direction='Вправо'), Fact(traffic_lights='Нет'), Fact(light='Мигающий жёлтый'), Fact(light_type='Стрелка влево'), Fact(prior_signs='Да'), Fact(prior_sign='Главная дорога'), Fact(my_road='Асфальт'), Fact(car_type='Мотоцикл')]
--
Остановиться и ждать
--
[Fact(regulator='Да'), Fact(regulator_direction='На нас'), Fact(traffic_lights='Да'), Fact(light='Зелёный'), Fact(light_type='Нет стрелки'), Fact(prior_signs='Да'), Fact(prior_sign='Преимущество встречного движения'), Fact(my_road='Щебёнка'), Fact(car_type='Велосипед')]
--
Повернуть направо, иначе остановиться и ждать
--
[Fact(regulator='Да'), Fact(regulator_direction='Влево'), Fact(traffic_lights='Да'), Fact(light='Мигающий жёлтый'), Fact(light_type='Стрелка вправо'), Fact(prior_signs='Нет'), Fact(prior_sign='Преимущество встречного движения'), Fact(my_road='Щебёнка'), Fact(car_type='Автомобиль')]
--
Можно ехать
--
[Fact(regulator='Нет'), Fact(regulator_direction='Вправо'), Fact(traffic_lights='Да'), Fact(light='Зелёный'), Fact(light_type='Нет стрелки'), Fact(prior_signs='Да'), Fact(prior_sign='Преимущество встречного движения'), Fact(my_road='Грязь'), Fact(car_type='Мотоцикл')]
--
Можно ехать
--
[Fact(regulator='Нет'), Fact(regulator_direction='От нас'), Fact(traffic_lights='Да'), Fact(light='Нет'), Fact(light_type='Нет стрелки'), Fact(prior_signs='Нет'), Fact(prior_sign='Главная дорога'), Fact(my_road='Бетон'), Fact(car_type='Трамвай')]
--
Можно ехать
--
```

Навигатор:
```
[Fact(navigator_direction='Назад'), Fact(forbidden_sign='Да'), Fact(ban_on_turning='Да'), Fact(one_way_traffic='Нет'), Fact(stop_15_meters='Да')]
--
Развернуться на ближайшем перекрёстке
--
[Fact(navigator_direction='Нет'), Fact(forbidden_sign='Нет'), Fact(ban_on_turning='Да'), Fact(one_way_traffic='Нет'), Fact(stop_15_meters='Да')]
--
Мы доехали
--
```

Пешеходный переход:
```
[Fact('Пешеходный переход'), Fact(pedestrians='Да')]
--
Притормозить
Остановиться и дождаться, пока пешеход пройдет
--
[Fact('Пешеходный переход'), Fact(pedestrians='Нет')]
--
Притормозить
Ехать дальше без изменения скорости
```

## Выводы

Выполнив данную лабораторную работу, мы получили интересный опыт в работе в команде. Всё началось с выбора темы, рассматривалось очень много вариантов, например, анализатор ошибок на атомной электростанции (этот вариант откинули из-за сложности самой области), рекомендации автомобилей, комплектующих компьютера и многое другое. Но решили остановаться на достаточно интересной, и, как нам показалось, актуальной теме - автопилот. Предполагалось, что  информация, которую анализирует наша система, может поступать, например, с помощью компьютерного зрения. И в итоге наш искусственный интеллект выдаёт рекомендации водителю как поступать, не нарушая правила дорожного движения. Были даже идеи, что экспертная система полностью возьмёт под контроль движение машины, но для этого нужно гараздо больше данных, и работа окажется намного сложнее. Следующая трудность, с которой мы столкнулись - составление плана действий и распределение деятельности. Тут у нас происходило всё как-то хаотично: решения приходили и принимались спантанно, по мере изучения документации для pyknow. Но всё-таки получилась некая полная картина. С поставленной задачей мы справились. После того, как каждый понял, что надо делать, проблем не возникало и результат был достигнут. Данная работа научила нас создавать экспертные системы, работать в команде, а также находить оригинальные выходы из разных ситуаций.
