import dash
import dash_cytoscape as cyto
import dash_html_components as html
from dash.dependencies import Input, Output
import networkx as nx
import pandas as pd

app = dash.Dash(__name__)

# Pythonのパッケージ依存関係のデータを読み込み
df = pd.read_csv("adj_matrix.csv", index_col="source")
G = nx.from_pandas_adjacency(df, create_using=nx.DiGraph)

# NetworkXのデータ構造からCytoscape用のデータ構造に変換
cy = nx.readwrite.json_graph.cytoscape_data(G)

# Dash Cytoscape用のデータ構造に変換
elements = cy["elements"]["nodes"] + cy["elements"]["edges"]

default_styles = [
    {
        "selector": "node",
        "style": {
            "label": "data(id)",
            "font-size": 15,
            "text-opacity": 0.6,
            "background-color": "#58BE89",
        },
    },
    {"selector": "edge", "style": {"mid-target-arrow-shape": "vee", "arrow-scale": 2}},
]

# パッケージ名に応じてノード色を変更するスタイルを作成する
node_color_styles = [
    {"selector": "[id *= 'plotly']", "style": {"background-color": "#F8CE4B"}},
    {"selector": "[id *= 'dash']", "style": {"background-color": "#409DF6"}},
]

# 入次数に応じてノードサイズが大きくするスタイルを作成
node_size_styles = [
    {
        "selector": "[[indegree = {}]]".format(i),
        "style": {"width": 10 * (i + 1), "height": 10 * (i + 1)},
    }
    for i in range(10)
]

stylesheet = default_styles + node_color_styles + node_size_styles

cyto_div = cyto.Cytoscape(
    id="package_graph",
    style={"width": "700px", "height": "700px"},
    layout={"name": "cose"},
    elements=elements,
    stylesheet=stylesheet,
)

app.layout = html.Div(
        [
            html.H1("Dashのパッケージ依存関係"),
            cyto_div
        ]
    )


def get_neighbor_node_ids(node_element_dict):  # ❶
    """
    ノードの要素辞書から隣接ノードのIDのリストを取得する
    """
    # タップしたノードのID
    node_id = node_element_dict["data"]["id"]
    # 隣接ノードのIDを取得する
    neighbor_node_ids = [x["source"] for x in node_element_dict["edgesData"]]
    neighbor_node_ids += [x["target"] for x in node_element_dict["edgesData"]]
    # 自分自身のノードIDは除外する
    neighbor_node_ids = list(set(neighbor_node_ids) - set(node_id))
    return neighbor_node_ids


@app.callback(
    Output("package_graph", "stylesheet"),  # スタイル設定を変化させる
    [Input("package_graph", "tapNode")],  # タップしたノードの要素辞書全体を受け取る
)
def change_neighbor_node_style(node_element_dict):
    if not node_element_dict:
        return stylesheet

    # 隣接ノードのIDのリストを取得
    neighbor_node_ids = get_neighbor_node_ids(node_element_dict)

    # 隣接ノードのスタイルを作成する
    new_styles = []

    for node_id in neighbor_node_ids:
        # 隣接ノードの背景色は赤
        style = {"selector": f"#{node_id}", "style": {"background-color": "red"}}
        new_styles.append(style)

    new_stylesheets = stylesheet + new_styles

    return new_stylesheets


if __name__ == "__main__":
    app.run_server(debug=True, port=8053)
