import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import math

class LocationToLocationOptimizer:
    """
    Route optimizer from ANY location to ANY location
    Integrates metro, walking, bus, and auto options
    """
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.locations = {}  # All searchable locations
        self.metro_stations = {}
        
        # Build complete network
        self._build_metro_network()
        self._add_popular_locations()
        self._connect_locations_to_metro()
        self._add_direct_connections()
    
    def _build_metro_network(self):
        """Build Kochi Metro network with coordinates"""
        metro_data = [
            ("Aluva Metro", 10.1082, 76.3520, "Zone 3"),
            ("Pulinchodu Metro", 10.1012, 76.3445, "Zone 3"),
            ("Companypady Metro", 10.0942, 76.3370, "Zone 3"),
            ("Ambattukavu Metro", 10.0872, 76.3295, "Zone 2"),
            ("Muttom Metro", 10.0802, 76.3220, "Zone 2"),
            ("Kalamassery Metro", 10.0732, 76.3145, "Zone 2"),
            ("Cusat Metro", 10.0662, 76.3070, "Zone 2"),
            ("Pathadipalam Metro", 10.0592, 76.2995, "Zone 2"),
            ("Edapally Metro", 10.0522, 76.2920, "Zone 2"),
            ("Changampuzha Park Metro", 10.0452, 76.2845, "Zone 2"),
            ("Palarivattom Metro", 10.0382, 76.2770, "Zone 2"),
            ("J.L.N Stadium Metro", 10.0312, 76.2695, "Zone 2"),
            ("Kaloor Metro", 10.0242, 76.2620, "Zone 2"),
            ("Lissie Metro", 10.0172, 76.2545, "Zone 1"),
            ("M.G Road Metro", 10.0102, 76.2470, "Zone 1"),
            ("Maharajas Metro", 10.0032, 76.2395, "Zone 1"),
            ("Ernakulam South Metro", 9.9962, 76.2320, "Zone 1"),
            ("Kadavanthra Metro", 9.9892, 76.2245, "Zone 2"),
            ("Elamkulam Metro", 9.9822, 76.2170, "Zone 2"),
            ("Vyttila Metro", 9.9752, 76.2095, "Zone 2"),
            ("Thaikoodam Metro", 9.9682, 76.2020, "Zone 3"),
            ("Petta Metro", 9.9612, 76.1945, "Zone 3"),
            ("Thripunithura Metro", 9.9542, 76.1870, "Zone 3")
        ]
        
        for name, lat, lon, zone in metro_data:
            self.locations[name] = {
                'lat': lat,
                'lon': lon,
                'type': 'metro_station',
                'zone': zone
            }
            self.metro_stations[name] = (lat, lon)
        
        # Connect consecutive metro stations
        stations_list = [name for name, _, _, _ in metro_data]
        for i in range(len(stations_list) - 1):
            station1 = stations_list[i]
            station2 = stations_list[i + 1]
            
            time = 2.5  # Average 2.5 minutes between stations
            distance = self._haversine_distance(
                self.locations[station1]['lat'], self.locations[station1]['lon'],
                self.locations[station2]['lat'], self.locations[station2]['lon']
            )
            cost = 5  # ₹5 per hop
            
            self._add_edge(station1, station2, 'metro', time, distance, cost)
            self._add_edge(station2, station1, 'metro', time, distance, cost)
    
    def _add_popular_locations(self):
        """Add popular destinations in Kochi"""
        popular_places = [
            # Residential/Commercial areas
            ("Aluva Town", 10.1100, 76.3550, "residential"),
            ("Kalamassery Town", 10.0750, 76.3200, "residential"),
            ("Edapally Market", 10.0540, 76.2950, "commercial"),
            ("Kakkanad Infopark", 10.0150, 76.3450, "commercial"),
            ("Palarivattom Junction", 10.0400, 76.2800, "junction"),
            ("M.G Road Market", 10.0120, 76.2500, "commercial"),
            ("Marine Drive", 9.9750, 76.2800, "tourist"),
            ("Ernakulam South Bus Stand", 9.9980, 76.2350, "transport_hub"),
            ("Fort Kochi", 9.9650, 76.2420, "tourist"),
            ("Vyttila Hub", 9.9770, 76.3100, "transport_hub"),
            ("Kakkanad Seaport Airport Road", 10.0050, 76.3350, "commercial"),
            ("Thripunithura Town", 9.9560, 76.1900, "residential"),
            
            # Hospitals
            ("Medical Trust Hospital Edapally", 10.0510, 76.2880, "hospital"),
            ("Lakeshore Hospital Kochi", 9.9800, 76.2950, "hospital"),
            ("Amrita Hospital Kochi", 10.0430, 76.3100, "hospital"),
            
            # Educational Institutions
            ("CUSAT Campus", 10.0650, 76.3050, "educational"),
            ("Rajagiri College Kakkanad", 10.0200, 76.3400, "educational"),
            
            # Shopping Malls
            ("Lulu Mall Edapally", 10.0450, 76.3000, "mall"),
            ("Oberon Mall", 10.0340, 76.2780, "mall"),
            ("Centre Square Mall", 9.9880, 76.2880, "mall"),
        ]
        
        for name, lat, lon, loc_type in popular_places:
            self.locations[name] = {
                'lat': lat,
                'lon': lon,
                'type': loc_type,
                'zone': 'N/A'
            }
    
    def _connect_locations_to_metro(self):
        """Connect each location to nearest metro stations"""
        for location, loc_data in self.locations.items():
            if loc_data['type'] == 'metro_station':
                continue
            
            # Find 3 nearest metro stations
            nearest_stations = self._find_nearest_metro_stations(location, k=3)
            
            for station, distance_km in nearest_stations:
                # Walking connection (if < 1.5km) - reduced from 2km
                if distance_km < 1.5:
                    walk_time = distance_km * 15  # 15 min per km walking
                    walk_cost = distance_km * 5  # ₹5/km for time value (changed from 0)
                    self._add_edge(location, station, 'walk', walk_time, distance_km, walk_cost)
                    self._add_edge(station, location, 'walk', walk_time, distance_km, walk_cost)
                
                # Auto connection (always available for reasonable distances)
                if distance_km < 15:  # Only connect if within 15km
                    auto_time = distance_km * 3  # 3 min per km by auto
                    auto_cost = 20 + (distance_km * 12)  # ₹20 base + ₹12/km
                    self._add_edge(location, station, 'auto', auto_time, distance_km, auto_cost)
                    self._add_edge(station, location, 'auto', auto_time, distance_km, auto_cost)
                
                # Bus connection (if > 1km and < 10km)
                if 1.0 < distance_km < 10:
                    bus_time = distance_km * 4  # 4 min per km by bus
                    bus_cost = 10 + (distance_km * 3)  # ₹10 base + ₹3/km
                    self._add_edge(location, station, 'bus', bus_time, distance_km, bus_cost)
                    self._add_edge(station, location, 'bus', bus_time, distance_km, bus_cost)
    
    def _add_direct_connections(self):
        """Add direct connections between nearby non-metro locations"""
        locations_list = [(name, data) for name, data in self.locations.items() 
                         if data['type'] != 'metro_station']
        
        for i, (loc1, data1) in enumerate(locations_list):
            for loc2, data2 in locations_list[i+1:]:
                distance = self._haversine_distance(
                    data1['lat'], data1['lon'],
                    data2['lat'], data2['lon']
                )
                
                # Add auto connection if within 10km
                if distance < 10:
                    auto_time = distance * 3
                    auto_cost = 20 + (distance * 12)
                    self._add_edge(loc1, loc2, 'auto', auto_time, distance, auto_cost)
                    self._add_edge(loc2, loc1, 'auto', auto_time, distance, auto_cost)
                
                # Add walking if within 1.5km
                if distance < 1.5:
                    walk_time = distance * 15
                    walk_cost = distance * 5
                    self._add_edge(loc1, loc2, 'walk', walk_time, distance, walk_cost)
                    self._add_edge(loc2, loc1, 'walk', walk_time, distance, walk_cost)
    
    def _add_edge(self, from_loc: str, to_loc: str, mode: str, 
                  time: float, distance: float, cost: float):
        """Add directed edge to graph"""
        self.graph[from_loc].append({
            'destination': to_loc,
            'mode': mode,
            'time': time,
            'distance': distance,
            'cost': cost
        })
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _find_nearest_metro_stations(self, location: str, k: int = 3) -> List[Tuple[str, float]]:
        """Find k nearest metro stations to a location"""
        if location not in self.locations:
            return []
        
        loc_data = self.locations[location]
        distances = []
        
        for station, (lat, lon) in self.metro_stations.items():
            dist = self._haversine_distance(
                loc_data['lat'], loc_data['lon'], lat, lon
            )
            distances.append((station, dist))
        
        distances.sort(key=lambda x: x[1])
        return distances[:k]
    
    def find_optimized_routes(self, start_location: str, end_location: str) -> List[Dict]:
        """
        Find optimized routes from any location to any location
        Returns multiple route alternatives
        """
        
        if start_location not in self.locations:
            return [{"error": f"Start location '{start_location}' not found"}]
        if end_location not in self.locations:
            return [{"error": f"End location '{end_location}' not found"}]
        
        if start_location == end_location:
            return [{"error": "Start and end locations are the same"}]
        
        # Run Dijkstra with different strategies
        strategies = [
            {"name": "Cheapest", "cost": 0.8, "time": 0.1, "conv": 0.1},
            {"name": "Fastest", "cost": 0.1, "time": 0.8, "conv": 0.1},
            {"name": "Balanced", "cost": 0.4, "time": 0.4, "conv": 0.2},
            {"name": "Most Convenient", "cost": 0.2, "time": 0.3, "conv": 0.5},
        ]
        
        all_routes = []
        
        for strategy in strategies:
            result = self._dijkstra(
                start_location,
                end_location,
                cost_weight=strategy["cost"],
                time_weight=strategy["time"],
                convenience_weight=strategy["conv"]
            )
            
            if result and result['previous'][end_location] is not None:
                path = self._reconstruct_path(start_location, end_location, result)
                
                if path:  # Only add if path exists
                    all_routes.append({
                        'strategy': strategy["name"],
                        'total_cost': round(result['costs'][end_location], 2),
                        'total_time': round(result['times'][end_location], 1),
                        'total_distance': round(result['distances_km'][end_location], 2),
                        'num_segments': len(path) - 1,
                        'path': path
                    })
        
        # Remove duplicates (same path with different strategy names)
        unique_routes = []
        seen_paths = set()
        
        for route in all_routes:
            path_key = tuple([p['location'] for p in route['path']])
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                unique_routes.append(route)
        
        # Sort by a composite score favoring cheaper and faster routes
        unique_routes.sort(key=lambda r: (r['total_cost'] * 0.6 + r['total_time'] * 0.4))
        
        if not unique_routes:
            return [{"error": f"No route found between {start_location} and {end_location}"}]
        
        return unique_routes
    
    def _dijkstra(self, start: str, end: str, cost_weight: float, 
                  time_weight: float, convenience_weight: float) -> Optional[Dict]:
        """Dijkstra's algorithm with multi-criteria optimization"""
        
        distances = {loc: float('inf') for loc in self.locations}
        costs = {loc: float('inf') for loc in self.locations}
        times = {loc: float('inf') for loc in self.locations}
        distances_km = {loc: float('inf') for loc in self.locations}
        transfers = {loc: 0 for loc in self.locations}
        previous = {loc: None for loc in self.locations}
        edge_info = {loc: None for loc in self.locations}  # Store edge details
        
        distances[start] = 0
        costs[start] = 0
        times[start] = 0
        distances_km[start] = 0
        transfers[start] = 0
        
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            # Early exit if we reached destination
            if current == end:
                break
            
            # Check if current location has any edges
            if current not in self.graph:
                continue
            
            for edge in self.graph[current]:
                neighbor = edge['destination']
                
                if neighbor in visited:
                    continue
                
                new_cost = costs[current] + edge['cost']
                new_time = times[current] + edge['time']
                new_distance = distances_km[current] + edge['distance']
                new_transfers = transfers[current]
                
                # Get previous mode
                prev_mode = edge_info[current]['mode'] if edge_info[current] else None
                
                # Increment transfers if mode changes
                if prev_mode and prev_mode != edge['mode']:
                    new_transfers += 1
                
                # Convenience penalty for mode changes and walking
                mode_change_penalty = 0
                if prev_mode and prev_mode != edge['mode']:
                    mode_change_penalty = 0.3
                
                # Add penalty for long walks
                walk_penalty = 0
                if edge['mode'] == 'walk' and edge['distance'] > 0.5:
                    walk_penalty = edge['distance'] * 0.2
                
                # Normalize for fair comparison
                norm_cost = new_cost / 200.0 if new_cost > 0 else 0
                norm_time = new_time / 120.0 if new_time > 0 else 0
                norm_transfers = new_transfers / 5.0 if new_transfers > 0 else 0
                
                # Composite score
                composite = (
                    cost_weight * norm_cost +
                    time_weight * norm_time +
                    convenience_weight * (norm_transfers + mode_change_penalty + walk_penalty)
                )
                
                if composite < distances[neighbor]:
                    distances[neighbor] = composite
                    costs[neighbor] = new_cost
                    times[neighbor] = new_time
                    distances_km[neighbor] = new_distance
                    transfers[neighbor] = new_transfers
                    previous[neighbor] = current
                    edge_info[neighbor] = edge  # Store edge details
                    heapq.heappush(pq, (composite, neighbor))
        
        return {
            'distances': distances,
            'costs': costs,
            'times': times,
            'distances_km': distances_km,
            'transfers': transfers,
            'previous': previous,
            'edge_info': edge_info
        }
    
    def _reconstruct_path(self, start: str, end: str, result: Dict) -> List[Dict]:
        """Reconstruct the path with detailed information"""
        path = []
        current = end
        
        # Build path backwards
        while current is not None:
            path.append(current)
            current = result['previous'][current]
        
        path.reverse()
        
        # Validate path
        if not path or path[0] != start:
            return []
        
        # Add detailed information
        detailed_path = []
        for i in range(len(path)):
            loc = path[i]
            
            if i == 0:
                # Starting point
                detailed_path.append({
                    'location': loc,
                    'type': self.locations[loc]['type'],
                    'mode': 'start',
                    'segment_time': 0,
                    'segment_cost': 0,
                    'segment_distance': 0
                })
            else:
                # Get edge info from result
                edge = result['edge_info'][loc]
                
                if edge:
                    detailed_path.append({
                        'location': loc,
                        'type': self.locations[loc]['type'],
                        'mode': edge['mode'],
                        'segment_time': round(edge['time'], 1),
                        'segment_cost': round(edge['cost'], 2),
                        'segment_distance': round(edge['distance'], 2)
                    })
                else:
                    # Edge not found - shouldn't happen but handle gracefully
                    detailed_path.append({
                        'location': loc,
                        'type': self.locations[loc]['type'],
                        'mode': 'unknown',
                        'segment_time': 0,
                        'segment_cost': 0,
                        'segment_distance': 0
                    })
        
        return detailed_path

