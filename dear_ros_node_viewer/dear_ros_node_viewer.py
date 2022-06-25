# Copyright 2022 takeshi-iwanari
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Main function for Dear ROS Node Viewer
"""

from __future__ import annotations
import os
import argparse
import json
import numpy as np
import networkx as nx

from dear_ros_node_viewer.caret2networkx import caret2networkx
from dear_ros_node_viewer.networkx2dearpygui import Networkx2DearPyGui


def align_layout(graph):
    """
    Set (max+min) / 2 as origin(0, 0)

    Note:
        This logis is not mandatory. I added this just to make zoom a little better
        Without this, zoom in/out is processed based on (0,0)=left-top
        When Dear PyGui support zoomable node editor, this logic is not needed
    """
    layout_np = np.array(list(map(lambda val: val['pos'], graph.nodes.values())))
    layout_min, layout_max = layout_np.min(0), layout_np.max(0)
    offset_x = (layout_max[0] + layout_min[0]) / 2
    offset_y = (layout_max[1] + layout_min[1]) / 2
    if offset_x == 0 or offset_y == 0:
        return graph
    for node_name in graph.nodes:
        graph.nodes[node_name]['pos'][0] -= offset_x
        graph.nodes[node_name]['pos'][1] -= offset_y
    return graph


def normalize_layout(layout: dict[str, tuple[int, int]]):
    """
    Normalize positions to [0.0, 1.0] (left-top = (0, 0))

    Parameters
    ----------
    layout: dict[str,tuple[int,int]]
        Dictionary of positions keyed by node.

    Returns
    -------
    layout: dict[str,tuple[int,int]]
        Dictionary of normalized positions keyed by node.
    """

    if len(layout) == 0:
        return layout
    for key, val in layout.items():
        layout[key] = list(val)
    layout_np = np.array(list(layout.values()))
    layout_min, layout_max = layout_np.min(0), layout_np.max(0)
    norm_w = (layout_max[0] - layout_min[0])
    norm_h = (layout_max[1] - layout_min[1])
    if norm_w == 0 or norm_h == 0:
        return layout
    for pos in layout.values():
        pos[0] = (pos[0] - layout_min[0]) / norm_w
        pos[1] = (pos[1] - layout_min[1]) / norm_h
    return layout


def place_node(graph: nx.classes.digraph.DiGraph, group_name: str, prog: str = 'dot'):
    """
    Place nodes belonging to group.
    Normalized position [x, y] is set to graph.nodes[node]['pos']

    Parameters
    ----------
    graph: nx.classes.digraph.DiGraph
        NetworkX Graph
    group_name: str
        group name
    prog: str  (default: 'dot')
        Name of the GraphViz command to use for layout.
        Options depend on GraphViz version but may include:
        'dot', 'twopi', 'fdp', 'sfdp', 'circo'

    Returns
    -------
    layout: dict[str,tuple[int,int]]
        Dictionary of normalized positions keyed by node.
    """

    graph_modified = nx.DiGraph()
    for node_name in graph.nodes:
        if group_name in node_name:
            graph_modified.add_node(node_name)
    for edge in graph.edges:
        if group_name in edge[0] and group_name in edge[1]:
            graph_modified.add_edge(edge[0], edge[1])
    layout = nx.nx_pydot.pydot_layout(graph_modified, prog=prog)
    layout = normalize_layout(layout)
    return layout


def place_node_by_group(graph, group_setting):
    """
    Place all nodes
    Nodes belonging to the same group are placed in the same area.
    The area is specified in group_setting.group_setting
    """

    # for node_name in graph.nodes:
    #     graph.nodes[node_name]['pos'] = [0, 0]
    #     graph.nodes[node_name]['color'] = [128, 128, 128]

    # Add "__other__" if a node doesn't belong to any group to make process easier #
    mapping_list = {}
    for node_name in graph.nodes:
        is_other_node = True
        for group_name in group_setting.keys():
            if group_name in node_name:
                is_other_node = False
        if is_other_node:
            mapping_list[node_name] = '"' + '__others__' + node_name.strip('"') + '"'
        else:
            mapping_list[node_name] = node_name
    graph = nx.relabel_nodes(graph, mapping_list)

    # Place nodes and add properties into graph #
    for group_name, graph_property in group_setting.items():
        layout = place_node(graph, group_name)
        direction = graph_property['direction']
        offset = graph_property['offset']
        color = graph_property['color']

        for node_name in graph.nodes:
            if group_name in node_name:
                pos = layout[node_name]
                pos[1] = 1 - pos[1]     # 0.0 is top, 1.0 is bottom
                if direction == 'horizontal':
                    graph.nodes[node_name]['pos'] = \
                        [offset[0] + pos[1] * offset[2], offset[1] + pos[0] * offset[3]]
                else:
                    graph.nodes[node_name]['pos'] = \
                        [offset[0] + pos[0] * offset[2], offset[1] + pos[1] * offset[3]]
                graph.nodes[node_name]['color'] = color

    # Remove "__other__" #
    mapping_list_swap = {v: k for k, v in mapping_list.items()}
    graph = nx.relabel_nodes(graph, mapping_list_swap)

    return graph


def load_setting_json(setting_file):
    """
    Load JSON setting file
    Set default values if the file doesn't exist
    """

    if os.path.isfile(setting_file):
        with open(setting_file, encoding='UTF-8') as f_setting:
            setting = json.load(f_setting)
        app_setting = setting['app_setting']
        group_setting = setting['group_setting']
    else:
        app_setting = {
            "font": "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
        }
        group_setting = {
            "__others__": {
                "offset": [0.0, 0.0, 1.0, 1.0],
                "color": [0, 0, 0]
            }

        }
    return app_setting, group_setting


def main():
    """
    Main function for Dear ROS Node Viewer
    """
    parser = argparse.ArgumentParser(
        description='Visualize Node Diagram using Architecture File Created by CARET')
    parser.add_argument(
        '--architecture_yaml_file', type=str, default='architecture.yaml',
        help='Architecture (yaml) file path. default=architecture.yaml')
    parser.add_argument(
        '--target_path', type=str, default='all_graph',
        help='Specify path to be loaded. default=all_graph')
    parser.add_argument(
        '--setting_file', type=str, default='setting.json',
        help='default=setting.json')
    args = parser.parse_args()

    app_setting, group_setting = load_setting_json(args.setting_file)

    graph = caret2networkx(args.architecture_yaml_file, args.target_path)
    graph = place_node_by_group(graph, group_setting)
    graph = align_layout(graph)

    Networkx2DearPyGui(
        app_setting, graph, app_setting['window_size'][0], app_setting['window_size'][1])
