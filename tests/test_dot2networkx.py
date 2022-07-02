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
Test dot2networkx module
"""

import networkx as nx
from dear_ros_node_viewer.dot2networkx import dot2networkx


def test_dot2networkx():
    graph = dot2networkx('rosgraph_nodeonly.dot')
    assert(graph.has_node('"/node_src"'))

    graph = dot2networkx('rosgraph_nodetopic.dot')
    assert(graph.has_node('"/node_src"'))