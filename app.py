import gspread
from oauth2client.service_account import ServiceAccountCredentials
import networkx as nx
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_auth
import visdcc
import dash

# Basic auth setup
VALID_USERNAME_PASSWORD_PAIRS = {
    'username1': 'password1',
    'username2': 'password2',
    'username3': 'password3',
    'username4': 'password4'
}

app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.title = 'TITLE OF YOUR MAP'

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path/to/your/credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheets document
sheet = client.open("Your Google Sheets Document Name")
elements_sheet = sheet.worksheet("Elements")
connections_sheet = sheet.worksheet("Connections")

# Function to fetch data from Google Sheets
def fetch_data():
    elements_data = elements_sheet.get_all_values()
    elements_header = elements_data[0]
    elements_filtered = [
        {
            'Label': row[elements_header.index('Label')],
            'Type': row[elements_header.index('Type')],
            'Description': row[elements_header.index('Description')],
            'AKA': row[elements_header.index('AKA')]
        }
        for row in elements_data[1:]
    ]

    connections_data = connections_sheet.get_all_values()
    connections_header = connections_data[0]
    connections_filtered = [
        {
            'From': row[connections_header.index('From')],
            'To': row[connections_header.index('To')]
        }
        for row in connections_data[1:]
    ]

    G = nx.Graph()

    for element in elements_filtered:
        label = element.get('Label', 'Unknown')
        type_ = element.get('Type', 'Unknown')
        description = element.get('Description', '')
        aka = element.get('AKA', '')
        G.add_node(label, label=label, type=type_, description=description, aka=aka)

    for connection in connections_filtered:
        if 'From' in connection and 'To' in connection:
            G.add_edge(connection['From'], connection['To'])
        else:
            print("Missing key in connection:", connection)

    for node in G.nodes():
        if 'label' not in G.nodes[node]:
            G.nodes[node]['label'] = node
        if 'type' not in G.nodes[node]:
            G.nodes[node]['type'] = 'Unknown'
        if 'description' not in G.nodes[node]:
            G.nodes[node]['description'] = ''
        if 'aka' not in G.nodes[node]:
            G.nodes[node]['aka'] = ''

    color_map = {
        'Group': 'blue',
        'Malware': 'orange',
        'Organization': 'red',
        'Person': 'green',
        'Ransomware': 'purple',
        'Vulnerability': 'pink',
        'Unknown': '#97C2FC'
    }

    nodes = [{'id': node, 'label': G.nodes[node]['label'], 'title': f"Type: {G.nodes[node]['type']}", 'color': color_map.get(G.nodes[node]['type'], '#97C2FC')} for node in G.nodes()]
    edges = [{'from': edge[0], 'to': edge[1]} for edge in G.edges()]

    search_options = []
    for node in G.nodes():
        search_options.append({'label': G.nodes[node]['label'], 'value': G.nodes[node]['label']})
        if G.nodes[node]['aka']:
            search_options.append({'label': f"{G.nodes[node]['label']} (AKA: {G.nodes[node]['aka']})", 'value': G.nodes[node]['label']})

    return nodes, edges, search_options, color_map, G

nodes, edges, search_options, color_map, G = fetch_data()

