import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import heapq
import random
from tkinter import Toplevel, Label
from PIL import Image, ImageTk
from tkinter import Toplevel, Canvas, Scrollbar, Frame


class Heap:
    def __init__(self):
        self.heap = []
        self.node_positions = {}

    def add(self, node, distance):
        heapq.heappush(self.heap, (distance, node))
        self.node_positions[node] = distance

    def remove(self):
        distance, node = heapq.heappop(self.heap)
        del self.node_positions[node]
        return node, distance

    def update(self, node, new_distance):
        for i in range(len(self.heap)):
            if self.heap[i][1] == node:
                self.heap[i] = (new_distance, node)
                heapq.heapify(self.heap)
                break
        self.node_positions[node] = new_distance

    def is_empty(self):
        return len(self.heap) == 0


class RealTimeData:
    def __init__(self):
        self.station_status = {
            "0": {"name": "Shaheed Sthal", "dist": 0.0},
            "1": {"name": "Hindon River", "dist": 1.0},
            "2": {"name": "Arthala", "dist": 2.5},
        }

        self.train_arrivals = {
            "Shaheed Sthal": random.randint(1, 10),
            "Hindon River": random.randint(1, 10),
            "Arthala": random.randint(1, 10),
        }

    def get_station_status(self, station):
        return self.station_status.get(station, "No Data Available")

    def get_train_arrival(self, station):
        return self.train_arrivals.get(station, "No Data Available")


