import heapq

graph = {
    'Bhopal': {
        'Indore': {'distance': 190, 'traffic': 1.2},
        'Nagpur': {'distance': 350, 'traffic': 1.5}
    },
    'Indore': {
        'Bhopal': {'distance': 190, 'traffic': 1.2},
        'Mumbai': {'distance': 580, 'traffic': 1.8}
    },
    'Nagpur': {
        'Bhopal': {'distance': 350, 'traffic': 1.5},
        'Mumbai': {'distance': 700, 'traffic': 1.3}
    },
    'Mumbai': {
        'Indore': {'distance': 580, 'traffic': 1.8},
        'Nagpur': {'distance': 700, 'traffic': 1.3}
    }
}
def dijkstra(start, end, mode='distance'):
    queue = [(0, start, [])]
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == end:
            return cost, path

        for neighbor, values in graph[node].items():

            if mode == 'traffic':
                weight = values['distance'] * values['traffic']
            else:
                weight = values['distance']

            heapq.heappush(queue, (cost + weight, neighbor, path))

    return float("inf"), []