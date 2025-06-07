# assignment-julep

# Foodie Tour Generator (JULEP AI) Streamlit App

## Overview
This project is a Streamlit web application that generates personalized one-day foodie tours for selected cities based on current weather conditions. The app fetches weather data from the Open-Meteo API and uses the Julep API to create culturally relevant food tours, recommending iconic dishes and top-rated restaurants for breakfast, lunch, and dinner. The app supports multiple cities, provides a user-friendly interface with card-based visualizations, and allows users to download results as a JSON file.

The development process involved creating the core functionality, integrating it into a Streamlit app, and iteratively addressing errors and enhancing features based on user feedback.

## Features
- **City Selection**: Users can choose from predefined cities (Paris, New York, Tokyo) via a multiselect dropdown or enter custom cities through a text input.
- **Weather-Based Tours**: Fetches real-time weather data to determine indoor or outdoor dining suitability.
- **Foodie Tour Generation**: Creates a JSON-formatted tour for each city, including:
  - Weather details (temperature, condition, dining type).
  - Three iconic dishes.
  - Breakfast, lunch, and dinner recommendations with restaurant names, addresses, dishes, descriptions, and weather considerations.
- **Visualizations**: Displays tours in a clean, card-based layout with weather and dish details.
- **JSON Output**: Shows raw JSON data (toggled via a button) and allows downloading as `foodie_tours.json`.
- **Error Handling**: Minimal error messages for unsupported cities or API failures.
- **Streamlit UI**: Professional design with a sidebar for city selection, custom CSS, and a wide layout.

## Development Journey

### Step 1: Core Functionality
- **Objective**: Create functions to fetch weather data and generate foodie tours.
- **Components**:
  - `get_weather(city)`: Fetches temperature and weather conditions from Open-Meteo API for predefined cities (Paris, New York, Tokyo).
  - `generate_foodie_tour(city, weather)`: Uses Julep API to generate a JSON tour based on weather and city.
  - `main_workflow(cities)`: Coordinates weather fetching and tour generation for multiple cities.
- **Challenges**:
  - Initial `400 Bad Request` errors in `get_weather` due to an incorrect URL parameter (`current` vs. `%C2%A4t`).
  - Fixed by correcting the URL:
    ```python
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode&timezone=auto"
    ```

### Step 2: Streamlit Integration
- **Objective**: Build a Streamlit app to provide a user-friendly interface.
- **Features Added**:
  - Sidebar with multiselect for predefined cities and text input for custom cities.
  - Main panel with a title, subtitle, and “Generate Foodie Tours” button.
  - Results displayed in expandable sections per city with JSON output.
  - Download button for `foodie_tours.json`.
- **Challenges**:
  - Syntax error in `st.error` line due to an extra quote (`""`).
    - Fixed by removing the extra quote:
      ```python
      st.error(f"Error for {result['city']}: {result['error']}")
      ```
  - Reappearance of the `400 Bad Request` error in `get_weather`, fixed by reapplying the URL correction.

### Step 3: UI Enhancements
- **Objective**: Improve the Streamlit app based on user feedback to remove processing messages, enhance visualizations, and refine the layout.
- **Changes Made**:
  - **Silent Processing**: Removed all debug prints (`st.write`, `st.spinner`, `st.success`, `st.error`) from `get_weather`, `generate_foodie_tour`, and `main_workflow`, showing only final results or minimal error messages.
  - **Visualizations**: Added card-based layouts for breakfast, lunch, and dinner using `st.columns` and custom CSS:
    - Left column: Restaurant, address, dish, description.
    - Right column: Weather consideration.
  - **Layout Improvements**:
    - Wide layout (`st.set_page_config(layout="wide")`).
    - Custom CSS for cards, buttons, and typography.
    - Sidebar for city selection.
    - Footer with branding.
  - **JSON Display**: Initially used a nested `st.expander("View Raw JSON")`, causing a `StreamlitAPIException`.

### Step 4: Fixing Nested Expander Error
- **Objective**: Resolve `StreamlitAPIException: Expanders may not be nested inside other expanders`.
- **Issue**: The JSON display was nested inside city expanders:
  ```python
  with st.expander(f"Foodie Tour for {city}"):
      with st.expander("View Raw JSON"):
          st.json(result)
  ```
