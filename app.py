import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.8rem;
        background-color: rgba(30, 30, 30, 0.7) !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 0.8rem;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
        border: none;
    }
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 1rem;
        border-radius: 0.8rem;
        color: #FFFFFF;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="metric-container"] label {
        color: #9E9E9E;
    }
    div[data-testid="metric-container"] div {
        color: #FFFFFF;
    }
    div[data-testid="stExpander"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        border-radius: 0.8rem;
        padding: 1rem;
    }
    .stMarkdown {
        color: #FFFFFF;
    }
    div[data-testid="stText"] {
        color: #FFFFFF;
    }
    .stTextInput>div>div {
        background-color: #1E1E1E;
        color: #FFFFFF;
        border-radius: 0.8rem;
    }
    .stTextInput>label {
        color: #FFFFFF;
    }
    div[data-testid="stHeader"] {
        background-color: transparent;
    }
    .plot-container {
        background-color: #1E1E1E;
        border-radius: 0.8rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def get_weather_data(city_name):
    """Fetch weather data from OpenWeatherMap API"""
    API_KEY = os.getenv('API_KEY')
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    try:
        response = requests.get(BASE_URL, params={
            "q": city_name,
            "appid": API_KEY,
            "units": "metric"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"❌ Error: City not found or invalid API key")
        return None
    except Exception as err:
        st.error(f"❌ An error occurred: {err}")
        return None

def create_temperature_gauge(temp, feels_like):
    """Create a temperature gauge visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=temp,
        delta={"reference": feels_like, "valueformat": ".1f"},
        title={"text": "Temperature (°C)", "font": {"color": "#FFFFFF"}},
        gauge={
            "axis": {"range": [-20, 50], "tickcolor": "#FFFFFF"},
            "bar": {"color": "#4CAF50"},
            "bgcolor": "rgba(30, 30, 30, 0.8)",
            "borderwidth": 2,
            "bordercolor": "#333",
            "steps": [
                {"range": [-20, 0], "color": "#1E88E5"},
                {"range": [0, 20], "color": "#FFC107"},
                {"range": [20, 50], "color": "#FF5722"}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(30, 30, 30, 0.8)',
        plot_bgcolor='rgba(30, 30, 30, 0.8)',
        font={'color': "#FFFFFF"},
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

def main():
    # Header with custom styling
    st.markdown("""
        <h1 style='text-align: center; color: #FFFFFF; margin-bottom: 2rem;'>
            🌤️ Weather Dashboard
        </h1>
    """, unsafe_allow_html=True)
    
    # City input
    col1, col2 = st.columns([3, 1])
    with col1:
        city = st.text_input(
            "Enter City Name",
            "London",
            help="Type the name of the city you want to check the weather for"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        search_clicked = st.button("Get Weather", type="primary")

    if search_clicked and city:
        data = get_weather_data(city)
        
        if data:
            # Display current time
            st.markdown(f"""
                <h3 style='text-align: center; color: #FFFFFF;'>
                    Weather in {city.title()}
                </h3>
                <p style='text-align: center; color: #9E9E9E;'>
                    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            """, unsafe_allow_html=True)
            
            # Create three columns for weather info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Temperature",
                    f"{data['main']['temp']}°C",
                    f"Feels like {data['main']['feels_like']}°C",
                    delta_color="off"
                )
                
            with col2:
                st.metric(
                    "Humidity",
                    f"{data['main']['humidity']}%",
                    delta_color="off"
                )
                
            with col3:
                st.metric(
                    "Wind Speed",
                    f"{data['wind']['speed']} m/s",
                    delta_color="off"
                )
            
            # Weather condition
            st.info(
                f"**Current Conditions:** {data['weather'][0]['description'].title()}"
            )
            
            # Temperature gauge
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            st.plotly_chart(
                create_temperature_gauge(
                    data['main']['temp'],
                    data['main']['feels_like']
                ),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional weather details
            with st.expander("📊 See More Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**🌡️ Pressure:**", f"{data['main']['pressure']} hPa")
                    st.write("**👁️ Visibility:**", f"{data.get('visibility', 'N/A')} meters")
                with col2:
                    st.write("**☁️ Cloudiness:**", f"{data['clouds']['all']}%")
                    if 'rain' in data:
                        st.write("**🌧️ Rain (1h):**", f"{data['rain'].get('1h', 0)} mm")

if __name__ == "__main__":
    main()
