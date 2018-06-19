import json

with open("network.json", "r") as read_file:
    data = json.load(read_file)

nodes = data["Topology"]["Nodes"]
links = data["Topology"]["Links"]

for key in nodes:
    print '%s: %s'%(key, nodes[key]["cost"])

# Adjacency/weight matrix for Floyd-Warshall algorithm
weight_matrix = { }

# Pad weight_matrix with infinity or zeros
for key1 in nodes:
    if key1 not in weight_matrix:
        weight_matrix[key1] = { }
    for key2 in nodes:
        if key1 == key2:
            weight_matrix[key1][key2] = 0
        else:
            weight_matrix[key1][key2] = float("inf")

# Inirialize the weight_matrix with straightforward values
for link in links:
    src  = link["src"]
    dst  = link["dst"]
    cost = link["cost"]
    # The graph is undirected - assign same weight in both directions on link
    weight_matrix[src][dst] = cost
    weight_matrix[dst][src] = cost

# Execute the Floyd-Warshall algorithm
for key_src in weight_matrix:
    for key_dst in weight_matrix[key_src]:
        for proxy_node in nodes:
            proxy_weight = weight_matrix[key_src][proxy_node] + weight_matrix[proxy_node][key_dst]
            if proxy_weight < weight_matrix[key_src][key_dst]:
                weight_matrix[key_src][key_dst] = proxy_weight

print "Link costs:"
print weight_matrix
print

# We need to keep record of the minimal achieved cost of placing VNF at a ceratin loaction
results = { }
for vnf in data["TrafficRequest"]["VnfSequence"]:
    results[vnf] = { }
    results[vnf]["cost"] = float("inf")
    results[vnf]["location"] = None

ingress_node = data["TrafficRequest"]["Source"]
egress_node  = data["TrafficRequest"]["Destination"]

# the Viterbi algorithm
previous_vnf = None
# ...iterate over graph stages (which are VNFs):
for vnf in data["TrafficRequest"]["VnfSequence"]:
    vnf_info = data["Middleboxes"][vnf]
    for substrate_node in vnf_info["locations"]:
        if previous_vnf is not None:
            prev_vnf_info = data["Middleboxes"][previous_vnf]
            for prev_substrate in prev_vnf_info["locations"]:
                new_cost = results[previous_vnf]["cost"] + weight_matrix[prev_substrate][substrate_node] + nodes[substrate_node]["cost"] + vnf_info["cost"]
                if new_cost < results[vnf]["cost"]:
                    results[vnf]["cost"] = new_cost
                    results[vnf]["location"] = substrate_node
        else:
            new_cost = weight_matrix[ingress_node][substrate_node] + nodes[substrate_node]["cost"] + vnf_info["cost"]
            if new_cost < results[vnf]["cost"]:
                results[vnf]["cost"] = new_cost
                results[vnf]["location"] = substrate_node
    previous_vnf = vnf

print results
