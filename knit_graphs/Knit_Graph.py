"""The graph structure used to represent knitted objects"""
from enum import Enum
from typing import Dict, Optional, List, Tuple, Union

import networkx

from knit_graphs.Loop import Loop
from knit_graphs.Yarn import Yarn
from knitting_machine.Machine_State import Yarn_Carrier


class Pull_Direction(Enum):
    """An enumerator of the two pull directions of a loop"""
    BtF = "BtF"
    FtB = "FtB"

    def opposite(self):
        """
        :return: returns the opposite pull direction of self
        """
        if self is Pull_Direction.BtF:
            return Pull_Direction.FtB
        else:
            return Pull_Direction.BtF


class Knit_Graph:
    """
    A class to knitted structures
    ...

    Attributes
    ----------
    graph : networkx.DiGraph
        the directed-graph structure of loops pulled through other loops
    loops: Dict[int, Loop]
        A map of each unique loop id to its loop
    yarns: Dict[str, Yarn]
         Yarn Ids mapped to the corrisponding yarn
    """

    def __init__(self):
        self.graph: networkx.DiGraph = networkx.DiGraph()
        self.loops: Dict[int, Loop] = {}
        self.last_loop_id: int = -1
        self.yarns: Dict[str, Yarn] = {}

    def add_loop(self, loop: Loop):
        """
        :param loop: the loop to be added in as a node in the graph
        """
        # Add the loop to the loops dictionary

        # Create new node in the graph, attach the loop
        self.graph.add_node(loop.loop_id, loop=loop)

        assert loop.yarn_id in self.yarns, f"No yarn {loop.yarn_id} in this graph"

        # If this loop is not on its specified yarn add it to the end of the yarn
        if loop not in self.yarns[loop.yarn_id]:
            self.yarns[loop.yarn_id].add_loop_to_end(loop_id=None, loop=loop)

        # Add the loop to the loops dictionary and update last_loop_id
        self.loops[loop.loop_id] = loop


    def add_yarn(self, yarn: Yarn):
        """
        :param yarn: the yarn to be added to the graph structure
        """
        self.yarns[yarn.yarn_id] = yarn

    def connect_loops(self, parent_loop_id: int, child_loop_id: int,
                      pull_direction: Pull_Direction = Pull_Direction.BtF,
                      stack_position: Optional[int] = None, depth: int = 0, parent_offset: int = 0):
        """
        Creates a stitch-edge by connecting a parent and child loop
        :param parent_offset: The direction and distance, oriented from the front, to the parent_loop
        :param depth: -1, 0, 1: The crossing depth in a cable over other stitches. 0 if Not crossing other stitches
        :param parent_loop_id: the id of the parent loop to connect to this child
        :param child_loop_id:  the id of the child loop to connect to the parent
        :param pull_direction: the direction the child is pulled through the parent
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        assert parent_loop_id in self, f"parent loop {parent_loop_id} is not in this graph"
        assert child_loop_id in self, f"child loop {child_loop_id} is not in this graph"

        # Connect parent loop to child loop with appropriate attributes
        self.graph.add_edge(
            parent_loop_id,
            child_loop_id,
            pull_direction=pull_direction,
            depth=depth,
            parent_offset=parent_offset,
        )

        child_loop = self[child_loop_id]
        parent_loop = self[parent_loop_id]
        # Add the parent loop to the child's parent loop stack
        child_loop.add_parent_loop(parent_loop, stack_position)


    def get_courses(self) -> Tuple[Dict[int, float], Dict[float, List[int]]]:
        """
        Course information will be used to generate instruction for knitting machines and
         visualizations that structure knitted objects like grids.
         Evaluation of a course structure should be done in O(n*m) time where n is the number of loops in the graph and
         m is the largest number of parent loops pulled through a single loop (rarely more than 3).
        :return: A dictionary of loop_ids to the course they are on,
        a dictionary or course ids to the loops on that course in the order of creation
        The first set of loops in the graph is on course 0.
        A course change occurs when a loop has a parent loop that is in the last course.
        """

        loop_ids_to_course = {}
        course_to_loop_ids = {0: []}
        current_course_id = 0

        # Iterate through the loops
        for current_loop_id in range(self.last_loop_id + 1):
            # Check if there are any parent loops, if there are, then iterate through them
            for parent in self.loops[current_loop_id].parent_loops:
                # If the parent loop is in the course below the current course, there is a course change
                if loop_ids_to_course[parent.loop_id] != current_course_id-1:
                    # Course change! Increment course id and create an empty course.
                    current_course_id += 1
                    course_to_loop_ids[current_course_id] = []
            # Add values to dictionaries
            loop_ids_to_course[current_loop_id] = current_course_id
            course_to_loop_ids[current_course_id].append(current_loop_id)

        return(loop_ids_to_course, course_to_loop_ids)

    def get_carriers(self) -> List[Yarn_Carrier]:
        """
        :return: A list of yarn carriers that hold the yarns involved in this graph
        """
        return [yarn.carrier for yarn in self.yarns.values()]

    def __contains__(self, item: Union[int, Loop]) -> bool:
        """
        :param item: the loop being checked for in the graph
        :return: true if the loop_id of item or the loop is in the graph
        """
        if type(item) is int:
            return self.graph.has_node(item)
        elif isinstance(item, Loop):
            return self.graph.has_node(item.loop_id)

    def __getitem__(self, item: int) -> Loop:
        """
        :param item: the loop_id being checked for in the graph
        :return: the Loop in the graph with the matching id
        """
        if item not in self:
            raise AttributeError
        else:
            return self.graph.nodes[item]["loop"]