app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0),
    dcc.Store(id='graph-data', data={'nodes': nodes, 'edges': edges, 'search_options': search_options, 'G': nx.node_link_data(G)}),
    dcc.Dropdown(
        id='search-input',
        options=search_options,
        placeholder='Search for a node...',
        multi=False,
        style={'width': '100%', 'backgroundColor': '#333', 'color': 'black', 'border': '1px solid #444'}
    ),
    html.Button('Deselect', id='deselect-button', n_clicks=0, style={'margin-top': '10px'}),
    dcc.Loading(
        id='loading-icon',
        type='circle',
        children=[
            html.Div(
                visdcc.Network(
                    id='network-graph',
                    data={'nodes': nodes, 'edges': edges},
                    options={
                        'interaction': {
                            'dragNodes': True,
                            'dragView': True,
                            'zoomView': True
                        },
                        'nodes': {
                            'color': 'white',
                            'font': {'color': 'white'}
                        },
                        'edges': {
                            'color': 'lightgray'
                        },
                        'physics': {
                            'enabled': True
                        },
                        'layout': {
                            'randomSeed': 42
                        }
                    },
                    style={'height': '75vh', 'width': '100%', 'position': 'relative'}
                ),
                style={'height': '75vh', 'width': '100%', 'position': 'relative'}
            ),
            html.Div(
                id='color-legend',
                children=[
                    html.Div([
                        html.Div(style={'display': 'inline-block', 'width': '15px', 'height': '15px', 'backgroundColor': color, 'margin-right': '5px'}),
                        html.Span(type_, style={'fontSize': '12px'})
                    ]) for type_, color in color_map.items()
                ],
                style={
                    'position': 'absolute', 'top': '300px', 'left': '10px', 'backgroundColor': 'rgba(0, 0, 0, 0.7)',
                    'padding': '10px', 'borderRadius': '5px', 'color': 'white', 'zIndex': '1000', 'fontSize': '12px'
                }
            )
        ]
    ),
    html.Div(id='node-info', style={'backgroundColor': '#222', 'color': 'white', 'padding': '10px', 'height': '25vh', 'overflowY': 'scroll', 'width': '100%'}),
    dcc.Store(id='clicked-node', data=None)
], style={'backgroundColor': 'black', 'color': 'white', 'height': '100vh', 'width': '100%', 'overflow': 'hidden'})

@app.callback(
    [Output('graph-data', 'data'),
     Output('network-graph', 'data'),
     Output('search-input', 'options'),
     Output('search-input', 'value'),
     Output('clicked-node', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('search-input', 'value'),
     Input('deselect-button', 'n_clicks'),
     Input('network-graph', 'selection')]
)
def update_data(n_intervals, search_value, n_clicks, selection):
    ctx = dash.callback_context
    nodes, edges, search_options, color_map, G = fetch_data()

    graph_data = {'nodes': nodes, 'edges': edges, 'search_options': search_options, 'G': nx.node_link_data(G)}

    node_to_highlight = None

    if ctx.triggered:
        trigger = ctx.triggered[0]['prop_id']

        if trigger == 'search-input.value':
            node_to_highlight = search_value
        elif trigger == 'network-graph.selection':
            if selection and 'nodes' in selection and selection['nodes']:
                node_to_highlight = selection['nodes'][0]
        elif trigger == 'deselect-button.n_clicks':
            return graph_data, {'nodes': nodes, 'edges': edges}, search_options, None, None

    if node_to_highlight:
        highlighted_nodes = set()
        for node in nodes:
            if node['id'] == node_to_highlight:
                highlighted_nodes.add(node['id'])
                for edge in G.edges(node_to_highlight):
                    for n in nodes:
                        if n['id'] == edge[1]:
                            highlighted_nodes.add(n['id'])

        for node in nodes:
            if node['id'] not in highlighted_nodes:
                node['opacity'] = 0.1
                node['color'] = 'gray'

        return graph_data, {'nodes': nodes, 'edges': edges}, search_options, None, node_to_highlight

    return graph_data, {'nodes': nodes, 'edges': edges}, search_options, None, None

@app.callback(
    Output('node-info', 'children'),
    [Input('search-input', 'value'),
     Input('clicked-node', 'data'),
     Input('deselect-button', 'n_clicks'),
     Input('graph-data', 'data')]
)
def update_node_info(search_value, clicked_node, n_clicks, graph_data):
    ctx = dash.callback_context
    node_to_display = search_value if search_value else clicked_node

    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'deselect-button.n_clicks':
        return ""

    G = nx.node_link_graph(graph_data['G'])

    if node_to_display and node_to_display in G.nodes:
        node_data = G.nodes[node_to_display]
        description = node_data.get('description', 'No description available.')
        aka = node_data.get('aka', 'No alternative names available.')
        return [
            html.H4(f"Node: {node_to_display}"),
            html.Div([
                html.Div([
                    html.P(f"Description: {description}", style={'padding-bottom': '10px'}),
                ], style={'overflowY': 'auto', 'maxHeight': '50%'}),
                html.Div([
                    html.P(f"AKA: {aka}", style={'border-top': '1px solid #444', 'padding-top': '10px'})
                ], style={'overflowY': 'auto', 'maxHeight': '50%'})
            ], style={'height': '100%'})
        ]
    return ""

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
