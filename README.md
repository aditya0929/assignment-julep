# assignment-julep

## Foodie Tour Generator (JULEP AI) Streamlit App - (view in light theme)

## Overview
This project is a Streamlit web application that generates personalized one-day foodie tours for any city worldwide, tailored to current weather conditions. The app leverages the **Open-Meteo Geocoding API** to fetch coordinates for user-specified cities and the **Open-Meteo Weather API** for real-time weather data, enabling culturally relevant food tours via the **Julep API**. Each tour recommends three iconic dishes and top-rated restaurants for breakfast, lunch, and dinner, presented in a user-friendly interface with card-based visualizations. Users can download tour results as a JSON file for offline use.

Developed in Google Colab and deployed on Streamlit Community Cloud, the project evolved through iterative enhancements, addressing errors, and incorporating user feedback to achieve global city support and a polished UI.
![image](https://github.com/user-attachments/assets/f9706b03-b681-40c9-8567-275e08191969)


## Features
- **Global City Selection**: Choose from predefined cities (e.g., Paris, New York, Tokyo, Delhi, London, Sydney) via a multiselect dropdown or enter any city worldwide through a text input.
- **Dynamic Coordinate Lookup**: Uses Open-Meteo Geocoding API to fetch latitude and longitude for any city, enabling global coverage.
- **Weather-Based Tours**: Retrieves real-time weather data to recommend indoor or outdoor dining based on temperature and conditions.
- **Foodie Tour Generation**: Produces a JSON-formatted tour for each city, including:
  - Weather details (temperature, condition, dining type).
  - Three iconic dishes reflective of the city’s culinary culture.
  - Breakfast, lunch, and dinner recommendations with restaurant names, addresses, dish descriptions, and weather considerations.
- **Card-Based Visualizations**: Displays tours in a clean, responsive layout with custom CSS, using two-column cards for meal details.
- **JSON Output**: Toggles raw JSON display per city via a button and supports downloading all tours as `foodie_tours.json`.
- **Error Handling**: Provides user-friendly warnings for invalid city names (e.g., misspellings) or API failures.
- **Professional UI**: Features a sidebar for city selection, wide layout, custom typography, and a branded footer.

## Development Journey

### Step 1: Core Functionality
- **Objective**: Build functions to fetch weather data and generate foodie tours.
- **Components**:
  - `get_weather(city)`: Initially used hardcoded coordinates for Paris, New York, and Tokyo; later updated to use Open-Meteo Geocoding API for coordinates and Open-Meteo Weather API for temperature and conditions.
  - `generate_foodie_tour(city, weather)`: Integrates Julep API to create a JSON tour based on city and weather inputs.
  - `main_workflow(cities)`: Orchestrates weather retrieval and tour generation for multiple cities.
- **Challenges**:
  - Encountered `400 Bad Request` errors in `get_weather` due to an incorrect URL parameter (`current` vs. `%C2%A4t`).
  - Fixed by correcting the URL:
    ```python
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}¤t=temperature_2m,weathercode&timezone=auto"
    ```
![image](https://github.com/user-attachments/assets/8b3bfed6-4742-4585-9b6f-32356de61f81)

### Step 2: Streamlit Integration
- **Objective**: Develop a Streamlit app for an interactive user experience.
- **Features Added**:
  - Sidebar with multiselect dropdown for predefined cities and text input for custom cities.
  - Main panel with a title, subtitle, and “Generate Foodie Tours” button.
  - Expandable sections for each city’s tour results, including JSON output.
  - Download button for `foodie_tours.json`.
- **Challenges**:
  - Syntax error in an `st.error` line due to an extra quote (`""`).
    - Fixed by correcting:
      ```python
      st.error(f"Error for {result['city']}: {result['error']}")
      ```
  - Reappearance of the `400 Bad Request` error in `get_weather`, resolved by reapplying the URL fix.

### Step 3: UI Enhancements
- **Objective**: Refine the Streamlit app based on user feedback to streamline processing and improve visuals.
- **Changes Made**:
  - **Silent Processing**: Removed debug outputs (`st.write`, `st.spinner`, `st.success`, `st.error`) from core functions, displaying only final results or minimal warnings.
  - **Visualizations**: Implemented card-based layouts for breakfast, lunch, and dinner using `st.columns` and custom CSS:
    - Left column: Restaurant, address, dish, description.
    - Right column: Weather consideration.
  - **Layout Improvements**:
    - Enabled wide layout with `st.set_page_config(layout="wide")`.
    - Added custom CSS for cards, buttons, and typography.
    - Designed a sidebar for city selection and a footer with branding.
  - **JSON Display**: Initially attempted nested expanders for JSON, leading to a `StreamlitAPIException`.

### Step 4: Fixing Nested Expander Error
- **Objective**: Resolve `StreamlitAPIException: Expanders may not be nested inside other expanders`.
- **Issue**: JSON display was nested inside city expanders:
  ```python
  with st.expander(f"Foodie Tour for {city}"):
      with st.expander("View Raw JSON"):
          st.json(result)
  ```
- **Solution**:
  - Replaced the inner expander with a toggle button using `st.session_state`:
    ```python
    if st.button("Toggle Raw JSON", key=f"json_toggle_{city}"):
        st.session_state.show_json[city] = not st.session_state.show_json.get(city, False)
    if st.session_state.show_json.get(city, False):
        st.json(result)
    ```
  - Initialized session state:
    ```python
    if "show_json" not in st.session_state:
        st.session_state.show_json = {}
    ```
- **Outcome**: Eliminated nesting while preserving JSON toggle functionality.

### Step 5: Global City Support
- **Objective**: Enable tours for any city worldwide, overcoming the hardcoded coordinate limitation.
- **Issue**: The app initially supported only Paris, New York, and Tokyo due to a hardcoded `city_coords` dictionary, causing errors for cities like Delhi.
- **Solution**:
  - Integrated Open-Meteo Geocoding API to fetch coordinates dynamically:
    ```python
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    ```
  - Added caching with `@st.cache_data(ttl=86400)` to optimize API calls.
  - Updated the UI with an `st.info` message to clarify global city support.
  - Expanded predefined cities to include Delhi, London, and Sydney as examples.
- **Outcome**: Users can now input any city (e.g., Delhi, Mumbai, Sydney), and the app generates tours seamlessly.

### Step 6: Deployment on Streamlit Community Cloud
- **Objective**: Deploy the app for public access.
- **Steps**:
  - Pushed code to a GitHub repository (`assignment-julep`).
  - Configured Streamlit Cloud to deploy from the repository.
  - Added Julep API key to Streamlit Cloud secrets (see Setup Instructions below).
- **Challenges**:
  - Encountered `KeyError: 'st.secrets has no key "JULEP_API"'` due to a mismatch between `JULEP_API` and `JULEP_API_KEY`.
  - Fixed by updating secrets to use `JULEP_API_KEY` and ensuring `main.py` referenced the correct key.
 
  ![image](https://github.com/user-attachments/assets/07f4a47f-3fa5-422e-8a3e-8a71be739ca4)


## Setup Instructions

### Option 1: Run in Google Colab with LocalTunnel
1. **Open a New Colab Notebook**:
   - Visit [Google Colab](https://colab.research.google.com/).
2. **Install Dependencies**:
   ```python
   !pip install streamlit==1.22.0 julep==2.10.0 requests==2.26.0 anyio==3.6.2 httpx==0.23.0 pydantic==1.10.8 python-dotenv==0.21.0 ruamel-yaml==0.17.21 sniffio==1.3.0 typing-extensions==4.5.0
   !npm install -g localtunnel
   ```
3. **Save the App Code**:
   ```python
   %%writefile main.py
   # Paste the contents of main.py from your repository
   ```
4. **Create Secrets File** (for local testing):
   ```python
   %%writefile .streamlit/secrets.toml
   [general]
   JULEP_API_KEY = "<your_julep_api_key>"
   ```
   - Replace `<your_julep_api_key>` with your actual Julep API key (do not commit this file to GitHub).
5. **Run the App**:
   ```python
   import os
   os.system("streamlit run main.py & npx localtunnel --port 8501")
   ```
   - Copy the provided URL (e.g., `https://<your-tunnel>.loca.lt`).
   - Open it in a browser and click “Click to Continue”.
6. **Interact**:
   - Select cities (e.g., Paris, Delhi) or enter a custom city (e.g., Mumbai).
   - Click “Generate Foodie Tours”.
   - View card-based results, toggle JSON, and download `foodie_tours.json`.

### Option 2: Run Locally
1. **Create a Directory**:
   ```bash
   mkdir foodie_tour_app
   cd foodie_tour_app
   ```
2. **Save Files**:
   - Save the app code as `main.py`.
   - Create `requirements.txt`:
     ```plaintext
     streamlit>=1.22.0
     requests>=2.26.0
     julep==2.10.0
     anyio>=3.6.2
     httpx>=0.23.0
     pydantic>=1.10.8
     python-dotenv>=0.21.0
     ruamel-yaml>=0.17.21
     sniffio>=1.3.0
     typing-extensions>=4.5.0
     ```
   - Create `.streamlit/secrets.toml`:
     ```toml
     [general]
     JULEP_API_KEY = "<your_julep_api_key>"
     ```
     - Replace `<your_julep_api_key>` with your actual Julep API key (do not commit this file to GitHub).
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the App**:
   ```bash
   streamlit run main.py
   ```
   - Open `http://localhost:8501` in a browser.
5. **Interact**:
   - Same as above.

### Option 3: Deploy on Streamlit Community Cloud
1. **Push to GitHub**:
   - Create a repository (e.g., `assignment-julep`).
   - Add files: `main.py`, `requirements.txt`, `.gitignore`, `README.md`.
   - Ensure `.gitignore` includes sensitive files:
     ```plaintext
     .streamlit/secrets.toml
     *.env
     *.pyc
     __pycache__/
     *.DS_Store
     ```
   - Commit and push:
     ```bash
     git add .
     git commit -m "Initial commit with global city support"
     git push origin main
     ```
2. **Configure Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and create a new app.
   - Link to your GitHub repository.
   - Set:
     - Repository: `your-username/assignment-julep`.
     - Branch: `main`.
     - Main file path: `main.py`.
     - Python version: 3.11.
   - Add secrets in the app’s **Settings** > **Secrets**:
     ```toml
     [general]
     JULEP_API_KEY = "<your_julep_api_key>"
     ```
     - Replace `<your_julep_api_key>` with your actual Julep API key.
3. **Deploy**:
   - Click “Deploy” and monitor the logs.
   - Access the app at the provided URL (e.g., `https://assignment-julep.streamlit.app/`).

## Example Usage
1. **Select Cities**:
   - Choose Paris, Delhi, and London from the multiselect dropdown.
   - Enter a custom city (e.g., Sydney) in the text input.
2. **Generate Tours**:
   - Click “Generate Foodie Tours”.
   - View results under “Foodie Tour Results”.
3. **View Results**:
   - Each city has an expandable section with:
     - Weather (e.g., “Cloudy, 18.8°C, Indoor dining”).
     - Iconic dishes (e.g., “Butter Chicken, Chole Bhature, Gulab Jamun” for Delhi).
     - Cards for breakfast, lunch, and dinner with restaurant details.
     - “Toggle Raw JSON” button to display JSON output.
   - Warnings for invalid cities (e.g., “City Delh not found in Open-Meteo database”).
4. **Download JSON**:
   - Click “Download Foodie Tours as JSON” to save `foodie_tours.json`.

## Dependencies
- **Python Libraries**:
  - `streamlit>=1.22.0`: Web app framework.
  - `julep==2.10.0`: API client for tour generation.
  - `requests>=2.26.0`: HTTP requests for Open-Meteo APIs.
  - `anyio>=3.6.2`, `httpx>=0.23.0`, `pydantic>=1.10.8`, `python-dotenv>=0.21.0`, `ruamel-yaml>=0.17.21`, `sniffio>=1.3.0`, `typing-extensions>=4.5.0`: Julep dependencies.
- **APIs**:
  - **Open-Meteo Geocoding API**: Fetches city coordinates (no key required).
  - **Open-Meteo Weather API**: Provides weather data (no key required).
  - **Julep API**: Generates food tours (requires API key).

## Limitations
- **Performance**: Multi-city generation may be slow due to sequential API calls with a 1-second delay to avoid rate limits.
- **City Name Sensitivity**: Open-Meteo Geocoding API may fail for misspelled or ambiguous city names (e.g., “Delh” vs. “Delhi”).
- **Julep API Dependency**: Requires a valid API key and proper agent configuration.

## Future Steps
- **Step 7**: Validate `foodie_tours.json` for correctness and consistency across cities.
- **Step 8**: Optimize performance by batching API calls or reducing delays.
- **Step 9**: Enhance city input with fuzzy matching or autocomplete to handle misspellings.
- **Step 10**: Add support for user preferences (e.g., dietary restrictions) in tour generation.

## Troubleshooting
- **Open-Meteo API Errors**:
  - Verify geocoding and weather URLs:
    ```python
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}¤t=temperature_2m,weathercode&timezone=auto"
    ```
  - Test in a Python environment:
    ```python
    import requests
    city = "Delhi"
    response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json")
    print(response.json())
    ```
  - Check Open-Meteo API status.
- **Julep API Errors**:
  - Validate agent configuration:
    ```python
    agent = client.agents.get(agent_id)
    print(f"Agent: {agent.name}, Model: {agent.model}, About: {agent.about}")
    ```
  - Ensure API key is valid by contacting Julep support at [developers@julep.ai](mailto:developers@julep.ai).
- **Streamlit Issues**:
  - Update Streamlit:
    ```bash
    pip install --upgrade streamlit
    ```
  - Restart the server or tunnel if the app doesn’t load.
  - Check deployment logs in Streamlit Cloud for errors.
- **Contact**: Share error messages, stack traces, or screenshots on the [Streamlit Community Forum](https://discuss.streamlit.io/) for assistance.