- **Solution**:
  - Replaced the inner expander with a button toggle using `st.session_state`:
    ```python
    if st.button("Toggle Raw JSON", key=f"json_toggle_{city}"):
        st.session_state.show_json[city] = not st.session_state.show_json.get(city, False)
    if st.session_state.show_json.get(city, False):
        st.json(result)
    ```
  - Added session state initialization:
    ```python
    if "show_json" not in st.session_state:
        st.session_state.show_json = {}
    ```
- **Outcome**: Eliminated nesting, preserving JSON functionality.

## Setup Instructions

### Option 1: Run in Google Colab with LocalTunnel
1. **Open a New Colab Notebook**:
   - Go to [Google Colab](https://colab.research.google.com/).
2. **Install Dependencies**:
   ```python
   !pip install streamlit julep requests
   !npm install -g localtunnel
   ```
3. **Save the App Code**:
   ```python
   %%writefile main.py
   # Paste the contents of app.py from the latest code
   ```
4. **Run the App**:
   ```python
   import os
   os.system("streamlit run main.py & npx localtunnel --port 8501")
   ```
   - Copy the provided URL (e.g., `https://<your-tunnel>.loca.lt`).
   - Open it in your browser and click “Click to Continue”.
5. **Interact**:
   - Select cities (e.g., Paris, New York) in the sidebar.
   - Click “Generate Foodie Tours”.
   - View results with cards, toggle JSON, and download `foodie_tours.json`.

### Option 2: Run Locally
1. **Create a Directory**:
   ```bash
   mkdir foodie_tour_app
   cd foodie_tour_app
   ```
2. **Save Files**:
   - Save the app code as `app.py` (or `main.py`).
   - Save the requirements as `requirements.txt`:
     ```
     streamlit
     julep
     requests
     ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the App**:
   ```bash
   streamlit run app.py  # or streamlit run main.py
   ```
   - Open `http://localhost:8501` in your browser.
5. **Interact**:
   - Same as above.

## Example Usage
1. **Select Cities**:
   - Choose Paris and New York from the multiselect.
   - Enter a custom city (e.g., London) in the text input input (note: will fail).
2. **Generate Tours**:
   - Click “Generate Foodie Tours”.
   - Wait for results under “Foodie Tour Results”.
3. **View Results**:
   - Each city has an expandable section with:
     - Weather (e.g., “Cloudy, 18.8°C, Indoor dining”).
     - Iconic dishes (e.g., “Croissant, Coq au Vin, Crème Brûlée”).
     - Cards for breakfast, lunch, and dinner.
     - “Toggle Raw JSON” button to show JSON.
   - Errors for unsupported cities (e.g., “Error for London: City not found...”).
4. **Download JSON**:
   - Click “Download Foodie Tours as JSON” to save `foodie_tours.json`.

## Dependencies
- **Python Libraries**:
  - `streamlit`: Web app framework.
  - `julep`: API client for tour generation.
  - `requests`: HTTP requests for weather API.
- **APIs**:
  - Open-Meteo: Weather data.
  - Julep API: Food tour generation (requires key).

## Limitations
- **Custom Cities**: Only supports Paris, New York, and Tokyo due to hardcoded coordinates in `city_coords`. Custom cities trigger errors (to be addressed in Step 6 with geocoding).
- **Performance**: Multi-city generation may be slow due to sequential API calls and a 1-second delay to avoid rate limits.
- **Julep API**: Requires a valid API key and agent configuration.

## Future Steps
- **Step 5**: Validate the JSON output (`foodie_tours.json`) for correctness.
- **Step 6**: Add a geocoding API (e.g., Nominatim) to support custom cities dynamically.

## Troubleshooting
- **Weather API Errors**:
  - Verify the `get_weather` URL uses `current`.
  - Check Open-Meteo API status.
- **Julep API Errors**:
  - Validate agent configuration:
     ```python
     agent = client.agents.get(agent_id)
     print(f"Agent: {agent.name}, Model: {agent.model}, About: {agent.about}")
     ```
   - Ensure API key is valid at [x.ai/api](https://x.ai/api).
- **Streamlit Issues**:
  - Update Streamlit`:
     ```bash
     pip install --upgrade streamlit
     ```
   - Restart the server/tunnel if the app doesn’t load.
- **Contact**: Share error messages, stack traces, or screenshots for debugging.

## Acknowledgments
- **Open-Meteo**: For providing free weather data.
- **Julep**: For enabling food tour generation.
- **Streamlit**: For the intuitive web app framework.

**Created with ❤️ for food lovers** lovers on June 10, 2025.
