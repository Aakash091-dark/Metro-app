import streamlit as st
import heapq
import random
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
from datetime import datetime, timedelta

class MetroGraph:
    def __init__(self):
        self.graph = {
            "Shaheed Sthal": {"Hindon River": 1.0},
            "Hindon River": {"Shaheed Sthal": 1.0, "Arthala": 1.5},
            "Arthala": {"Hindon River": 1.5, "Mohan Nagar": 0.7},
            "Mohan Nagar": {"Arthala": 0.7, "Shyam Park": 1.3},
            "Shyam Park": {"Mohan Nagar": 1.3, "Major Mohit Sharma": 1.2},
            "Major Mohit Sharma": {"Shyam Park": 1.2, "Raj Bagh": 1.2},
            "Raj Bagh": {"Major Mohit Sharma": 1.2, "Shaheed Nagar": 1.3},
            "Shaheed Nagar": {"Raj Bagh": 1.3, "Dilshad Garden": 1.2},
            "Dilshad Garden": {"Shaheed Nagar": 1.2, "Jhil mil": 0.9},
            "Jhil mil": {"Dilshad Garden": 0.9, "Mansarovar Park": 1.1},
            "Mansarovar Park": {"Jhil mil": 1.1}
        }
        
        # Station coordinates (approximate values for Delhi metro stations)
        self.station_coords = {
            "Shaheed Sthal": (28.6725, 77.3718),
            "Hindon River": (28.6789, 77.3657),
            "Arthala": (28.6853, 77.3596),
            "Mohan Nagar": (28.6917, 77.3535),
            "Shyam Park": (28.6981, 77.3474),
            "Major Mohit Sharma": (28.7045, 77.3413),
            "Raj Bagh": (28.7109, 77.3352),
            "Shaheed Nagar": (28.7173, 77.3291),
            "Dilshad Garden": (28.7237, 77.3230),
            "Jhil mil": (28.7301, 77.3169),
            "Mansarovar Park": (28.7365, 77.3108)
        }

    def get_stations(self):
        return list(self.graph.keys())

    def dijkstra(self, start, end):
        distances = {station: float('inf') for station in self.graph}
        previous = {station: None for station in self.graph}
        distances[start] = 0
        pq = [(0, start)]
        
        while pq:
            current_distance, current_station = heapq.heappop(pq)
            
            if current_distance > distances[current_station]:
                continue
                
            if current_station == end:
                break
                
            for neighbor, weight in self.graph[current_station].items():
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_station
                    heapq.heappush(pq, (distance, neighbor))
        
        if distances[end] == float('inf'):
            return None, None
            
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]

def calculate_fare(distance):
    base_fare = 10
    per_km_charge = 2
    return base_fare + (distance * per_km_charge)

def generate_ticket_qr():
    # Placeholder for QR code generation
    return "QR_CODE_DATA"

def create_route_map(metro_graph, path):
    m = folium.Map(location=[28.7041, 77.3025], zoom_start=12)
    
    # Plot all stations
    for station, coords in metro_graph.station_coords.items():
        color = 'red' if station in path else 'blue'
        folium.CircleMarker(
            coords,
            radius=8,
            color=color,
            fill=True,
            popup=station
        ).add_to(m)
    
    # Plot route
    if path:
        route_coords = []
        for i in range(len(path)-1):
            start = metro_graph.station_coords[path[i]]
            end = metro_graph.station_coords[path[i+1]]
            route_coords.extend([start, end])
            folium.PolyLine(
                locations=[start, end],
                weight=4,
                color='red',
            ).add_to(m)
    
    return m

def main():
    st.set_page_config(page_title="Delhi Metro Route Planner", layout="wide")
    
    # Initialize session state
    if 'metro_graph' not in st.session_state:
        st.session_state.metro_graph = MetroGraph()
    if 'booking_history' not in st.session_state:
        st.session_state.booking_history = []

    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🚇 Delhi Metro Route Planner")
    
    # Sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Route Planning", "Ticket Booking", "Real-time Updates"])
    
    if page == "Route Planning":
        st.header("Plan Your Journey")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.selectbox("Select Source Station", st.session_state.metro_graph.get_stations())
            destination = st.selectbox("Select Destination Station", st.session_state.metro_graph.get_stations())
            
            if st.button("Find Route"):
                path, distance = st.session_state.metro_graph.dijkstra(source, destination)
                
                if path:
                    fare = calculate_fare(distance)
                    st.success("Route Found!")
                    st.write(f"🛤️ Path: {' → '.join(path)}")
                    st.write(f"📏 Distance: {distance:.2f} km")
                    st.write(f"💰 Estimated Fare: ₹{fare:.2f}")
                    
                    # Store route details in session state
                    st.session_state.current_route = {
                        'path': path,
                        'distance': distance,
                        'fare': fare
                    }
                else:
                    st.error("No route found between selected stations.")
        
        with col2:
            # Display route on map
            if 'current_route' in st.session_state:
                route_map = create_route_map(st.session_state.metro_graph, st.session_state.current_route['path'])
                folium_static(route_map)
    
    elif page == "Ticket Booking":
        st.header("Book Your Ticket")
        
        if 'current_route' not in st.session_state:
            st.warning("Please plan your route first!")
            return
            
        with st.form("booking_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            journey_date = st.date_input("Journey Date")
            
            submitted = st.form_submit_button("Book Ticket")
            
            if submitted:
                if name and email and phone:
                    # Create booking
                    booking = {
                        'booking_id': f"METRO{random.randint(10000,99999)}",
                        'name': name,
                        'source': st.session_state.current_route['path'][0],
                        'destination': st.session_state.current_route['path'][-1],
                        'fare': st.session_state.current_route['fare'],
                        'date': journey_date.strftime("%Y-%m-%d"),
                        'qr_code': generate_ticket_qr()
                    }
                    
                    st.session_state.booking_history.append(booking)
                    
                    # Display booking confirmation
                    st.success("Ticket Booked Successfully!")
                    st.json(booking)
                else:
                    st.error("Please fill all required fields!")
    
    else:  # Real-time Updates
        st.header("Real-time Metro Updates")
        
        # Simulated real-time data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Station Status")
            status_df = pd.DataFrame({
                'Station': st.session_state.metro_graph.get_stations(),
                'Status': ['Operational'] * len(st.session_state.metro_graph.get_stations()),
                'Next Train': [f"{random.randint(1,10)} mins" for _ in range(len(st.session_state.metro_graph.get_stations()))]
            })
            st.dataframe(status_df)
        
        with col2:
            st.subheader("Service Alerts")
            alerts = [
                "Minor delays on Red Line due to technical issue",
                "Normal service on all other lines",
                "Maintenance work scheduled for tonight"
            ]
            for alert in alerts:
                st.info(alert)
        
        # Crowd density heat map
        st.subheader("Station Crowd Density")
        stations = st.session_state.metro_graph.get_stations()
        crowd_data = [random.randint(20, 100) for _ in stations]
        
        fig = go.Figure(data=[go.Bar(x=stations, y=crowd_data)])
        fig.update_layout(
            title="Current Station Crowd Levels",
            xaxis_title="Stations",
            yaxis_title="Crowd Density (%)"
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()