import streamlit as st
import json
import time
import requests
from julep import Julep
from io import StringIO

# Set page configuration
st.set_page_config(page_title="Foodie Tour Generator", layout="wide", page_icon="🍽️")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stApp { max-width: 1200px; margin: auto; }
    .title { font-size: 2.5em; color: #2c3e50; text-align: center; margin-bottom: 0.5em; }
    .subtitle { font-size: 1.2em; color: #7f8c8d; text-align: center; margin-bottom: 2em; }
    .card { background-color: white; padding: 1.5em; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 1em; }
    .card-title { font-size: 1.5em; color: #e74c3c; margin-bottom: 0.5em; }
    .card-text { font-size: 1em; color: #34495e; }
    .sidebar .sidebar-content { background-color: #ecf0f1; }
    .stButton>button { background-color: #e74c3c; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #c0392b; }
    </style>
""", unsafe_allow_html=True)

# Julep API key
JULEP_API_KEY = st.secrets["JULEP_API"]

# Initialize Julep client
client = Julep(api_key=JULEP_API_KEY, environment="production")

# Agent ID from Step 2
agent_id = "0684428f-e045-76d5-8000-3f78054879ba"

# Weather function (corrected URL, debug prints removed)
def get_weather(city):
    city_coords = {
        "Paris": {"lat": 48.8566, "lon": 2.3522},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503}
    }
    if city not in city_coords:
        return {"temperature": None, "condition": "unknown", "is_outdoor": False, "error": f"City {city} not found in coordinates database"}
    lat, lon = city_coords[city]["lat"], city_coords[city]["lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        temperature = data["current"]["temperature_2m"]
        weathercode = data["current"]["weathercode"]
        condition = "clear" if weathercode == 0 else "cloudy" if weathercode <= 3 else "other"
        is_outdoor = condition == "clear" and temperature > 15
        return {
            "temperature": temperature,
            "condition": condition,
            "is_outdoor": is_outdoor
        }
    except requests.RequestException as e:
        return {"temperature": None, "condition": "unknown", "is_outdoor": False, "error": f"Error fetching weather for {city}: {str(e)}"}

# Foodie tour generation function (unchanged, debug prints removed)
def generate_foodie_tour(city, weather):
    dining_type = "outdoor" if weather["is_outdoor"] else "indoor"
    prompt = f"""
    Create a one-day foodie tour for {city}. Today's weather is {weather['condition']} with a temperature of {weather['temperature']}°C, suitable for {dining_type} dining. Follow these steps:
    1. Identify three iconic dishes for {city} based on its culinary culture.
    2. Find top-rated restaurants in {city} that serve these dishes, prioritizing highly reviewed establishments.
    3. Generate a narrative for breakfast, lunch, and dinner, including restaurant names, addresses, dish descriptions, and how the weather influences the dining experience.
    4. Output the response as a JSON object with fields: 'city' (string), 'weather' (object with 'temperature' as a number, 'condition' as a string, 'dining' as a string), 'iconic_dishes' (array of three strings), and 'tour' (object with 'breakfast', 'lunch', 'dinner', each containing 'restaurant', 'address', 'dish', 'description', 'weather_consideration' as strings).
    Ensure the narrative is engaging, culturally relevant, and reflects the {dining_type} dining environment.
    Return only valid JSON with no extra text, backticks, or markdown formatting.
    """
    try:
        task_definition = {
            "name": "Foodie Tour Generator",
            "description": "Generate a one-day foodie tour for a given city based on weather",
            "main": [
                {
                    "prompt": [
                        {"role": "system", "content": "You are a culinary expert specializing in food tours."},
                        {"role": "user", "content": prompt}
                    ]
                }
            ]
        }
        task = client.tasks.create(
            agent_id=agent_id,
            **task_definition
        )
        max_retries = 2
        for attempt in range(max_retries):
            execution = client.executions.create(
                task_id=task.id,
                input={
                    "city": city,
                    "temperature": weather["temperature"],
                    "condition": weather["condition"],
                    "dining_type": dining_type
                }
            )
            timeout = time.time() + 60
            while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
                time.sleep(2)
                if time.time() > timeout:
                    return {"error": f"Execution timed out for {city}"}
            if result.status == "succeeded":
                raw_response = result.output['choices'][0]['message']['content']
                parsed_response = json.loads(raw_response)
                return parsed_response
            else:
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    return {"error": f"Execution failed for {city}: {result.error}"}
    except Exception as e:
        return {"error": f"Error generating foodie tour for {city}: {e.__class__.__name__}: {str(e)}"}

# Workflow function for multiple cities (processing messages removed)
def main_workflow(cities):
    results = []
    for city in cities:
        weather = get_weather(city)
        if weather.get("error"):
            results.append({"city": city, "error": weather["error"]})
            continue
        if weather["temperature"] is not None:
            foodie_tour = generate_foodie_tour(city, weather)
            if foodie_tour and not foodie_tour.get("error"):
                results.append(foodie_tour)
            else:
                results.append({"city": city, "error": foodie_tour.get("error", "Failed to generate foodie tour")})
        else:
            results.append({"city": city, "error": "Failed to fetch weather"})
        time.sleep(1)  # Avoid API rate limits
    return results

# Initialize session state for JSON toggle
if "show_json" not in st.session_state:
    st.session_state.show_json = {}

# Sidebar for city selection
with st.sidebar:
    st.header("City Selection")
    predefined_cities = ["Paris", "New York", "Tokyo"]
    selected_cities = st.multiselect(
        "Choose cities:",
        options=predefined_cities,
        default=["Paris"],
        help="Select one or more cities from the list."
    )
    custom_city = st.text_input("Add a custom city:", help="e.g., London (note: only predefined cities are supported)")
    if custom_city:
        custom_city = custom_city.strip()
        if custom_city and custom_city not in selected_cities:
            selected_cities.append(custom_city)
    
    if selected_cities:
        st.markdown(f"**Selected cities:** {', '.join(selected_cities)}")
    else:
        st.warning("Please select at least one city.")

# Main content
st.markdown('<div class="title">Foodie Tour Generator 🍽️</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Plan your culinary adventure with weather-based dining recommendations!</div>', unsafe_allow_html=True)

if st.button("Generate Foodie Tours", key="generate_button"):
    if selected_cities:
        with st.spinner("Generating foodie tours..."):
            results = main_workflow(selected_cities)
        if results:
            st.subheader("Foodie Tour Results")
            for result in results:
                if result.get("error"):
                    st.error(f"Error for {result['city']}: {result['error']}")
                    continue
                city = result["city"]
                with st.expander(f"Foodie Tour for {city}", expanded=True):
                    # Visualizations using cards
                    st.markdown(f"**Weather**: {result['weather']['condition'].capitalize()}, {result['weather']['temperature']}°C, {result['weather']['dining'].capitalize()} dining")
                    st.markdown(f"**Iconic Dishes**: {', '.join(result['iconic_dishes'])}")
                    for meal in ["breakfast", "lunch", "dinner"]:
                        meal_data = result["tour"][meal]
                        st.markdown(f'<div class="card"><div class="card-title">{meal.capitalize()}</div>', unsafe_allow_html=True)
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**Restaurant**: {meal_data['restaurant']}")
                            st.markdown(f"**Address**: {meal_data['address']}")
                            st.markdown(f"**Dish**: {meal_data['dish']}")
                            st.markdown(f"**Description**: {meal_data['description']}")
                        with col2:
                            st.markdown(f"**Weather Consideration**: {meal_data['weather_consideration']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    # Button to toggle JSON display
                    if st.button("Toggle Raw JSON", key=f"json_toggle_{city}"):
                        st.session_state.show_json[city] = not st.session_state.show_json.get(city, False)
                    if st.session_state.show_json.get(city, False):
                        st.json(result)
            
            # Download JSON
            json_str = json.dumps({"foodie_tours": results}, indent=2)
            st.download_button(
                label="Download Foodie Tours as JSON",
                data=json_str,
                file_name="foodie_tours.json",
                mime="application/json",
                key="download_button"
            )
        else:
            st.error("No foodie tours generated.")
    else:
        st.error("Please select at least one city.")

st.markdown("---")
st.markdown("powered by Julep AI and Open-Meteo for weather data - assignment submission")