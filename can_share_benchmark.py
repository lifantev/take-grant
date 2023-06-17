from timeit import default_timer as timer
from dataclasses import dataclass
from can_share import *


@dataclass
class TestCase:
    n: int
    graph_name: str
    a: str
    x: str
    y: str


test_graphs = dict[str, nx.MultiDiGraph]()


def set_up(tcc: list[TestCase]):
    for tc in tcc:
        g, _, _ = read_graph(f'./test/{tc.graph_name}.json')
        test_graphs[tc.graph_name] = g


def benchmark_can_share(tc: TestCase):
    graph = test_graphs[tc.graph_name]

    start = timer()
    for _ in range(tc.n):
        res = can_share(graph, tc.a, tc.x, tc.y)
        assert (True == res)

    sum_time = timer() - start
    print(tc.graph_name,
          f'V+E={len(graph.nodes)}+{len(graph.edges)}={len(graph.nodes)+len(graph.edges)}',
          f'n={tc.n}',
          f'sum_time={sum_time}', f'avg_time={sum_time/tc.n}')


test_cases = [
    TestCase(n=100, graph_name='chain_3_example3-complex-graph',
             x='0_1', y='2_8', a='A'),
    TestCase(n=100, graph_name='chain_6_example3-complex-graph',
             x='0_1', y='5_8', a='A'),
    TestCase(n=100, graph_name='chain_12_example3-complex-graph',
             x='0_1', y='11_8', a='A'),
    TestCase(n=100, graph_name='chain_24_example3-complex-graph',
             x='0_1', y='23_8', a='A'),
    TestCase(n=100, graph_name='chain_48_example3-complex-graph',
             x='0_1', y='47_8', a='A'),
    TestCase(n=100, graph_name='chain_86_example3-complex-graph',
             x='0_1', y='85_8', a='A'),
]

set_up(tcc=test_cases)

for tc in test_cases:
    benchmark_can_share(tc)
