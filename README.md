# GSheets MindMap

This app is a web application that visualizes and analyzes data using network graphs. The data is sourced from a Google Sheets document, making it easy to update and manage.

## Features

- Visualize data as an interactive network graph
- Search for nodes and highlight connections
- Display detailed information about nodes
- Periodically update data from Google Sheets

## Setup

### Prerequisites

- Python 3.7+
- Google Sheets API credentials
- Dash and related libraries

### Installation

1. Clone the repository:

```sh
git clone https://github.com/your-username/gsheets-mindmap.git
cd gsheets-mindmap
```

2. Install the required packages:

```sh
pip install -r requirements.txt
```

3. Set up Google Sheets API credentials:

- Follow the instructions to create a service account and download the credentials file: [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- Save the credentials file as `credentials.json` in the project directory.

4. Update the code:

- Replace `path/to/your/credentials.json` with the path to your credentials file.
- Replace `"Your Google Sheets Document Name"` with the name of your Google Sheets document.
- Replace `elements_filtered` with the titles of your columns.
  - Keep Label and Type, but change Description and AKA to whatever you want to match with your data.
  - If you change Description or AKA column names, replace code which calls those values.
- Replace `color_map` colors with your element Types.

### Running the App

```sh
python app.py
```

The application will be available at `http://localhost:8050`.

## Usage

- Use the search bar to find and highlight specific nodes.
- Click on nodes to view detailed information.
- Click the "Deselect" button to reset the highlights.
