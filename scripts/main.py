from pathlib import Path
import time
import pandas as pd
import requests

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
INPUT = DATA / "population.csv"
OUTPUT = DATA / "current_weather_stats.csv"
API = "https://api.open-meteo.com/v1/forecast"

FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
]

def main():
    df = pd.read_csv(INPUT)
    required = {
        "City", "Country", "Population", "Latitude", "Longitude"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in ["Latitude", "Longitude", "Population"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    cities = df.dropna(
        subset=["City", "Country", "Latitude", "Longitude"]
    ).head(50).copy()

    rows = []
    with requests.Session() as session:
        for i, (_, city) in enumerate(cities.iterrows(), 1):
            print(f"[{i}/50] {city['City']}, {city['Country']}")
            row = {
                "City": city["City"],
                "Country": city["Country"],
                "API_Status": "failed",
            }
            try:
                response = session.get(
                    API,
                    params={
                        "latitude": city["Latitude"],
                        "longitude": city["Longitude"],
                        "current": ",".join(FIELDS),
                        "timezone": "auto",
                    },
                    timeout=25,
                )
                response.raise_for_status()
                current = response.json().get("current", {})
                temp = current.get("temperature_2m")
                row.update({
                    "Weather_Time": current.get("time"),
                    "Temperature_C": temp,
                    "Temperature_F": (
                        round(temp * 9 / 5 + 32, 2)
                        if temp is not None else None
                    ),
                    "Humidity_Percent": current.get("relative_humidity_2m"),
                    "Feels_Like_C": current.get("apparent_temperature"),
                    "Precipitation_mm": current.get("precipitation"),
                    "Weather_Code": current.get("weather_code"),
                    "Wind_Speed_kmh": current.get("wind_speed_10m"),
                    "API_Status": "success" if temp is not None else "no_current_data",
                })
            except (requests.RequestException, ValueError, TypeError) as exc:
                print(f"  Weather request failed: {exc}")
            rows.append(row)
            time.sleep(0.1)

    weather = pd.DataFrame(rows)

    result = cities.merge(
        weather, on=["City", "Country"], how="left",
        validate="one_to_one"
    )

    result["Population"] = pd.to_numeric(
        result["Population"], errors="coerce"
    ).astype("Int64")

    for col in [
        "Temperature_C", "Temperature_F", "Humidity_Percent",
        "Feels_Like_C", "Precipitation_mm", "Wind_Speed_kmh"
    ]:
        result[col] = pd.to_numeric(result[col], errors="coerce")

    result["Temperature_Category"] = result["Temperature_C"].apply(
        lambda t: (
            "Unknown" if pd.isna(t)
            else "Cold" if t <= 10
            else "Mild" if t <= 25
            else "Hot"
        )
    )

    result.to_csv(OUTPUT, index=False)
    print("\n--- Pipeline summary ---")
    print("Input cities:", len(cities))
    print("Successful weather records:",
          (result["API_Status"] == "success").sum())
    print("Missing temperatures:", result["Temperature_C"].isna().sum())
    print("Saved to:", OUTPUT)
    print(result[[
        "City", "Country", "Population",
        "Temperature_C", "Temperature_F",
        "Temperature_Category", "API_Status"
    ]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