class RouteOptimizerApp:
    """User interface for location-to-location routing"""
    
    def __init__(self):
        self.optimizer = LocationToLocationOptimizer()
    
    def display_available_locations(self):
        """Show all searchable locations"""
        print("\n" + "="*80)
        print("AVAILABLE LOCATIONS IN KOCHI")
        print("="*80)
        
        # Group by type
        metro = [name for name, data in self.optimizer.locations.items() 
                if data['type'] == 'metro_station']
        commercial = [name for name, data in self.optimizer.locations.items() 
                     if data['type'] in ['commercial', 'mall']]
        residential = [name for name, data in self.optimizer.locations.items() 
                      if data['type'] == 'residential']
        others = [name for name, data in self.optimizer.locations.items() 
                 if data['type'] not in ['metro_station', 'commercial', 'mall', 'residential']]
        
        print(f"\n📍 METRO STATIONS ({len(metro)}):")
        for i, loc in enumerate(sorted(metro), 1):
            print(f"   {i:2d}. {loc}")
        
        print(f"\n🏢 COMMERCIAL/MALLS ({len(commercial)}):")
        for loc in sorted(commercial):
            print(f"   • {loc}")
        
        print(f"\n🏘️  RESIDENTIAL AREAS ({len(residential)}):")
        for loc in sorted(residential):
            print(f"   • {loc}")
        
        print(f"\n🎯 OTHER LOCATIONS ({len(others)}):")
        for loc in sorted(others):
            loc_type = self.optimizer.locations[loc]['type']
            print(f"   • {loc} ({loc_type})")
        
        print(f"\nTotal locations: {len(self.optimizer.locations)}")
    
    def find_route(self):
        """Interactive route finding"""
        print("\n" + "="*80)
        print("FIND OPTIMIZED ROUTE")
        print("="*80)
        
        print("\nEnter location names (or part of name):")
        start = input("From (Starting Location): ").strip()
        end = input("To (Destination): ").strip()
        
        if not start or not end:
            print("❌ Please enter both starting location and destination")
            return
        
        # Fuzzy search for locations
        start_matches = [loc for loc in self.optimizer.locations.keys() 
                        if start.lower() in loc.lower()]
        end_matches = [loc for loc in self.optimizer.locations.keys() 
                      if end.lower() in loc.lower()]
        
        if not start_matches:
            print(f"❌ No locations found matching '{start}'")
            return
        if not end_matches:
            print(f"❌ No locations found matching '{end}'")
            return
        
        if len(start_matches) > 1:
            print(f"\nMultiple matches for start location:")
            for i, loc in enumerate(start_matches, 1):
                print(f"{i}. {loc}")
            try:
                choice = int(input("Select (number): ")) - 1
                if choice < 0 or choice >= len(start_matches):
                    print("Invalid selection")
                    return
                start_location = start_matches[choice]
            except (ValueError, IndexError):
                print("Invalid input")
                return
        else:
            start_location = start_matches[0]
        
        if len(end_matches) > 1:
            print(f"\nMultiple matches for destination:")
            for i, loc in enumerate(end_matches, 1):
                print(f"{i}. {loc}")
            try:
                choice = int(input("Select (number): ")) - 1
                if choice < 0 or choice >= len(end_matches):
                    print("Invalid selection")
                    return
                end_location = end_matches[choice]
            except (ValueError, IndexError):
                print("Invalid input")
                return
        else:
            end_location = end_matches[0]
        
        print(f"\n🔍 Finding optimized routes from:")
        print(f"   📍 {start_location}")
        print(f"   → 📍 {end_location}")
        print("\nCalculating...\n")
        
        routes = self.optimizer.find_optimized_routes(start_location, end_location)
        
        if not routes:
            print("❌ No routes found!")
            return
        
        if 'error' in routes[0]:
            print(f"❌ {routes[0]['error']}")
            return
        
        self.display_routes(routes, start_location, end_location)
    
    def display_routes(self, routes: List[Dict], start: str, end: str):
        """Display all route alternatives"""
        print("\n" + "="*80)
        print(f"ROUTE ALTERNATIVES: {start} → {end}")
        print("="*80)
        
        for i, route in enumerate(routes, 1):
            print(f"\n{'─'*80}")
            print(f"🛣️  OPTION {i}: {route['strategy']}")
            print(f"{'─'*80}")
            print(f"💰 Total Cost: ₹{route['total_cost']}")
            print(f"⏱️  Total Time: {route['total_time']} minutes")
            print(f"📏 Total Distance: {route['total_distance']} km")
            print(f"🔄 Segments: {route['num_segments']}")
            
            print(f"\n📍 Detailed Route:")
            for j, step in enumerate(route['path'], 1):
                mode_icon = {
                    'start': '🏁',
                    'metro': '🚇',
                    'bus': '🚌',
                    'auto': '🛺',
                    'walk': '🚶',
                    'unknown': '❓'
                }.get(step['mode'], '→')
                
                if j == 1:
                    print(f"   {j}. {mode_icon} START: {step['location']}")
                else:
                    print(f"   {j}. {mode_icon} {step['mode'].upper()}: {step['location']}")
                    print(f"       (Time: {step['segment_time']}min, "
                          f"Cost: ₹{step['segment_cost']}, "
                          f"Distance: {step['segment_distance']}km)")
            
            # Verify totals
            calc_cost = sum([s['segment_cost'] for s in route['path']])
            calc_time = sum([s['segment_time'] for s in route['path']])
            calc_dist = sum([s['segment_distance'] for s in route['path']])
            
            print(f"\n✅ Verification:")
            print(f"   Cost: ₹{calc_cost:.2f} (displayed: ₹{route['total_cost']})")
            print(f"   Time: {calc_time:.1f}min (displayed: {route['total_time']}min)")
            print(f"   Distance: {calc_dist:.2f}km (displayed: {route['total_distance']}km)")
            
            # Summary
            modes_used = set([s['mode'] for s in route['path'] if s['mode'] not in ['start', 'unknown']])
            if modes_used:
                print(f"\n🎯 Transport modes: {', '.join([m.upper() for m in modes_used])}")
    
    def run(self):
        """Main application loop"""
        print("\n" + "🗺️ "*30)
        print("KOCHI LOCATION-TO-LOCATION ROUTE OPTIMIZER")
        print("Find optimized routes from ANY location to ANY location!")
        print("🗺️ "*30)
        
        while True:
            print("\n" + "-"*80)
            print("MENU:")
            print("1. View all available locations")
            print("2. Find route between two locations")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                self.display_available_locations()
            elif choice == '2':
                self.find_route()
            elif choice == '3':
                print("\n✅ Thank you for using Kochi Route Optimizer!")
                print("Safe travels! 🚇🚌🛺\n")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = RouteOptimizerApp()
    app.run()