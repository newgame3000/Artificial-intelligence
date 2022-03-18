import re
import inspect
from pyknow import conditionalelement
from Navigator import Navigator
from CrossroadPassage import CrossroadPassage
from Crosswalk import Crosswalk

declaration_re = re.compile(r"(?<=self\.declare\(Fact\().*?(?=\)\)\n)")
constants = [
    ('FOLLOW_TRAFFIC_LIGHTS', '\'Следовать сигналам светофора\''),
    ('NOT_MAIN_ROAD', '\'Мы на второстепенной дороге\''),
    ('MAIN_ROAD', '\'Мы на главной дороге\''),
    ('CHECK_RIGHT', '\'Воспользоваться правилом \"помеха справа\"\''),
    ('ACTION_GO_LEFT', '\'Повернуть налево, иначе остановиться и ждать\''),
    ('ACTION_GO_RIGHT', '\'Повернуть направо, иначе остановиться и ждать\''),
    ('ACTION_GO', '\'Можно ехать\''),
    ('ACTION_STOP', '\'Остановиться и ждать\''),
    ('ACTION_CHECK_AND_GO', '\'Уступить дорогу, если есть другие ТС, иначе можно ехать\''),
    ('ACTION_TURN_AROUND', '\'Развернуться\''),
    ('ACTION_CONTINUE_DRIVING_STRAIGHT', '\'Продолжать движение вперёд по правилам\''),
    ('ACTION_CONTINUE_DRIVING_CROSSROAD', '\'Следуем правилам проезда на перекрёстке\''),
    ('ACTION_END', '\'Мы доехали\''),
    ('ACTION_STRAIGHT_CROSSROAD_TURN', '\'Ехать до ближайшего перекрёстка и повернуть в направлении пункта назначения\''),
    ('ACTION_CROSSROAD_TURN', '\'Развернуться на ближайшем перекрёстке\''),
    ('YES', '\'Да\''),
    ('NO', '\'Нет\'')
]


def replace_constants(s):
    for (key, value) in constants:
        s = s.replace(key, value)
    return s


def ke2dot(engine):
    '''Генератор схемы связей между фактами и правилами'''
    
    def gen_node(name, label, shape):
        return "\t\"{}\" [label=\"{}\", shape={}]\n".format(name, label, shape)

    def gen_edge(name1, name2):
        return "\t\"{}\" -> \"{}\"\n".format(name1, name2)
    
    def get_id(name):
        nonlocal facts
        nonlocal id_
        
        res = facts.get(name)
        if res is None:
            facts[name] = id_
            id_ += 1
            return str(name), True
        return str(name), False

    def iterate_over_tree(node: tuple, node_id: str):
        nonlocal result
        nonlocal id_

        for child in node:
            node_type = str(type(child)).rsplit('.', 1)[-1][:-2]
            if node_type == 'Fact':
                fact = str(child).rsplit("Fact", 1)[-1][1:-1].replace('"', "'")
                child_id, is_new = get_id(fact)
                if is_new:
                    result += gen_node(child_id, fact, "rectangle")
                result += gen_edge(child_id, node_id)
            else:
                child_id = str(id_)
                id_ += 1
                result += gen_node(child_id, node_type, "circle")
                result += gen_edge(child_id, node_id)
                iterate_over_tree(child, child_id)

    result = "digraph KnowledgeEngine {\n\tgraph [splines=spline]\n"
    facts = dict()
    id_ = 0

    for rule in engine.get_rules():
        top_node = ""
        if len(rule) > 1:
            top_node = str(id_)
            id_ += 1
            result += gen_node(top_node, "AND", "circle")
            iterate_over_tree(conditionalelement.AND(*rule), top_node)
        else:
            node_type = str(type(rule[0])).rsplit('.', 1)[-1][:-2]
            if node_type == "Fact":
                fact = str(rule[0]).rsplit("Fact", 1)[-1][1:-1].replace('"', "'")
                top_node, is_new = get_id(fact)
                if is_new: 
                    result += gen_node(top_node, fact, "rectangle")
            else:
                top_node = str(id_)
                id_ += 1
                result += gen_node(top_node, node_type, "circle")
                iterate_over_tree(rule[0], top_node)

        funcname = rule._wrapped.__name__
        result += gen_node(funcname, funcname, "parallelogram")
        result += gen_edge(top_node, funcname)

        declarations = declaration_re.findall(inspect.getsource(rule._wrapped))
        for declaration in map(replace_constants, declarations):
            declaration = declaration.replace('"', "'").replace(" = ", "=")
            node_id, is_new = get_id(declaration)
            if is_new: 
                result += gen_node(node_id, declaration, "rectangle")
            result += gen_edge(funcname, node_id)

    result += "}\n"
    return result


class Engine(Crosswalk, Navigator, CrossroadPassage):
    pass


engine = Engine()
print(ke2dot(engine))
