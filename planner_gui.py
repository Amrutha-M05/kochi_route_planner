import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Dict, List
import sys
import webbrowser
import folium
import os
from pathlib import Path

# Import from your main dijkstra.py file
try:
    from dijkstra import LocationToLocationOptimizer
except ImportError:
    print("Error: Make sure dijkstra.py is in the same directory")
    sys.exit(1)

class LocationRouteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kochi Location-to-Location Route Optimizer with Maps")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f2f5')
        
        # Initialize the optimizer
        print("Initializing network... (this may take a moment)")
        self.optimizer = LocationToLocationOptimizer()
        print("Network initialized successfully!")
        
        # Variables
        self.start_location_var = tk.StringVar()
        self.end_location_var = tk.StringVar()
        self.current_routes = None
        self.current_start = None
        self.current_end = None
        
        # Available locations
        self.all_locations = sorted(list(self.optimizer.locations.keys()))
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Setup custom styles for the GUI"""
        style = ttk.Style()
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       foreground='#2c3e50',
                       background='#f0f2f5')
        
        style.configure('Section.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#34495e',
                       background='#ffffff')
        
        style.configure('Info.TLabel',
                       font=('Segoe UI', 9),
                       foreground='#7f8c8d',
                       background='#ffffff')
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel - Input controls
        self.create_input_panel(content_frame)
        
        # Right panel - Results
        self.create_results_panel(content_frame)
        
    def create_header(self, parent):
        """Create the header section"""
        header_frame = tk.Frame(parent, bg='#3498db', height=120)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame,
                              text="Kochi Route Planner",
                              font=('Segoe UI', 28, 'bold'),
                              fg='white',
                              bg='#3498db')
        title_label.pack(pady=(15, 5))
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Find optimized routes with interactive map visualization",
                                 font=('Segoe UI', 12),
                                 fg='white',
                                 bg='#3498db')
        subtitle_label.pack()
        
        # Info label
        info_label = tk.Label(header_frame,
                            text="✓ Multi-modal routing  |  ✓ Multiple alternatives  |  ✓ Interactive maps  |  ✓ Google Maps integration",
                            font=('Segoe UI', 10),
                            fg='#ecf0f1',
                            bg='#3498db')
        info_label.pack(pady=(5, 0))
        
    def create_input_panel(self, parent):
        """Create the input controls panel"""
        input_frame = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        input_frame.pack(side='left', fill='y', padx=(0, 10), ipadx=15, ipady=15)
        
        # Title
        title = tk.Label(input_frame,
                        text="📍 Route Planning",
                        font=('Segoe UI', 16, 'bold'),
                        bg='white',
                        fg='#2c3e50')
        title.pack(anchor='w', pady=(0, 20))
        
        # Starting location
        start_frame = tk.Frame(input_frame, bg='white')
        start_frame.pack(fill='x', pady=(0, 20))
        
        start_label = tk.Label(start_frame,
                              text="Starting Location",
                              font=('Segoe UI', 11, 'bold'),
                              bg='white',
                              fg='#34495e')
        start_label.pack(anchor='w')
        
        # Searchable combobox for start
        self.start_combo = ttk.Combobox(start_frame,
                                       textvariable=self.start_location_var,
                                       values=self.all_locations,
                                       width=35,
                                       font=('Segoe UI', 10))
        self.start_combo.pack(fill='x', pady=(5, 0))
        self.start_combo.set("Search or select starting location...")
        
        # Bind for autocomplete
        self.start_combo.bind('<KeyRelease>', lambda e: self.autocomplete(e, self.start_combo, self.start_location_var))
        
        # Info about location types
        start_info = tk.Label(start_frame,
                            text="Includes metro stations, malls, hospitals, and more",
                            font=('Segoe UI', 8),
                            fg='#95a5a6',
                            bg='white')
        start_info.pack(anchor='w', pady=(3, 0))
        
        # Destination location
        dest_frame = tk.Frame(input_frame, bg='white')
        dest_frame.pack(fill='x', pady=(0, 20))
        
        dest_label = tk.Label(dest_frame,
                             text="Destination",
                             font=('Segoe UI', 11, 'bold'),
                             bg='white',
                             fg='#34495e')
        dest_label.pack(anchor='w')
        
        self.dest_combo = ttk.Combobox(dest_frame,
                                      textvariable=self.end_location_var,
                                      values=self.all_locations,
                                      width=35,
                                      font=('Segoe UI', 10))
        self.dest_combo.pack(fill='x', pady=(5, 0))
        self.dest_combo.set("Search or select destination...")
        
        # Bind for autocomplete
        self.dest_combo.bind('<KeyRelease>', lambda e: self.autocomplete(e, self.dest_combo, self.end_location_var))
        
        dest_info = tk.Label(dest_frame,
                           text="Choose from 40+ locations across Kochi",
                           font=('Segoe UI', 8),
                           fg='#95a5a6',
                           bg='white')
        dest_info.pack(anchor='w', pady=(3, 0))
        
        # Quick location filters
        filter_frame = tk.Frame(input_frame, bg='white')
        filter_frame.pack(fill='x', pady=(0, 20))
        
        filter_label = tk.Label(filter_frame,
                               text="Quick Filters",
                               font=('Segoe UI', 10, 'bold'),
                               bg='white',
                               fg='#34495e')
        filter_label.pack(anchor='w', pady=(0, 8))
        
        filter_buttons = tk.Frame(filter_frame, bg='white')
        filter_buttons.pack(fill='x')
        
        filters = [
            ("🚇 Metro", "metro"),
            ("🏢 Malls", "mall"),
            ("🏥 Hospital", "hospital"),
            ("🎓 Education", "educational")
        ]
        
        for i, (text, filter_type) in enumerate(filters):
            btn = tk.Button(filter_buttons,
                          text=text,
                          font=('Segoe UI', 8),
                          bg='#ecf0f1',
                          fg='#2c3e50',
                          relief='flat',
                          padx=5,
                          pady=3,
                          cursor='hand2',
                          command=lambda ft=filter_type: self.filter_locations(ft))
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='ew')
        
        filter_buttons.columnconfigure(0, weight=1)
        filter_buttons.columnconfigure(1, weight=1)
        
        # Swap button
        swap_btn = tk.Button(input_frame,
                           text="⇅ Swap Start ↔ End",
                           font=('Segoe UI', 10),
                           bg='#95a5a6',
                           fg='white',
                           relief='flat',
                           padx=15,
                           pady=8,
                           cursor='hand2',
                           command=self.swap_locations)
        swap_btn.pack(fill='x', pady=(0, 20))
        
        # Calculate button
        self.calculate_btn = tk.Button(input_frame,
                                      text="🔍 Find Optimal Routes",
                                      font=('Segoe UI', 14, 'bold'),
                                      bg='#27ae60',
                                      fg='white',
                                      relief='flat',
                                      padx=20,
                                      pady=15,
                                      cursor='hand2',
                                      command=self.calculate_routes)
        self.calculate_btn.pack(fill='x')
        
        # Map buttons section
        map_section = tk.Frame(input_frame, bg='#f0f8ff', relief='solid', borderwidth=1)
        map_section.pack(fill='x', pady=(20, 0))
        
        map_title = tk.Label(map_section,
                            text="🗺️ Map Visualization",
                            font=('Segoe UI', 11, 'bold'),
                            bg='#f0f8ff',
                            fg='#2c3e50')
        map_title.pack(pady=(10, 5))
        
        # Interactive Map button
        self.view_map_btn = tk.Button(map_section,
                                     text="📍 View Route on Interactive Map",
                                     font=('Segoe UI', 10, 'bold'),
                                     bg='#3498db',
                                     fg='white',
                                     relief='flat',
                                     padx=15,
                                     pady=10,
                                     cursor='hand2',
                                     state='disabled',
                                     command=self.show_interactive_map)
        self.view_map_btn.pack(fill='x', padx=10, pady=(0, 5))
        
        # Google Maps button
        self.gmaps_btn = tk.Button(map_section,
                                  text="🌍 Open in Google Maps",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#e74c3c',
                                  fg='white',
                                  relief='flat',
                                  padx=15,
                                  pady=10,
                                  cursor='hand2',
                                  state='disabled',
                                  command=self.open_google_maps)
        self.gmaps_btn.pack(fill='x', padx=10, pady=(0, 10))
        
        # Statistics
        stats_frame = tk.Frame(input_frame, bg='#f8f9fa', relief='solid', borderwidth=1)
        stats_frame.pack(fill='x', pady=(20, 0))
        
        stats_title = tk.Label(stats_frame,
                              text="Network Statistics",
                              font=('Segoe UI', 9, 'bold'),
                              bg='#f8f9fa',
                              fg='#2c3e50')
        stats_title.pack(pady=(8, 5))
        
        total_locs = len(self.optimizer.locations)
        metro_count = len([l for l, d in self.optimizer.locations.items() 
                          if d['type'] == 'metro_station'])
        
        stats_text = f"""Total Locations: {total_locs}