def apply_modern_theme():
    style = ttk.Style()
    style.theme_use("clam")

    colors = {
        "primary": "#004d99",
        "secondary": "#0073e6",
        "accent": "#e60000",
        "background": "#f2f2f2",
        "surface": "#ffffff",
        "text": "#333333",
        "text_secondary": "#666666",
    }

    style.configure("TFrame", background=colors["background"])
    style.configure(
        "TLabel",
        background=colors["background"],
        foreground=colors["text"],
        font=("Arial", 10),
    )
    style.configure(
        "TButton",
        background=colors["primary"],
        foreground="white",
        font=("Arial", 10, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", colors["secondary"])],
        foreground=[("active", "white")],
    )
    style.configure("TNotebook", background=colors["background"])
    style.configure(
        "TNotebook.Tab",
        background=colors["surface"],
        foreground=colors["text"],
        padding=[10, 5],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", colors["primary"])],
        foreground=[("selected", "white")],
    )

    return style, colors


class MetroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Delhi Metro Route Planner")
        self.root.geometry("900x700")

        self.style, self.colors = apply_modern_theme()
        self.root.configure(bg=self.colors["background"])

        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            main_frame,
            text="Delhi Metro Route Planner",
            font=("Arial", 24, "bold"),
            foreground=self.colors["primary"],
        )
        header.pack(pady=(0, 20))

        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(expand=True, fill="both")

        self.distance_tracking_frame = ttk.Frame(
            self.tab_control, padding="20 20 20 20"
        )
        self.ticket_booking_frame = ttk.Frame(self.tab_control, padding="20 20 20 20")

        self.tab_control.add(self.distance_tracking_frame, text="Route Planning")
        self.tab_control.add(self.ticket_booking_frame, text="Ticket Booking")

        self.initialize_distance_tracking_tab()
        self.initialize_ticket_booking_tab()

        self.map_button = ttk.Button(
            main_frame,
            text="Show Delhi Metro Map",
            command=self.show_delhi_metro_map,
            style="Accent.TButton",
        )
        self.map_button.pack(pady=20)

        self.metro_graph = self.create_graph()

    def initialize_distance_tracking_tab(self):
        ttk.Label(self.distance_tracking_frame, text="Source Station:").grid(
            row=0, column=0, padx=10, pady=10, sticky="W"
        )
        self.source_entry = ttk.Entry(self.distance_tracking_frame, width=30)
        self.source_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.distance_tracking_frame, text="Destination Station:").grid(
            row=1, column=0, padx=10, pady=10, sticky="W"
        )
        self.destination_entry = ttk.Entry(self.distance_tracking_frame, width=30)
        self.destination_entry.grid(row=1, column=1, padx=10, pady=10)

        calculate_button = ttk.Button(
            self.distance_tracking_frame,
            text="Calculate Route & Fare",
            command=self.calculate_route,
        )
        calculate_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.result_label = ttk.Label(self.distance_tracking_frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=10)

    def initialize_ticket_booking_tab(self):
        ttk.Label(
            self.ticket_booking_frame, text="Enter Your Details to Book Ticket:"
        ).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self.ticket_booking_frame, text="Name:").grid(
            row=1, column=0, padx=10, pady=10, sticky="W"
        )
        self.name_entry = ttk.Entry(self.ticket_booking_frame, width=30)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.ticket_booking_frame, text="Phone Number:").grid(
            row=2, column=0, padx=10, pady=10, sticky="W"
        )
        self.phone_entry = ttk.Entry(self.ticket_booking_frame, width=30)
        self.phone_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.ticket_booking_frame, text="Email:").grid(
            row=3, column=0, padx=10, pady=10, sticky="W"
        )
        self.email_entry = ttk.Entry(self.ticket_booking_frame, width=30)
        self.email_entry.grid(row=3, column=1, padx=10, pady=10)

        self.book_button = ttk.Button(
            self.ticket_booking_frame,
            text="Book Ticket",
            command=self.book_ticket,
            state=tk.DISABLED,
        )
        self.book_button.grid(row=4, column=0, columnspan=2, pady=20)

    def show_delhi_metro_map(self):
        try:
            map_window = Toplevel(self.root)
            map_window.title("Delhi Metro Map")
            map_window.geometry("1000x800")

            canvas = Canvas(map_window, bg="white")
            canvas.pack(side="left", fill="both", expand=True)

            x_scroll = Scrollbar(map_window, orient="horizontal", command=canvas.xview)
            y_scroll = Scrollbar(map_window, orient="vertical", command=canvas.yview)
            x_scroll.pack(side="bottom", fill="x")
            y_scroll.pack(side="right", fill="y")
            canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

            img = Image.open("delhi_metro_map.jpeg")
            map_img = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=map_img, anchor="nw")
            canvas.image = map_img
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load map: {e}")

    def create_graph(self):
        graph = {
            "Shaheed Sthal (New Bus Adda)": {"Hindon River": 1.0},
            "Hindon River": {"Shaheed Sthal (New Bus Adda)": 1.0, "Arthala": 1.5},
            "Arthala": {"Hindon River": 1.5, "Mohan Nagar": 0.7},
            "Mohan Nagar": {"Arthala": 0.7, "Shyam Park": 1.3},
            "Shyam Park": {
                "Mohan Nagar": 1.3,
                "Major Mohit Sharma Rajendra Nagar": 1.2,
            },
            "Major Mohit Sharma Rajendra Nagar": {"Shyam Park": 1.2, "Raj Bagh": 1.2},
            "Raj Bagh": {
                "Major Mohit Sharma Rajendra Nagar": 1.2,
                "Shaheed Nagar": 1.3,
            },
            "Shaheed Nagar": {"Raj Bagh": 1.3, "Dilshad Garden": 1.2},
            "Dilshad Garden": {"Shaheed Nagar": 1.2, "Jhil mil": 0.9},
            "Jhil mil": {"Dilshad Garden": 0.9, "Mansarovar Park": 1.1},
            "Mansarovar Park": {"Jhil mil": 1.1},
        }

    def calculate_route(self):
        source = self.source_entry.get()
        destination = self.destination_entry.get()

        if source not in self.metro_graph or destination not in self.metro_graph:
            messagebox.showerror("Error", "Invalid source or destination station.")
            return

        path, distance = self.dijkstra(source, destination)

        if path is None:
            self.result_label.config(text="No route found.")
        else:
            fare = self.calculate_fare(distance)
            path_str = " -> ".join(path)
            self.result_label.config(
                text=f"Shortest path: {path_str}\nTotal distance: {distance} km\nTotal fare: {fare} INR"
            )
            self.book_button.config(state=tk.NORMAL)

    def dijkstra(self, start, end):
        distances = {station: float("inf") for station in self.metro_graph}
        previous_stations = {station: None for station in self.metro_graph}
        distances[start] = 0
        queue = [(0, start)]

        while queue:
            current_distance, current_station = heapq.heappop(queue)

            if current_station == end:
                path = []
                while current_station is not None:
                    path.append(current_station)
                    current_station = previous_stations[current_station]
                path.reverse()
                return path, distances[end]

            if current_distance > distances[current_station]:
                continue

            for neighbor, weight in self.metro_graph[current_station].items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_stations[neighbor] = current_station
                    heapq.heappush(queue, (distance, neighbor))

        return None, None

    def calculate_fare(self, distance):
        fare_rate = 10
        return round(distance * fare_rate, 2)

    def update_real_time_data(self):
        station = self.source_entry.get()
        if station and station in self.metro_graph:
            self.station_status_label.config(text=f"Station Status ({station}): Open")
            self.arrival_label.config(
                text=f"Train Arrival at {station}: {random.randint(1, 10)} min"
            )

        disruptions = self.get_disruptions()
        disruption_text = "\n".join(
            [f"{station}: {disruption}" for station, disruption in disruptions.items()]
        )
        self.disruptions_label.config(text=f"Service Disruptions:\n{disruption_text}")

        self.root.after(10000, self.update_real_time_data)

    def get_disruptions(self):
        return {
            "Mohan Nagar": "Line 1 delayed",
            "Dilshad Garden": "Maintenance ongoing",
        }

    def book_ticket(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()

        if not name or not phone or not email:
            messagebox.showerror(
                "Error", "Please enter your name, phone number, and email."
            )
            return

        booking_info = (
            f"Name: {name}\nPhone: {phone}\nEmail: {email}\n"
            f"Source: {self.source_entry.get()}\nDestination: {self.destination_entry.get()}\n"
            f"Fare: {self.result_label.cget('text').split('\\n')[-1]}"
        )

        messagebox.showinfo(
            "Booking Confirmation", f"Ticket booked successfully!\n\n{booking_info}"
        )
        self.book_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = MetroApp(root)
    root.mainloop()
