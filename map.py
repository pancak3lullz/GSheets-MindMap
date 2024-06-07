import gspread
from oauth2client.service_account import ServiceAccountCredentials
import networkx as nx
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("JSON-FILE-OF-YOUR-GOOGLE-PROJECT-SERVICE-ACCOUNT", scope)
client = gspread.authorize(creds)

# Open your Google Sheets document
sheet = client.open("NAME OF YOUR GOOGLE SHEET")
elements_sheet = sheet.worksheet("Elements")
connections_sheet = sheet.worksheet("Connections")

# Read elements
elements_data = elements_sheet.get_all_records()
connections_data = connections_sheet.get_all_records()

# Create a graph
G = nx.Graph()

# Add elements to the graph
for element in elements_data:
    if 'Label' in element and 'Type' in element:
        G.add_node(element['Label'], label=element['Label'], type=element['Type'])
    else:
        print("Missing key in element:", element)

# Add connections to the graph
for connection in connections_data:
    if 'From' in connection and 'To' in connection:
        G.add_edge(connection['From'], connection['To'])
    else:
        print("Missing key in connection:", connection)

# Use spring layout with increased k and iterations
pos = nx.spring_layout(G, k=2, iterations=1000)

# Function to enforce minimum distance
def enforce_min_distance(pos, min_dist):
    new_pos = pos.copy()
    for i, (node1, (x1, y1)) in enumerate(pos.items()):
        for j, (node2, (x2, y2)) in enumerate(pos.items()):
            if i >= j:
                continue
            dx = x2 - x1
            dy = y2 - y1
            dist = np.sqrt(dx**2 + dy**2)
            if dist < min_dist:
                angle = np.arctan2(dy, dx)
                move_dist = (min_dist - dist) / 2
                new_pos[node1] = (x1 - move_dist * np.cos(angle), y1 - move_dist * np.sin(angle))
                new_pos[node2] = (x2 + move_dist * np.cos(angle), y2 + move_dist * np.sin(angle))
    return new_pos

# Enforce minimum distance
min_distance = 0.05
pos = enforce_min_distance(pos, min_distance)

# Extract edge positions
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

# Extract node positions
node_x = []
node_y = []
node_text = []
node_customdata = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(G.nodes[node].get('label', node))
    node_customdata.append(node)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    text=node_text,
    textposition='top center',
    hoverinfo='text',
    customdata=node_customdata,
    marker=dict(
        showscale=True,
        colorscale='Blues',
        size=10,  # Adjust node size if necessary
        color=[],
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right',
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        ),
        line_width=2),
    textfont=dict(size=10, color='white'))  # Adjust font size if necessary

# Color nodes by degree
node_adjacencies = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))

node_trace.marker.color = node_adjacencies

# Initial figure
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Cybercrime Ops',
                    titlefont_size=16,
                    titlefont_color='white',
                    showlegend=False,
                    hovermode='closest',
                    clickmode='event+select',
                    margin=dict(b=0, l=0, r=0, t=40),  # Adjust margins to fill the screen
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='black',
                    paper_bgcolor='black'
                ))

# Set up Dash app
app = dash.Dash(__name__)
app.title = 'BROWSER TAB TITLE'  # Set the browser tab title

app.layout = html.Div([
    dcc.Dropdown(
        id='search-input',
        options=[{'label': label, 'value': label} for label in sorted(G.nodes())],
        placeholder='Search for a node...',
        multi=False,
        style={'width': '100%', 'backgroundColor': '#333', 'color': 'black', 'border': '1px solid #444'}
    ),
    html.Button('Deselect', id='deselect-button', n_clicks=0, style={'margin-top': '10px'}),
    dcc.Graph(id='network-graph', figure=fig, style={'height': '90vh', 'backgroundColor': 'black'})  # Adjust height to fill the screen
], style={'backgroundColor': 'black', 'color': 'white'})

@app.callback(
    Output('network-graph', 'figure'),
    [Input('network-graph', 'clickData'),
     Input('search-input', 'value'),
     Input('deselect-button', 'n_clicks')]
)
def update_figure(clickData, search_value, n_clicks):
    ctx = dash.callback_context

    # Reset graph if Deselect button is clicked
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'deselect-button.n_clicks':
        return fig

    node_clicked = None

    if ctx.triggered and 'network-graph.clickData' in ctx.triggered[0]['prop_id']:
        if clickData and clickData['points']:
            node_clicked = clickData['points'][0]['customdata']
    elif ctx.triggered and 'search-input.value' in ctx.triggered[0]['prop_id']:
        node_clicked = search_value

    if node_clicked is None:
        return fig

    # Highlight the clicked or searched node and its neighbors
    new_edge_x = []
    new_edge_y = []
    highlighted_nodes = {node_clicked}
    for edge in G.edges(node_clicked):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        new_edge_x.append(x0)
        new_edge_x.append(x1)
        new_edge_x.append(None)
        new_edge_y.append(y0)
        new_edge_y.append(y1)
        new_edge_y.append(None)
        highlighted_nodes.add(edge[0])
        highlighted_nodes.add(edge[1])

    highlighted_edge_trace = go.Scatter(
        x=new_edge_x, y=new_edge_y,
        line=dict(width=2, color='red'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_customdata = []
    node_color = []
    node_opacity = []
    text_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node].get('label', node))
        node_customdata.append(node)
        if node in highlighted_nodes:
            node_color.append(node_adjacencies[list(G.nodes()).index(node)])
            node_opacity.append(1.0)
            text_color.append('white')
        else:
            node_color.append('#444')
            node_opacity.append(0.2)
            text_color.append('#444')

    new_node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        hoverinfo='text',
        customdata=node_customdata,
        marker=dict(
            showscale=True,
            colorscale='Blues',
            size=10,  # Adjust node size if necessary
            color=node_color,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right',
                titlefont=dict(color='white'),
                tickfont=dict(color='white')
            ),
            line_width=2,
            opacity=node_opacity),
        textfont=dict(size=10, color=text_color))  # Adjust font size and color if necessary

    new_fig = go.Figure(data=[edge_trace, new_node_trace, highlighted_edge_trace],
                        layout=go.Layout(
                            title='Cybercrime Ops',
                            titlefont_size=16,
                            titlefont_color='white',
                            showlegend=False,
                            hovermode='closest',
                            clickmode='event+select',
                            margin=dict(b=0, l=0, r=0, t=40),  # Adjust margins to fill the screen
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            plot_bgcolor='black',
                            paper_bgcolor='black'
                        ))

    return new_fig

if __name__ == '__main__':
    app.run_server(debug=True)
