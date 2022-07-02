<h1 align="center">
    <img src="./00_docs/logo.png" alt="Dear RosNodeViewer logo"></a>
</h1>

[![Python application](https://github.com/takeshi-iwanari/dear_ros_node_viewer/actions/workflows/python-app.yml/badge.svg)](https://github.com/takeshi-iwanari/dear_ros_node_viewer/actions/workflows/python-app.yml)

# Dear RosNodeViewer
## About
- Visualize ROS2 node diagram
- Support the following sources:
    - *architecture.yaml* generated by [CARET](https://tier4.github.io/CARET_doc)
    - *rosgraph.dot* generated by rqt_graph
    - running ROS graph analysis (experimental)

## Get Started
```sh
sudo apt install graphviz graphviz-dev
pip3 install -r requirements.txt
python3 -m dear_ros_node_viewer architecture.yaml
```

- Operations:
    - Middle button drag: move graph area
    - Mouse scroll: zoom in/out (zoom function is temporal)


## How to Use
[See WiKi](https://github.com/takeshi-iwanari/dear_ros_node_viewer/wiki/01.-How-to-Use)


# Acknowledgements
- Dear RosNodeViewer utilizes [Dear PyGui](https://github.com/hoffstadt/DearPyGui)
    - *Dear RosNodeViewer* is named in honor of Dear PyGui
