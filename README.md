# GSheets Graph Visualization

This repository contains code to visualize graphs using data from a Google Sheets document. The visualization is created using NetworkX for graph management and Plotly/Dash for interactive visualization.

<div align="center">
   <img src="https://github.com/pancak3lullz/GSheets-MindMap/blob/main/cybercrime-ops.gif" alt="Example">
</div>

## Features

- **Google Sheets Integration**: Fetch elements and connections from a Google Sheets document.
- **Graph Visualization**: Display nodes and edges using a force-directed layout.
- **Interactive Dashboard**: Built with Dash to allow node search and interaction.
- **Custom Styling**: Nodes are styled based on their degree, with options to highlight selected nodes and connections.

## Prerequisites

1. **Google Cloud Setup**:
   - Enable the Google Sheets API and Google Drive API on your Google account.
   - Create a service account and download the JSON key file from the [Google Cloud Console](https://console.cloud.google.com/).

2. **Google Sheets Document**:
   - Create a Google Sheets document with two sheets named `Elements` and `Connections`.
   - The `Elements` sheet should have columns: `Label`, `Type`.
   - The `Connections` sheet should have columns: `From`, `To`.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/gsheets-mindmap.git
    cd gsheets-mindmap
    ```

2. **Create a virtual environment** (optional but recommended):
    ```sh
    python -m venv gsheets-mindmap-venv
    source gsheets-mindmap-venv/bin/activate  # On Windows, use `gsheets-mindmap-venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up Google Sheets API credentials**:
    - Save the JSON key file and rename it to `service_account.json`.

## Configuration

- **Update the code**:
  - Replace `"JSON-FILE-OF-YOUR-GOOGLE-PROJECT-SERVICE-ACCOUNT"` with the path to your JSON key file.
  - Replace `"NAME OF YOUR GOOGLE SHEET"` with the name of your Google Sheets document.
  - Replace `"BROWSER TAB TITLE"` with the desired title for the browser tab.

## Usage

1. **Run the application**:
    ```sh
    python map.py
    ```

2. **Access the dashboard**:
    Open your browser and navigate to `http://127.0.0.1:8050/`.

## Code Explanation

### Google Sheets API Setup

The code uses the Google Sheets API to fetch data from a specified Google Sheets document. Ensure the service account JSON file is correctly referenced and accessible.

### Graph Construction

Nodes and edges are added to the NetworkX graph based on the data fetched from the Google Sheets. Each node represents an element, and each edge represents a connection between elements.

### Layout and Visualization

A force-directed layout is used to position nodes. The `spring_layout` function helps in positioning nodes such that the edges are of approximately equal length and nodes are evenly distributed.

### Minimum Distance Enforcement

To avoid overlapping nodes, a custom function `enforce_min_distance` adjusts positions to ensure a minimum distance between nodes.

### Interactive Dashboard

Dash is used to create an interactive dashboard. The dashboard includes:
- A dropdown for searching nodes.
- A button to deselect nodes.
- A graph that updates based on interactions.

### Callbacks

Dash callbacks are used to update the graph based on user interactions. Clicking a node or selecting from the dropdown highlights the node and its connections.

## Acknowledgements

This project uses the following open-source libraries:
- [NetworkX](https://networkx.github.io/)
- [Plotly](https://plotly.com/python/)
- [Dash](https://dash.plotly.com/)
- [gspread](https://github.com/burnash/gspread)
- [oauth2client](https://github.com/google/oauth2client)
