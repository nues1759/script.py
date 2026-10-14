import csv
import requests
import json

BASE_URL = "https://api.open-meteo.com/v1/forecast"


try:
    with open("cities.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cities = list(reader)
except FileNotFoundError:
    print("Error: cities.csv not found.")
    exit()

results = []
hottestCity = None
hottestTemp = float("-inf")

with open("weather_results.txt", "w", encoding="utf-8") as out:
    for row in cities:
        city = row.get("city")
        lat = row.get("latitude")
        lon = row.get("longitude")

        try:
            r = requests.get(
                BASE_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": "true"
                },
                timeout=10
            )
            r.raise_for_status() 

            data = r.json()
            temp = data["current_weather"]["temperature"]
            wind = data["current_weather"]["windspeed"]
            time = data["current_weather"]["time"]
            winddirection = data["current_weather"]["winddirection"]
            status = "Hot" if temp > 30 else "Mild"

            
            out.write(
                f"{city}: Temperature {temp}°C, Wind {wind} km/h, Time {time}, Wind Direction {winddirection}°, Status {status}\n"
            )

            results.append({
            "city": city,
            "temperature": {"value": temp, "unit": "°C"},
            "wind": {"value": wind, "unit": "km/h"},
            "time": time,
            "winddirection": {"value": winddirection, "unit": "°"},
            "status": status
})

            if temp > hottestTemp:
                hottestTemp = temp
                hottestCity = city

        except requests.exceptions.Timeout:
            out.write(f"{city}: request timed out\n")
        except requests.exceptions.RequestException as e:
            out.write(f"{city}: request failed ({e})\n")
        except (KeyError, ValueError) as e:
            out.write(f"{city}: bad response format ({e})\n")


with open("weather_results.json", "w", encoding="utf-8") as json_out:
    json.dump(results, json_out, indent=4, ensure_ascii=False)

print("Done! Check weather_results.txt and weather_results.json")
if hottestCity:
    print(f"Hottest city: {hottestCity} with temperature: {hottestTemp}°C")