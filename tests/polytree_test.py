#!/usr/bin/env python

from PIL import Image, ImageDraw
from polytree.registry import EdgeRegistry
from polytree.node import Node
from polytree.vertex import Vertex
from polytree.edge import Edge
from polytree.tree import Tree
from polytree.xy import XY
from random import choice
from polytree.functions import update_edges_from_new_edge, place_door_on_edge

img = Image.new("RGBA", (800, 800), "white")
draw = ImageDraw.Draw(img)

reg = EdgeRegistry()
tri_L = Node("L", None, reg)
tri_R = Node("R", None, reg)
tri_O = Node("O", None, reg)
tri_P = Node("P", None, reg)

v_butt = Vertex(50, 250)
v_face = Vertex(200, 150)
v_top = Vertex(100, 50)

e_arrow = Edge(v_butt, v_face, tri_L, tri_R)
e_spear = Edge(v_face, v_top, tri_L, tri_O)
e_poker = Edge(v_butt, v_top, None, tri_L)

reg.extend((e_arrow, e_spear, e_poker))

#print(f"e_arrow: {e_arrow}")
#print(f"e_spear: {e_spear}")
#print(f"e_poker: {e_poker}")
#print()

#print(f"v_butt: {v_butt}")
#print(f"v_face: {v_face}")
#print(f"v_top: {v_top}")
#print()

v_bottom = Vertex(225, 280)
v_top_right = Vertex(275, 80)

e_four = Edge(v_butt, v_bottom, tri_R, None)
e_five = Edge(v_bottom, v_face, tri_R, tri_P)

e_six = Edge(v_top, v_top_right, None, tri_O)
e_seven = Edge(v_face, v_top_right, tri_O, tri_P)

e_eight = Edge(v_top_right, v_bottom, None, tri_P)

#print(f"e_four: {e_four}")
#print(f"e_five: {e_five}")
#print(f"e_six: {e_six}")
#print(f"e_seven: {e_seven}")
#print(f"e_eight: {e_eight}")
#print()

reg.extend((e_four, e_five, e_six, e_seven, e_eight))

#print(f"tri_L: {tri_L}")

#reg.add_to_draw(draw)
#tri_L.centroid().add_to_draw(draw)

# registry for split testing
test_split = EdgeRegistry()

node_m = Node("M", None, test_split)
node_n = Node("N", None, test_split)
node_o = Node("O", None, test_split)

v_a = Vertex(50,50)
v_b = Vertex(150,75)
v_c = Vertex(250,200)
v_d = Vertex(100,150)

#TODO make everything consistent in checking left first
e_ab = Edge(v_a, v_b, None, node_m)
e_bc = Edge(v_b, v_c, None, node_m)
e_cd = Edge(v_c, v_d, None, node_m)
e_da = Edge(v_d, v_a, None, node_m)

test_split.extend((e_ab, e_bc, e_cd, e_da))

e_db = Edge(v_d, v_b, node_o, node_n)
test_split.extend((e_db,))
new_edge = e_db
old_node = node_m

baum = Tree(XY(800))

print("End of poly_tree.test setup") 

def splits(tree, times, even=None):
    #print(f"Splitting {times} times (even={even})")
    for _ in range(times):
        #tree.split(choice(list(tree.leaves())))
        leaves = list(tree.leaves())
        #oldest = min(*leaves)
        rnd_leaf = choice(leaves)

        #target_node_id = oldest
        target_node_id = rnd_leaf
        #print(f"splits(): even={even}")
        tree.split_node(target_node_id, even=even)

def test_oppo(tree):
    node = tree.get(choice(list(baum.leaves())))
    edge = node.get_rnd_edge()
    op_edge = node.get_opp_edge(edge)

    tree.show(labels=False,highlight=[edge,op_edge])

print("End of poly_tree.test function declarations") 
