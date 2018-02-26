#!/usr/bin/env python

#TODO how to pep8?

from rectree_node import *
from line import *
from PIL import Image, ImageDraw

class Edge():
    ''' a Line and up to 2 Nodes'''
    def __init__(self, line, node, same_as=None):
        self.line = line
        self.nodes = node
        self.same_as = same_as

    def __repr__(self):
        # Don't print __repr__ of the linked Edge to avoid
        # infinite reflection
        return "{}: {} aka {}: {}".format(self.line, self.node, self.same_as.line, self.same_as.node))

class Tree():
    ''' a binary tree of Rectangles '''

    def __init__(self, rectangle):
        self.root = Node(0, None, rectangle)
        # the highest ID currently in the tree
        self.max_id = 0

        # A registry of all Edges in the Tree
        self.edges = {}
        for line in self.root.edges:
            self.edges[line] = [self.root]

        # Store the dimensions of the root node since we'll be
        # deleting its Rectangle
        self.canvas = rectangle.dims

    def get(self, id):
        def walk(cur, id):
            if cur is None:
                return
            elif cur.id == id:
                return cur

            found = walk(cur.a, id)
            if found:
                return found

            found = walk(cur.b, id)
            if found:
                return found

        return walk(self.root, id)

    def register_edge(self, new_edge):
        print("> Registering Edge {}".format(new_edge))

        def dovetail(line_a, node_a, line_b, node_b):
            #TODO maybe I should make a segment class?
            #TODO I don't like using 0 and assuming a single item list

            print(">> Dovetailing lines {} and {}".format(line_a, line_b))

            last_vertex = None
            new_segments = {}

            # remove duplicates so we don't get 0-length lines
            for vertex in sorted(set([line_a.start, line_a.end, line_b.start, line_b.end])):
                if last_vertex:
                    new_line = Line(last_vertex, vertex)
                    new_segments[new_line] = []
                    if new_line.issubset(line_a):
                        #TODO use append or += ?
                        new_segments[new_line].append(node_a)
                        print("Dovetail {:19} + {} ({})".format(str(new_line), node_a, new_segments[new_line]))
                    if new_line.issubset(line_b):
                        new_segments[new_line].append(node_b)
                        print("Dovetail {:19} + {} ({})".format(str(new_line), node_b, new_segments[new_line]))
                last_vertex = vertex

            #print("Returning new segment(s): {}".format(new_segments))
            return new_segments

        if new_edge in self.edges:
            #this exact line is already in the registry
            #just add this node to that segment
            assert len(self.segments[new_line]) == 1, "Segment doesn't have exactly 1 node: {}".format(self.segments[new_line])
            self.segments[new_line] += [new_node]
            print("Segment {:19} + {} ({}) just append a node".format(str(new_line), new_node, self.segments[new_line]))
            return

        # check for overlapping segments
        for existing_line in self.segments:
            #print("Checking existing_line {} for overlap".format(existing_line))
            if new_line.overlaps(existing_line):
                print("{} overlaps with {} ({})".format(new_line, existing_line, self.segments[existing_line]))
                existing_node = self.segments[existing_line][0]
                new_segments = dovetail(new_line, new_node, existing_line, existing_node)

                #the existing line will be entirely replaced
                del self.segments[existing_line]

                print("Processing dovetails: {}".format(new_segments))
                for new_segment_line in new_segments:
                    print("Processing {}".format(new_segment_line, new_segments[new_segment_line]))
                    #TODO I think I need a segment class
                    if existing_node in new_segments[new_segment_line]:
                        #any segment associated with the old node goes straight into
                        #the registry
                        #print(self.segments)
                        #print(new_segment_line)
                        assert new_segment_line not in self.segments, "Trying to overwrite {} ({}) with dovetail {} ({})".format(new_segment_line, self.segments[new_segment_line], new_segment_line, existing_node)
                        self.segments[new_segment_line] = new_segments[new_segment_line]
                        print("Segment {:19} = {} ({}) add any olds".format(str(new_segment_line), new_segments[new_segment_line], self.segments[new_segment_line]))
                    else:
                        self.add_segment(new_segment_line, new_node)
                #bail out - we can only find one overlap per invocation, maybe?
                break

        # Whatever makes it here gets added as a new segment, because
        # if it had overlapped, it would have gotten dovetailed and
        # then fed back into add_segment. So this is sort of like the
        # base case of a recursive function. Sort of. I think.
        self.segments[new_line] = [new_node]
        print("Segment {:19} = {} ({}) last resort".format(str(new_line), new_node, self.segments[new_line]))
        return
    
    def split(self, id, direction=None):
        cur = self.get(id)

        print("=== Splitting {} (probably into Node {} and Node {})".format(cur, self.max_id + 1, self.max_id + 2))

        #TODO may be time to learn to implement exception handling
        # Check if node exist
        if cur is None:
            print("Could not find Node {}".format(id))
            return

        # Check if node is a leaf node
        if not ( cur.a is None and cur.b is None ):
            print("You can only split leaf nodes. This node has children: {}".format(cur))
            return

        # If no direction is specified, split across the short dimension or
        # split randomly if it's a square
        if direction is None:
            if cur.rect.dims.x > cur.rect.dims.y:
                direction = "v"
            elif cur.rect.dims.x < cur.rect.dims.y:
                direction = "h"
            else:
                direction = choice(("v", "h"))

        # Split the Rectangle in the matching direction
        #TODO I once thought that I was glad I made separate splits on the
        # Rectangle object, but I no longer remember why. It doesn't seem to
        # fit with future diagonal split support
        if direction.startswith("v"):
            rect_a, rect_b = cur.rect.v_split()
        elif direction.startswith("h"):
            rect_a, rect_b = cur.rect.h_split()
        else:
            print("Something went wrong. Direction has to start with 'v' or 'h' but is {}".format(direction))
            return

        '''
            Design Considerations
                Would like to allow for diagonal splits
        '''

        #                add Edges to tree's Edge registry

        print("Cleaning up edges of {}".format(cur))

        # Remove Node's Rectangle
        #TODO what is the good way to delete/remove/blank things in objects?
        cur.rect = None
        
        # Remove Node from Edges in the Tree's registry
        for edge in cur.edges:
            #TODO I'm making a dict where keys are Lines and values are Edges, which are
            # a Line and up to two Nodes. This double-use of the same Line must be stupid?
            self.segments[edge.line].remove_node(cur)
            #print("Segment {:19} - {} ({})".format(str(line), cur, self.segments[line]))
            # If this leaves the Edge empty, delete it from the registry
            if self.segments[edge.line].isempty():
                #print("Deleting empty segment {}".format(line))
                #TODO when referencing the same index multiple times, do I just make a "pointer" to it?
                del self.segments[edge.line]

        # Delete the Node's Edges
        cur.edges = None

        #TODO Make an add_node() method or use Node.__init__()?
        # A method would keep Node agnostic of Tree's ID scheme
        cur.a = self.add_node(cur, rect_a)
        cur.b = self.add_node(cur, rect_b)

        return cur.a, cur.b

    def add_node(self, parent, rectangle):
        self.max_id += 1

        new_node = Node(self.max_id, parent, rectangle)

        # Add the edges to the Tree's registry
        for edge in new_node.edges:
            self.register_edge(edge)

        return new_node

    def leaves(self, start_id=0):
    # This only shows the id, not the rectangles
        def walk(node):
            if node.a is None and node.b is None:
                return [node.id]
            else:
                return walk(node.a) + walk(node.b)

        #return set(walk(self.root))
        return set(walk(self.get(start_id)))

    def show(self):
        img_size = self.canvas + 1

        img = Image.new("RGBA", img_size.astuple(), "black")

        draw = ImageDraw.Draw(img)

        self.add_to_draw(draw)

        for segment in self.segments:
            assert len(self.segments[segment]) == 1 or len(self.segments[segment]) == 2, "Segment {} has an impossible number of associated nodes: {} ({})".format(segment, len(self.segments[segment]), self.segments[segment])

            # All Edges are pink
            # Color all Edges tracked in the registry in blue
            draw.line(segment.astuples(), fill="blue", width=3)

            if len(self.segments[segment]) == 2:
                # Color all shared Edges green
                draw.line(segment.astuples(), fill="lightgreen", width=3)
                # Connect the centroids of adjacent Rectangles
                centroid_a = self.segments[segment][0].centroid()
                centroid_b = self.segments[segment][1].centroid()
                draw.line((centroid_a.astuple(), centroid_b.astuple()), fill="black")

        img.show()

    def add_to_draw(self, draw):
        def draw_all(cur):
            if cur is None:
                return
            if not cur.a and not cur.b:
                #only draw leaf nodes
                cur.rect.add_to_draw(draw)

            draw_all(cur.a)
            draw_all(cur.b)

        draw_all(self.root)

    def __repr__(self):
    # This only shows the id, not the rectangles

        #DEBUG - print a blank like to make output OK in iPython
        print("\n") #for ipython

        #draw_bst only prints to STDOUT so casting to str in order
        # to satisfy the __repr__ requirement causes it to also
        # print None after the tree
        #TODO Have to alter drawtree.py
        return str(drawtree(self.root))