import unittest
from dataclasses import dataclass
from can_share import *

test_cases = ['condition_1', 'condition_2', 'condition_3_1', 'condition_3_2', 'condition_4_1', 'condition_4_2',
              'example1-tg-bridge', 'example2-big-fig', 'example3-complex-graph']

test_graphs = dict[str, nx.MultiDiGraph]()


def set_up(names: list[str]):
    for name in names:
        g, _, _ = read_graph(f'./test/{name}.json')
        test_graphs[name] = g


def print_test_graphs(names: list[str]):
    for name in names:
        g, nodes_to_labels, edges_to_labels = read_graph(f'./test/{name}.json')
        print_graph(g, f'./view/{name}_view', nodes_to_labels, edges_to_labels)


set_up(names=test_cases)


class TestCondition1(unittest.TestCase):
    def test_condition_1(self):
        @dataclass
        class TestCase:
            x: str
            y: str
            a: str
            expected: bool

        graph = test_graphs['condition_1']
        testcases = [
            TestCase(x='1', y='2', a='A', expected=True),
            TestCase(x='1', y='3', a='A', expected=False),
            TestCase(x='1', y='4', a='A', expected=False),
            TestCase(x='1', y='6', a='A', expected=True),
            TestCase(x='1', y='5', a='A', expected=False),
        ]

        for case in testcases:
            actual = x_y_a_edge_exist(graph, case.a, case.x, case.y)
            self.assertEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestCondition2(unittest.TestCase):
    def test_condition_2(self):
        @dataclass
        class TestCase:
            a: str
            y: str
            expected: set[str]

        graph = test_graphs['condition_2']
        testcases = [
            TestCase(y='2', a='A', expected={'1'}),
            TestCase(y='7', a='A', expected=set()),
            TestCase(y='6', a='B', expected={'2'}),
            TestCase(y='6', a='A', expected={'5'}),
            TestCase(y='3', a='B', expected=set()),
        ]

        for case in testcases:
            actual = s_y_a_nodes(graph, case.a, case.y)
            self.assertSetEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestCondition3_1(unittest.TestCase):
    def test_condition_3_1(self):
        @dataclass
        class TestCase:
            x: str
            expected: set[str]

        graph = test_graphs['condition_3_1']
        testcases = [
            TestCase(x='2', expected={'1'}),
            TestCase(x='4', expected=set()),
            TestCase(x='6', expected=set()),
            TestCase(x='10', expected=set()),
            TestCase(x='14', expected={'11'}),
            TestCase(x='19', expected=set()),
            TestCase(x='24', expected={'23'}),
            TestCase(x='26', expected=set()),
            TestCase(x='29', expected={'28'}),
            TestCase(x='30', expected={'30'}),
            TestCase(x='35', expected={'33', '31'}),
        ]

        for case in testcases:
            actual = initially_spans(graph, case.x)
            self.assertSetEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestCondition3_2(unittest.TestCase):
    def test_condition_3_2(self):
        @dataclass
        class TestCase:
            s_ids: set[str]
            expected: set[str]

        graph = test_graphs['condition_3_2']
        testcases = [
            TestCase(s_ids={'1'}, expected={'3', '4', '5', '6', '8', '9'}),
            TestCase(s_ids={'12'}, expected={
                     '3', '4',  '5', '6', '8', '9', '12'}),
            TestCase(s_ids={'7', '11'}, expected={
                     '10', '6', '9', '8', '11', '7'}),
            TestCase(s_ids={'1', '7'}, expected={
                     '10', '6', '9', '8', '3', '4', '5', '7'}),
        ]

        for case in testcases:
            actual = terminally_spans(graph, case.s_ids)
            self.assertSetEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestCondition4_1(unittest.TestCase):
    def test_condition_4_1(self):
        @dataclass
        class TestCase:
            xi_si: tuple[str, str]
            expected: bool

        graph = test_graphs['condition_4_1']
        graph_view = graph.to_undirected(as_view=True)
        testcases = [
            TestCase(xi_si=('1', '4'), expected=True),
            TestCase(xi_si=('5', '6'), expected=True),
            TestCase(xi_si=('7', '9'), expected=True),
            TestCase(xi_si=('10', '13'), expected=False),
            TestCase(xi_si=('14', '15'), expected=True),
            TestCase(xi_si=('16', '18'), expected=False),
            TestCase(xi_si=('19', '21'), expected=True),
            TestCase(xi_si=('22', '26'), expected=True),
            TestCase(xi_si=('27', '30'), expected=False),
            TestCase(xi_si=('31', '34'), expected=False),
            TestCase(xi_si=('35', '39'), expected=True),
            TestCase(xi_si=('40', '44'), expected=True),
            TestCase(xi_si=('45', '49'), expected=False),
        ]

        for case in testcases:
            actual = island_bridge_paths_exist((graph, graph_view, case.xi_si))
            self.assertEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestCondition4_2(unittest.TestCase):
    def test_condition_4_2(self):
        @dataclass
        class TestCase:
            xi_si: tuple[str, str]
            expected: bool

        graph = test_graphs['condition_4_2']
        graph_view = graph.to_undirected(as_view=True)
        testcases = [
            TestCase(xi_si=('1', '4'), expected=True),
            TestCase(xi_si=('5', '7'), expected=True),
            TestCase(xi_si=('8', '11'), expected=True),
            TestCase(xi_si=('12', '18'), expected=True),
        ]

        for case in testcases:
            actual = island_bridge_paths_exist((graph, graph_view, case.xi_si))
            self.assertEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )


class TestArticlesExamples(unittest.TestCase):
    def test_examples(self):
        @dataclass
        class TestCase:
            graph_name: str
            a: str
            x: str
            y: str
            expected: bool

        testcases = [
            TestCase(graph_name='example1-tg-bridge', a='READ', x='5ddcccfd-ece6-4d32-85d1-3c86dbf69808',
                     y='cffe89b6-6399-470e-b8d8-87bc32628cc3', expected=True),
            TestCase(graph_name='example2-big-fig', a='READ', x='275ba42d-f079-4550-8de3-00b8fb5f2055',
                     y='4ffe40e8-6bc1-4ddf-89d1-8682dcdd2372', expected=True),
            TestCase(graph_name='example3-complex-graph',
                     a='A', x='1', y='8', expected=True),
        ]

        for case in testcases:
            graph = test_graphs[case.graph_name]
            actual = can_share(graph, case.a, case.x, case.y)
            self.assertEqual(
                case.expected,
                actual,
                "failed test {} expected {}, actual {}".format(
                    case, case.expected, actual
                ),
            )
