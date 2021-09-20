import networkx as nx, copy
from graph import get_graph

defaults = {
    'weight:fee_base': 1,
    'weight:fee_rate': 1,
    'weight:channels': 0.4,
    'weight:distance': 1,
    'weight:capacity': 0.6,
    'max:fee_base': 2000,
    'max:fee_rate': 1000,
    'max:channels': 40,
    'min:channels': 8,
    'min:capacity': 900000,
}


class InvalidPublicKey(Exception):
    pass


def suggest(pub_key, **kw):
    opts = defaults.copy()
    opts.update({k: v for k, v in kw.items() if v is not None})

    g = copy.deepcopy(get_graph())

    _add_distances_and_remove_unreachable(g, pub_key, opts)
    _remove_nodes_outside_tolerances(g, pub_key, opts)
    _add_scores(g, pub_key, opts)

    return sorted(list(g.nodes().values()), key=lambda n: -n['score'])[:21]


def _add_distances_and_remove_unreachable(g, pub_key, opts):
    distances = {}
    for k in g.nodes():
        try:
            distances[k] = len(nx.shortest_path(g, pub_key, k)) - 1
        except nx.NodeNotFound:
            raise InvalidPublicKey()
        except nx.NetworkXNoPath:
            distances[k] = float('inf')

    nx.set_node_attributes(g, distances, 'distance')

    def filter_node(n):
        return 'distance' not in g.nodes[n]

    g.remove_nodes_from(list(nx.subgraph_view(g, filter_node=filter_node).nodes()))


def _remove_nodes_outside_tolerances(g, pub_key, opts):
    def filter_node(n):
        node = g.nodes[n]

        return pub_key != n and (
            node['channels'] > opts['max:channels']
            or node['channels'] < opts['min:channels']
            or node['capacity'] < opts['min:capacity']
            or node['fee_base'] > opts['max:fee_base']
            or node['fee_rate'] > opts['max:fee_rate']
        )

    g.remove_nodes_from(list(nx.subgraph_view(g, filter_node=filter_node).nodes()))


def _add_scores(g, pub_key, opts):
    maximums = {
        k: max([node[k] for node in g.nodes().values() if node[k] != float('inf')])
        for k in ['channels', 'capacity', 'fee_base', 'fee_rate', 'distance']
    }

    score_scale = {
        'distance': opts[f'weight:distance'] * (1 / maximums['distance']),
        'channels': opts[f'weight:channels'] * (1 / maximums['channels']),
        'capacity': opts[f'weight:capacity'] * (1 / maximums['capacity']),
        'fee_base': opts[f'weight:fee_base'] * (1 / maximums['fee_base']),
        'fee_rate': opts[f'weight:fee_rate'] * (1 / maximums['fee_rate']),
    }

    scores = {}
    for k, node in g.nodes().items():
        scores[k] = sum([
            # Distance may be infinite for non-connected nodes, score it 1 better than the max
            score_scale['distance'] * min(node['distance'], maximums['distance'] + 1),
            score_scale['channels'] * node['channels'],
            score_scale['capacity'] * node['capacity'],
            1 - (score_scale['fee_base'] * node['fee_base']),
            1 - (score_scale['fee_rate'] * node['fee_rate']),
        ]) / 5

    nx.set_node_attributes(g, scores, 'score')