Metro Stations: {metro_count}
Other Locations: {total_locs - metro_count}
Transport Modes: 4 (Metro, Bus, Auto, Walk)"""
        
        stats_label = tk.Label(stats_frame,
                              text=stats_text,
                              font=('Segoe UI', 8),
                              bg='#f8f9fa',
                              fg='#7f8c8d',
                              justify='left')
        stats_label.pack(pady=(0, 8), padx=10)
        
    def create_results_panel(self, parent):
        """Create the results display panel"""
        results_frame = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        results_frame.pack(side='right', fill='both', expand=True)
        
        # Results header
        header_frame = tk.Frame(results_frame, bg='#ecf0f1')
        header_frame.pack(fill='x')
        
        self.results_header = tk.Label(header_frame,
                                      text="Select locations and click 'Find Optimal Routes' to begin",
                                      font=('Segoe UI', 13, 'bold'),
                                      bg='#ecf0f1',
                                      fg='#34495e',
                                      pady=15)
        self.results_header.pack()
        
        # Scrollable results area
        scroll_frame = tk.Frame(results_frame, bg='white')
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.results_canvas = tk.Canvas(scroll_frame,
                                       bg='white',
                                       highlightthickness=0,
                                       yscrollcommand=scrollbar.set)
        self.results_canvas.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=self.results_canvas.yview)
        
        # Frame inside canvas
        self.results_container = tk.Frame(self.results_canvas, bg='white')
        self.canvas_frame = self.results_canvas.create_window((0, 0),
                                                               window=self.results_container,
                                                               anchor='nw')
        
        # Bind canvas resize
        self.results_container.bind('<Configure>',
                                   lambda e: self.results_canvas.configure(
                                       scrollregion=self.results_canvas.bbox('all')))
        
        # Bind mousewheel scrolling
        self.results_canvas.bind('<Enter>', self._bind_mousewheel)
        self.results_canvas.bind('<Leave>', self._unbind_mousewheel)
        
        # Initial welcome message
        welcome_frame = tk.Frame(self.results_container, bg='white')
        welcome_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        welcome_icon = tk.Label(welcome_frame,
                               text="🗺️",
                               font=('Segoe UI', 72),
                               bg='white')
        welcome_icon.pack()
        
        welcome_text = tk.Label(welcome_frame,
                               text="Welcome to Kochi Route Optimizer!",
                               font=('Segoe UI', 16, 'bold'),
                               bg='white',
                               fg='#2c3e50')
        welcome_text.pack(pady=(10, 5))
        
        instructions = tk.Label(welcome_frame,
                               text="1. Select your starting location\n"
                                    "2. Choose your destination\n"
                                    "3. Click 'Find Optimal Routes'\n"
                                    "4. View routes on interactive maps",
                               font=('Segoe UI', 11),
                               bg='white',
                               fg='#7f8c8d',
                               justify='center')
        instructions.pack(pady=10)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(results_frame, mode='indeterminate')
    
    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas scrolling"""
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbind_mousewheel(self, event):
        """Unbind mousewheel from canvas"""
        self.results_canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.results_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def autocomplete(self, event, combobox, var):
        """Autocomplete for location search"""
        typed = var.get().lower()
        
        if typed == '' or typed == "search or select starting location..." or typed == "search or select destination...":
            combobox['values'] = self.all_locations
        else:
            matches = [loc for loc in self.all_locations if typed in loc.lower()]
            combobox['values'] = matches
    
    def filter_locations(self, location_type):
        """Filter locations by type"""
        filtered = []
        
        type_map = {
            'metro': 'metro_station',
            'mall': 'mall',
            'hospital': 'hospital',
            'educational': 'educational'
        }
        
        target_type = type_map.get(location_type, location_type)
        
        for loc, data in self.optimizer.locations.items():
            if data['type'] == target_type:
                filtered.append(loc)
        
        filtered = sorted(filtered)
        
        if filtered:
            self.start_combo['values'] = filtered
            self.dest_combo['values'] = filtered
            
            messagebox.showinfo("Filter Applied",
                              f"Showing {len(filtered)} locations of type: {location_type}\n"
                              f"Select a different filter or restart to show all locations.")
        else:
            messagebox.showwarning("No Results", 
                                 f"No locations found for type: {location_type}")
    
    def reset_filters(self):
        """Reset location filters"""
        self.start_combo['values'] = self.all_locations
        self.dest_combo['values'] = self.all_locations
    
    def swap_locations(self):
        """Swap start and end locations"""
        start = self.start_location_var.get()
        end = self.end_location_var.get()
        
        self.start_location_var.set(end)
        self.end_location_var.set(start)
    
    def validate_inputs(self):
        """Validate user inputs"""
        start = self.start_location_var.get()
        end = self.end_location_var.get()
        
        if not start or start == "Search or select starting location...":
            messagebox.showerror("Error", "Please select a starting location")
            return False
        
        if not end or end == "Search or select destination...":
            messagebox.showerror("Error", "Please select a destination")
            return False
        
        if start not in self.optimizer.locations:
            messagebox.showerror("Error", f"Starting location '{start}' not found")
            return False
        
        if end not in self.optimizer.locations:
            messagebox.showerror("Error", f"Destination '{end}' not found")
            return False
        
        if start == end:
            messagebox.showwarning("Warning", "Start and destination are the same!")
            return False
        
        return True
    
    def calculate_routes(self):
        """Calculate and display routes"""
        if not self.validate_inputs():
            return
        
        # Disable button
        self.calculate_btn.config(state='disabled', text="Calculating...")
        self.view_map_btn.config(state='disabled')
        self.gmaps_btn.config(state='disabled')
        self.progress.pack(fill='x', padx=10, pady=10)
        self.progress.start()
        
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        self.results_header.config(text="Calculating optimal routes...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._calculate_routes_thread)
        thread.daemon = True
        thread.start()
    
    def _calculate_routes_thread(self):
        """Thread function for route calculation"""
        try:
            start = self.start_location_var.get()
            end = self.end_location_var.get()
            
            # Calculate routes
            routes = self.optimizer.find_optimized_routes(start, end)
            
            # Update GUI in main thread
            self.root.after(0, self._display_results, start, end, routes)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _display_results(self, start, end, routes):
        """Display calculation results"""
        # Stop progress
        self.progress.stop()
        self.progress.pack_forget()
        self.calculate_btn.config(state='normal', text="🔍 Find Optimal Routes")
        
        # Update header
        self.results_header.config(text=f"Routes: {start} → {end}")
        
        # Clear container
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        if not routes or (isinstance(routes, list) and len(routes) > 0 and 'error' in routes[0]):
            error_msg = routes[0].get('error', 'No routes found') if routes else 'No routes found'
            error_frame = tk.Frame(self.results_container, bg='#fff3cd', relief='solid', borderwidth=1)
            error_frame.pack(fill='x', padx=20, pady=20)
            
            tk.Label(error_frame,
                    text="⚠️ " + error_msg,
                    font=('Segoe UI', 12),
                    bg='#fff3cd',
                    fg='#856404').pack(pady=15)
            return
        
        # Store routes for map generation
        self.current_routes = routes
        self.current_start = start
        self.current_end = end
        
        # Enable map buttons
        self.view_map_btn.config(state='normal')
        self.gmaps_btn.config(state='normal')
        
        # Display each route
        for i, route in enumerate(routes, 1):
            self._create_route_card(route, i)
        
        # Reset scroll position
        self.results_canvas.yview_moveto(0)
    
    def _create_route_card(self, route, index):
        """Create a card for each route alternative"""
        # Card container
        card = tk.Frame(self.results_container,
                       bg='white',
                       relief='solid',
                       borderwidth=2,
                       highlightbackground='#3498db',
                       highlightthickness=1)
        card.pack(fill='x', padx=15, pady=10)
        
        # Header with route type
        header = tk.Frame(card, bg='#3498db')
        header.pack(fill='x')
        
        strategy_colors = {
            'Cheapest': '#27ae60',
            'Fastest': '#e74c3c',
            'Balanced': '#3498db',
            'Most Convenient': '#9b59b6'
        }
        
        bg_color = strategy_colors.get(route.get('strategy', 'Balanced'), '#3498db')
        header.config(bg=bg_color)
        
        tk.Label(header,
                text=f"Option {index}: {route.get('strategy', 'Route')}",
                font=('Segoe UI', 13, 'bold'),
                bg=bg_color,
                fg='white',
                pady=12).pack()
        
        # Metrics row
        metrics_frame = tk.Frame(card, bg='#ecf0f1')
        metrics_frame.pack(fill='x', pady=1)
        
        metrics = [
            ("💰", "Cost", f"₹{route.get('total_cost', 0)}", '#27ae60'),
            ("⏱️", "Time", f"{route.get('total_time', 0)} min", '#e67e22'),
            ("📏", "Distance", f"{route.get('total_distance', 0)} km", '#3498db'),
            ("🔄", "Segments", str(route.get('num_segments', 0)), '#9b59b6')
        ]
        
        for icon, label, value, color in metrics:
            metric_box = tk.Frame(metrics_frame, bg='white', relief='solid', borderwidth=1)
            metric_box.pack(side='left', expand=True, fill='both', padx=2, pady=5)
            
            tk.Label(metric_box,
                    text=icon,
                    font=('Segoe UI', 16),
                    bg='white').pack()
            
            tk.Label(metric_box,
                    text=value,
                    font=('Segoe UI', 12, 'bold'),
                    fg=color,
                    bg='white').pack()
            
            tk.Label(metric_box,
                    text=label,
                    font=('Segoe UI', 8),
                    fg='#7f8c8d',
                    bg='white').pack(pady=(0, 5))
        
        # Route details
        details_frame = tk.Frame(card, bg='white')
        details_frame.pack(fill='both', padx=15, pady=10)
        
        tk.Label(details_frame,
                text="📍 Detailed Route:",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg='#2c3e50').pack(anchor='w', pady=(0, 8))
        
        # Each step
        path = route.get('path', [])
        for j, step in enumerate(path, 1):
            step_frame = tk.Frame(details_frame, bg='#f8f9fa')
            step_frame.pack(fill='x', pady=2)
            
            mode_icons = {
                'start': '🏁',
                'metro': '🚇',
                'bus': '🚌',
                'auto': '🛺',
                'walk': '🚶'
            }
            
            mode = step.get('mode', 'walk')
            icon = mode_icons.get(mode, '→')
            
            if j == 1:
                # Starting point
                tk.Label(step_frame,
                        text=f"{j}. {icon} START: {step.get('location', 'Unknown')}",
                        font=('Segoe UI', 10, 'bold'),
                        bg='#f8f9fa',
                        fg='#27ae60',
                        anchor='w').pack(fill='x', padx=10, pady=5)
            elif j == len(path):
                # End point
                tk.Label(step_frame,
                        text=f"{j}. 🏁 ARRIVE: {step.get('location', 'Unknown')}",
                        font=('Segoe UI', 10, 'bold'),
                        bg='#f8f9fa',
                        fg='#e74c3c',
                        anchor='w').pack(fill='x', padx=10, pady=5)
            else:
                # Intermediate step
                main_text = tk.Label(step_frame,
                                    text=f"{j}. {icon} {step.get('location', 'Unknown')}",
                                    font=('Segoe UI', 10),
                                    bg='#f8f9fa',
                                    fg='#2c3e50',
                                    anchor='w')
                main_text.pack(fill='x', padx=10, pady=(5, 2))
                
                detail_text = tk.Label(step_frame,
                                      text=f"    via {mode.upper()}: {step.get('segment_time', 0)} min, "
                                           f"₹{step.get('segment_cost', 0)}, {step.get('segment_distance', 0)} km",
                                      font=('Segoe UI', 8),
                                      bg='#f8f9fa',
                                      fg='#7f8c8d',
                                      anchor='w')
                detail_text.pack(fill='x', padx=10, pady=(0, 5))
        
        # Transport modes summary
        modes_frame = tk.Frame(card, bg='#f8f9fa', relief='solid', borderwidth=1)
        modes_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        modes_used = set([s.get('mode', 'walk') for s in path if s.get('mode') != 'start'])
        modes_text = ', '.join([m.upper() for m in modes_used]) if modes_used else 'None'
        
        tk.Label(modes_frame,
                text=f"🎯 Transport Modes Used: {modes_text}",
                font=('Segoe UI', 9),
                bg='#f8f9fa',
                fg='#34495e').pack(pady=8, padx=10)
    
    def show_interactive_map(self):
        """Generate and show interactive Folium map"""
        if not self.current_routes:
            messagebox.showwarning("No Routes", "Please calculate routes first")
            return
        
        try:
            # Create map centered on Kochi
            kochi_center = [10.0261, 76.2750]
            route_map = folium.Map(location=kochi_center, zoom_start=12)
            
            # Color scheme for different routes
            colors = ['blue', 'red', 'green', 'purple', 'orange']
            
            # Add routes
            for i, route in enumerate(self.current_routes):
                path = route.get('path', [])
                color = colors[i % len(colors)]
                
                # Get coordinates for route
                route_coords = []
                for step in path:
                    loc_name = step.get('location', '')
                    if loc_name in self.optimizer.locations:
                        loc_data = self.optimizer.locations[loc_name]
                        route_coords.append([loc_data['lat'], loc_data['lon']])
                
                # Draw route line
                if len(route_coords) > 1:
                    folium.PolyLine(
                        route_coords,
                        color=color,
                        weight=4,
                        opacity=0.7,
                        popup=f"Route {i+1}: {route.get('strategy', 'Route')}"
                    ).add_to(route_map)
                
                # Add markers
                for j, step in enumerate(path):
                    loc_name = step.get('location', '')
                    if loc_name in self.optimizer.locations:
                        loc_data = self.optimizer.locations[loc_name]
                        
                        # Icon based on position
                        if j == 0:
                            icon = folium.Icon(color='green', icon='play', prefix='fa')
                            popup_text = f"START: {loc_name}"
                        elif j == len(path) - 1:
                            icon = folium.Icon(color='red', icon='stop', prefix='fa')
                            popup_text = f"END: {loc_name}"
                        else:
                            icon = folium.Icon(color=color, icon='circle', prefix='fa')
                            mode = step.get('mode', 'unknown')
                            popup_text = f"{loc_name}<br>via {mode.upper()}"
                        
                        folium.Marker(
                            [loc_data['lat'], loc_data['lon']],
                            popup=popup_text,
                            icon=icon
                        ).add_to(route_map)
            
            # Save map
            map_path = Path.cwd() / "route_map.html"
            route_map.save(str(map_path))
            
            # Open in browser
            webbrowser.open('file://' + str(map_path.absolute()))
            
            messagebox.showinfo("Map Generated", 
                              f"Interactive map opened in your browser!\n"
                              f"Saved at: {map_path}")
            
        except Exception as e:
            messagebox.showerror("Map Error", f"Error generating map:\n{str(e)}")
    
    def open_google_maps(self):
        """Open route in Google Maps"""
        if not self.current_start or not self.current_end:
            messagebox.showwarning("No Route", "Please calculate routes first")
            return
        
        try:
            # Get coordinates
            start_loc = self.optimizer.locations[self.current_start]
            end_loc = self.optimizer.locations[self.current_end]
            
            # Create Google Maps URL for directions
            start_coords = f"{start_loc['lat']},{start_loc['lon']}"
            end_coords = f"{end_loc['lat']},{end_loc['lon']}"
            
            # Build URL with waypoints if available
            if self.current_routes and len(self.current_routes) > 0:
                # Get first route's path
                route = self.current_routes[0]
                path = route.get('path', [])
                
                # Get waypoints (middle locations)
                waypoints = []
                for i, step in enumerate(path[1:-1]):  # Skip first and last
                    loc_name = step.get('location', '')
                    if loc_name in self.optimizer.locations:
                        loc_data = self.optimizer.locations[loc_name]
                        waypoints.append(f"{loc_data['lat']},{loc_data['lon']}")
                
                # Build Google Maps URL
                if waypoints:
                    waypoints_str = "|".join(waypoints[:5])  # Google Maps limits waypoints
                    gmaps_url = (f"https://www.google.com/maps/dir/?api=1"
                               f"&origin={start_coords}"
                               f"&destination={end_coords}"
                               f"&waypoints={waypoints_str}"
                               f"&travelmode=transit")
                else:
                    gmaps_url = (f"https://www.google.com/maps/dir/?api=1"
                               f"&origin={start_coords}"
                               f"&destination={end_coords}"
                               f"&travelmode=transit")
            else:
                gmaps_url = (f"https://www.google.com/maps/dir/?api=1"
                           f"&origin={start_coords}"
                           f"&destination={end_coords}"
                           f"&travelmode=transit")
            
            # Open in browser
            webbrowser.open(gmaps_url)
            
            messagebox.showinfo("Google Maps", 
                              "Route opened in Google Maps!\n"
                              "You can see real-time traffic and alternative routes.")
            
        except Exception as e:
            messagebox.showerror("Google Maps Error", 
                               f"Error opening Google Maps:\n{str(e)}")
    
    def _show_error(self, error_message):
        """Show error message"""
        self.progress.stop()
        self.progress.pack_forget()
        self.calculate_btn.config(state='normal', text="🔍 Find Optimal Routes")
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    
    try:
        app = LocationRouteGUI(root)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Set minimum size
        root.minsize(1200, 800)
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        messagebox.showerror("Critical Error", f"A critical error occurred:\n{e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()