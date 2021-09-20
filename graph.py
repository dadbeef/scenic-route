import json, networkx as nx
from cachetools.func import ttl_cache
from ln import lnapi


@ttl_cache(ttl=60 * 60 * 3)
def get_graph():
    raw = get_raw()
    graph = nx.Graph()

    def _edge_attrs(edge):
        policy_ks = ['fee_base_msat', 'fee_rate_milli_msat']

        return {
            'channel_id': edge['channel_id'],
            'capacity': int(edge['capacity']),
            'node1_policy': {k: int(edge['node1_policy'][k]) for k in policy_ks},
            'node2_policy': {k: int(edge['node2_policy'][k]) for k in policy_ks},
        }

    graph.add_nodes_from([
        (node['pub_key'], {
            k: node[k] for k in ['pub_key', 'alias']
        })
        for node in raw['nodes']
    ])

    graph.add_edges_from([
        (edge['node1_pub'], edge['node2_pub'], _edge_attrs(edge))
        for edge in raw['edges'] if (
            edge['node1_policy']
            and edge['node2_policy']
            and not edge['node1_policy']['disabled']
            and not edge['node2_policy']['disabled']
        )
    ])

    # Remove nodes with no edges, add in some stats based on edges
    for k, node in list(graph.nodes(data=True)):
        channels = graph[k].values()
        n_channels = len(channels)

        if n_channels == 0:
            graph.remove_node(k)
        else:
            node.update({
                'channels': n_channels,
                'capacity': sum(c['capacity'] for c in channels) / n_channels,
                'fee_base': round(sum(
                    c[f'node{i}_policy']['fee_base_msat']
                    for c in channels for i in range(1, 2)
                ) / n_channels),
                'fee_rate': round(sum(
                    c[f'node{i}_policy']['fee_rate_milli_msat']
                    for c in channels for i in range(1, 2)
                ) / n_channels),
            })

    return graph


def get_raw():
    with open('graph.json', 'r') as f:
        return json.loads(f.read())


def refresh_graph():
    graph = lnapi('graph')

    with open('graph.json', 'w+') as f:
        return f.write(json.dumps(graph))

