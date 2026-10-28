# Weather Pipeline

This project collects current weather data for different cities and combines it with population data.

### What it does
- Reads city and population details from a CSV file.
- Gets current weather data from the Open-Meteo API.
- Combines both datasets using Python and Pandas.
- Uses BigQuery to analyse the data.
- Shows the results in a Looker Studio dashboard.

### Tools Used
- Python
- Pandas
- Open-Meteo API
- BigQuery
- Looker Studio

### Output
The pipeline creates a dataset with weather and population details for 50 cities. It includes temperature, humidity, wind speed and other weather information.

The dashboard shows weather summaries, a world map, temperature categories and comparisons of the hottest cities and countries.
