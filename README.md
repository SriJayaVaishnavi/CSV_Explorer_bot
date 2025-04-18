# CSV Explorer 

Standardized LLM-based CSV analysis tool with Streamlit UI.

## Project Overview
The CSV Analyst Bot is a Streamlit-based application designed to analyze CSV files using a variety of tools. It provides a user-friendly interface for uploading CSV files and querying the data to generate insights and visualizations.

## Key Features
- **Streamlit UI**: The application uses Streamlit to create an interactive web interface, allowing users to upload CSV files and input queries.
- **Data Upload and Display**: Users can upload CSV files, which are then displayed in a tabular format.
- **Query-Based Analysis**: Users can input queries about the data, which are routed to appropriate tools for analysis.
- **Tool Routing**: The application includes a routing mechanism to select the appropriate tool based on the user's query. This is done using keyword matching and, if necessary, a language model for more nuanced understanding.
- **Visualization Tools**: The application supports various visualization tools such as line plots, bar charts, scatter plots, histograms, pie charts, and correlation matrices.

## Technical Details
- **Background and Styling**: The application includes custom styling for a modern look, with a radial gradient background and styled components.
- **Tool Functions**: The application uses a set of predefined tool functions to perform different types of data analysis and visualization.
- **Routing Logic**: The routing logic is implemented in `router.py`, which uses keyword mapping and a priority order to determine the best tool for a given query. If no direct match is found, it uses a language model to infer the appropriate tool.

## Dependencies
The project requires the following dependencies, as specified in `requirements.txt`:
- Streamlit
- Pandas
- Requests


## Usage
1. **Run the Application**: Use Streamlit to run the application and open it in a web browser.
2. **Upload CSV**: Use the file uploader to select and upload a CSV file.
3. **Input Query**: Enter a query about the data to receive insights and visualizations.
