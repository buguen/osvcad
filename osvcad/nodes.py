# coding: utf-8

r"""Graph nodes"""

import abc

from os.path import basename, splitext, exists

import imp
import networkx as nx
# import json
import jsonpickle
import matplotlib.pyplot as plt
from random import uniform
from ccad import model as cm
import ccad.display as cd


class Assembly(nx.DiGraph):
    r"""Acyclic directed graph modelling of a assembly"""
    def __init__(self):
        super(Assembly, self).__init__()

    def write_yaml(self, yaml_file_name):
        r"""Export to YAML format

        Parameters
        ----------
        yaml_file_name : str
            Path to the YAML file

        """
        nx.write_yaml(self, yaml_file_name)

    def write_json(self, json_file_name):
        r"""Export to JSON format
        
        Parameters
        ----------
        json_file_name : str
            Path to the JSON file
    
        """
        jsonpickle.load_backend('json')
        jsonpickle.set_encoder_options('json', sort_keys=False, indent=4)

        with open(json_file_name, "w") as f:
            f.write(jsonpickle.encode(self))

    @classmethod
    def read_json(self, json_file_name):
        r"""Construct the assembly from a JSON file"""
        j_ = ""
        with open(json_file_name) as f:
            j_ = f.read()
        return jsonpickle.decode(j_)

    def show_plot(self):
        r"""Create a Matplotlib graph of the plot"""
        val_map = {'A': 1.0,
                   'D': 0.5714285714285714,
                   'H': 0.0}

        values = [val_map.get(node, 0.25) for node in self.nodes()]

        pos = nx.spring_layout(self)
        nx.draw_networkx_nodes(self, pos, cmap=plt.get_cmap('jet'),
                               node_color=values)
        nx.draw_networkx_edges(self, pos, edgelist=self.edges(), edge_color='r',
                               arrows=True)
        nx.draw_networkx_labels(self, pos)
        nx.draw_networkx_edge_labels(self, pos)
        plt.show()

    def display_3d(self):
        r"""Display the Assembly in a 3D viewer (currently ccad viewer)"""
        v = cd.view()
        # print(self.nodes())

        for node in self.nodes():
            # print(node)
            # print(node.shape)

            # Use edges to place nodes
            in_edges_of_node = self.in_edges(node, data=True)
            print("Node : %s" % str(node))
            print("Edges of node : %s" % str(in_edges_of_node))

            assert len(in_edges_of_node) <= 1  # Pour commencer ...

            if len(in_edges_of_node) == 1:
                placed_shape = in_edges_of_node[0][2]['object'].transform(node.shape)
            elif len(in_edges_of_node) == 0:
                placed_shape = node.shape
            else:
                raise NotImplementedError

            # v.display(node.shape,
            #           ccolor=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
            #           transparency=0.5)
            v.display(placed_shape,
                      color=(uniform(0, 1), uniform(0, 1), uniform(0, 1)),
                      transparency=0.)
            if node.anchors is not None:
                for k, anchor in node.anchors.items():
                    v.display_vector(origin=anchor['position'],
                                     direction=anchor['direction'])
        cd.start()


class GeometryNode(object):
    r"""Abstract base class for geometry nodes"""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.part = None
        self.anchors = None
        self.axes = None

        # Reminder : part libraries definition!
        # part = head + threaded + unthreaded
        # anchors = {1: {"position": (0., 0., 0.),
        #                "direction": (0., 0., -1.),
        #                "dimension": d_s_max,
        #                "description": "screw head on plane"}}

    @abc.abstractproperty
    def shape(self):
        r"""Abstract method to get shape content"""
        raise NotImplementedError

    @abc.abstractproperty
    def anchors(self):
        r"""Abstract method to get anchors content"""
        raise NotImplementedError


class GeometryNodePyScript(GeometryNode):
    r"""Geometry node created from a Python script"""
    def __init__(self, py_script_path):
        super(GeometryNode, self).__init__()
        self.py_script_path = py_script_path

        # TODO : use Part.from_py of ccad
        # cm.Part.from_py("sphere_r_2.py").geometry

        name, ext = splitext(basename(py_script_path))
        module_ = imp.load_source(name, py_script_path)

        self._shape = module_.part
        self._anchors = module_.anchors

    @property
    def shape(self):
        r"""Shape getter"""
        return self._shape

    @property
    def anchors(self):
        r"""Anchors getter"""
        return self._anchors


class GeometryNodeStep(GeometryNode):
    r"""Geometry node created from a STEP file"""
    def __init__(self, step_file_path, anchors=None):
        super(GeometryNode, self).__init__()
        assert exists(step_file_path)
        self.step_file_path = step_file_path
        self._anchors = anchors
        self._shape = cm.from_step(step_file_path)

    @property
    def shape(self):
        r"""Shape getter"""
        print(type(self._shape))
        return self._shape

    @property
    def anchors(self):
        r"""Anchors getter"""
        return self._anchors


class GeometryNodeLibraryPart(GeometryNode):
    r"""Geometry node created from a parts library"""
    def __init__(self, library_file_path, part_id):
        super(GeometryNode, self).__init__()
        self.library_file_path = library_file_path
        self.part_id = part_id

        from party.library_use import generate
        from os.path import splitext, join, dirname
        generate(library_file_path)

        print(library_file_path)

        scripts_folder = join(dirname(library_file_path), "scripts")

        module_path = join(scripts_folder, "%s.py" % part_id)

        module_ = imp.load_source(splitext(module_path)[0],
                                  module_path)
        # print(module_.__dict__)
        if not hasattr(module_, 'part'):
            raise ValueError("The Python module should have a 'part' variable")
        self._shape = module_.part
        self._anchors = module_.anchors

        # self._shape, self._anchors = cm.Part.from_py("libraries/scripts/%s.py" % part_id).geometry

        # p, anchors = cm.Part.from_library(url=url, name="F63800ZZ")

    @property
    def shape(self):
        r"""Shape getter"""
        return self._shape

    @property
    def anchors(self):
        r"""Anchors getter"""
        return self._anchors
