 
"""
Performance Analysis Script for Kochi Route Optimizer
Measures: Computation Time, Memory Usage, Routes Generated
"""

import time
import tracemalloc
import statistics
from dijkstra import LocationToLocationOptimizer
from typing import List, Dict
import sys

class PerformanceAnalyzer:
    def __init__(self):
        print("Initializing Route Optimizer...")
        self.optimizer = LocationToLocationOptimizer()
        print("✓ Optimizer initialized successfully!\n")
        
        # Test cases with varying complexity
        self.test_cases = [
            # Simple routes (direct metro)
            ("Aluva Metro", "Pulinchodu Metro", "Simple"),
            ("Edapally Metro", "Palarivattom Metro", "Simple"),
            
            # Medium routes (metro + connection)
            ("Lulu Mall Edapally", "M.G Road Metro", "Medium"),
            ("Medical Trust Hospital Edapally", "Oberon Mall", "Medium"),
            
            # Complex routes (multiple modes)
            ("Aluva Town", "Fort Kochi", "Complex"),
            ("Kakkanad Infopark", "Marine Drive", "Complex"),
            ("CUSAT Campus", "Thripunithura Town", "Complex"),
            
            # Long distance routes
            ("Aluva Metro", "Thripunithura Metro", "Long"),
            ("Lulu Mall Edapally", "Fort Kochi", "Long"),
        ]
        
        self.results = []
    
    def measure_single_route(self, start: str, end: str) -> Dict:
        """Measure performance for a single route calculation"""
        
        # Start memory tracking
        tracemalloc.start()
        
        # Measure computation time
        start_time = time.time()
        
        try:
            routes = self.optimizer.find_optimized_routes(start, end)
            
            end_time = time.time()
            computation_time = end_time - start_time
            
            # Get memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Extract route information
            num_routes = len(routes) if routes and 'error' not in routes[0] else 0
            
            return {
                'start': start,
                'end': end,
                'computation_time': computation_time,
                'memory_used_mb': peak / (1024 * 1024),
                'routes_generated': num_routes,
                'success': num_routes > 0,
                'routes': routes if num_routes > 0 else None
            }
            
        except Exception as e:
            tracemalloc.stop()
            return {
                'start': start,
                'end': end,
                'computation_time': 0,
                'memory_used_mb': 0,
                'routes_generated': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_analysis(self):
        """Run complete performance analysis"""
        
        print("="*80)
        print("PERFORMANCE ANALYSIS - KOCHI ROUTE OPTIMIZER")
        print("="*80)
        print(f"\nRunning {len(self.test_cases)} test cases...\n")
        
        for i, (start, end, complexity) in enumerate(self.test_cases, 1):
            print(f"Test {i}/{len(self.test_cases)}: {start} → {end} ({complexity})")
            
            result = self.measure_single_route(start, end)
            result['complexity'] = complexity
            self.results.append(result)
            
            if result['success']:
                print(f"  ✓ Time: {result['computation_time']:.4f}s | "
                      f"Memory: {result['memory_used_mb']:.2f}MB | "
                      f"Routes: {result['routes_generated']}")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
            
            print()
        
        print("="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        
        successful_tests = [r for r in self.results if r['success']]
        
        if not successful_tests:
            print("\n❌ No successful tests to analyze!")
            return
        
        # Calculate statistics
        computation_times = [r['computation_time'] for r in successful_tests]
        memory_usage = [r['memory_used_mb'] for r in successful_tests]
        routes_generated = [r['routes_generated'] for r in successful_tests]
        
        avg_time = statistics.mean(computation_times)
        max_time = max(computation_times)
        min_time = min(computation_times)
        std_time = statistics.stdev(computation_times) if len(computation_times) > 1 else 0
        
        avg_memory = statistics.mean(memory_usage)
        max_memory = max(memory_usage)
        min_memory = min(memory_usage)
        
        avg_routes = statistics.mean(routes_generated)
        
        # Print comprehensive report
        print("\n" + "="*80)
        print("ALGORITHM PERFORMANCE ANALYSIS")
        print("="*80)
        
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│                    COMPUTATIONAL EFFICIENCY                     │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        print(f"\n{'Metric':<35} {'Value':<20} {'Evaluation'}")
        print("-" * 80)
        
        # Computation Time
        print(f"{'Average Computation Time':<35} {avg_time:.4f} seconds    {self._evaluate_time(avg_time)}")
        print(f"{'Maximum Computation Time':<35} {max_time:.4f} seconds    {self._evaluate_time(max_time)}")
        print(f"{'Minimum Computation Time':<35} {min_time:.4f} seconds    {self._evaluate_time(min_time)}")
        print(f"{'Standard Deviation':<35} {std_time:.4f} seconds")
        
        print()
        
        # Memory Usage
        print(f"{'Average Memory Usage':<35} {avg_memory:.2f} MB          {self._evaluate_memory(avg_memory)}")
        print(f"{'Maximum Memory Usage':<35} {max_memory:.2f} MB          {self._evaluate_memory(max_memory)}")
        print(f"{'Minimum Memory Usage':<35} {min_memory:.2f} MB")
        
        print()
        
        # Routes Generated
        print(f"{'Average Routes Generated':<35} {avg_routes:.1f}              {self._evaluate_routes(avg_routes)}")
        print(f"{'Success Rate':<35} {len(successful_tests)}/{len(self.results)} ({len(successful_tests)/len(self.results)*100:.1f}%)")
        
        # Complexity Analysis
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│                    COMPLEXITY BREAKDOWN                         │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        complexity_stats = {}
        for complexity in ['Simple', 'Medium', 'Complex', 'Long']:
            tests = [r for r in successful_tests if r['complexity'] == complexity]
            if tests:
                complexity_stats[complexity] = {
                    'count': len(tests),
                    'avg_time': statistics.mean([r['computation_time'] for r in tests]),
                    'avg_memory': statistics.mean([r['memory_used_mb'] for r in tests])
                }
        
        print(f"\n{'Complexity':<15} {'Tests':<10} {'Avg Time':<20} {'Avg Memory'}")
        print("-" * 80)
        for complexity, stats in complexity_stats.items():
            print(f"{complexity:<15} {stats['count']:<10} {stats['avg_time']:.4f} seconds      {stats['avg_memory']:.2f} MB")
        
        # Time Complexity Verification
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│               TIME COMPLEXITY VERIFICATION                      │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        V = len(self.optimizer.locations)  # Vertices
        E = sum(len(edges) for edges in self.optimizer.graph.values())  # Edges
        
        theoretical_ops = (V + E) * (V ** 0.5)  # Approximation of (V+E)logV
        
        print(f"\nGraph Statistics:")
        print(f"  Vertices (V): {V}")
        print(f"  Edges (E): {E}")
        print(f"  Theoretical Complexity: O((V + E) log V)")
        print(f"  Expected Operations: ~{theoretical_ops:.0f}")
        print(f"\nActual Performance:")
        print(f"  Average Time: {avg_time:.4f} seconds")
        print(f"  Operations/Second: ~{theoretical_ops/avg_time if avg_time > 0 else 0:.0f}")
        
        # Best and Worst Cases
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│                   BEST & WORST CASES                            │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        fastest = min(successful_tests, key=lambda x: x['computation_time'])
        slowest = max(successful_tests, key=lambda x: x['computation_time'])
        
        print("\n🏆 FASTEST ROUTE:")
        print(f"  {fastest['start']} → {fastest['end']}")
        print(f"  Time: {fastest['computation_time']:.4f}s | Memory: {fastest['memory_used_mb']:.2f}MB")
        
        print("\n🐢 SLOWEST ROUTE:")
        print(f"  {slowest['start']} → {slowest['end']}")
        print(f"  Time: {slowest['computation_time']:.4f}s | Memory: {slowest['memory_used_mb']:.2f}MB")
        
        # Detailed Route Analysis
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│                  DETAILED ROUTE ANALYSIS                        │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        print(f"\n{'Route':<50} {'Time(s)':<12} {'Memory(MB)':<12} {'Routes'}")
        print("-" * 90)
        
        for result in successful_tests:
            route_str = f"{result['start'][:20]} → {result['end'][:20]}"
            print(f"{route_str:<50} {result['computation_time']:<12.4f} {result['memory_used_mb']:<12.2f} {result['routes_generated']}")
        
        # Summary Table (For Presentation)
        print("\n" + "="*80)
        print("SUMMARY TABLE ")
        print("="*80)
        
        print("\n┌────────────────────────────────┬──────────────────┬──────────────┐")
        print("│ Metric                         │ Value            │ Evaluation   │")
        print("├────────────────────────────────┼──────────────────┼──────────────┤")
        print(f"│ Average Computation Time       │ {avg_time:.4f} seconds  │ {self._evaluate_time(avg_time):<12} │")
        print(f"│ Maximum Computation Time       │ {max_time:.4f} seconds  │ {self._evaluate_time(max_time):<12} │")
        print(f"│ Memory Usage                   │ ~{avg_memory:.2f} MB        │ {self._evaluate_memory(avg_memory):<12} │")
        print(f"│ Routes Generated               │ {avg_routes:.1f}             │ {self._evaluate_routes(avg_routes):<12} │")
        print("└────────────────────────────────┴──────────────────┴──────────────┘")
        
        # Export data for PPT
        print("\n" + "="*80)
        print("DATA REPORT")
        print("="*80)
        print(f"""
Average Computation Time: {avg_time:.4f} seconds ({self._evaluate_time(avg_time)})
Maximum Computation Time: {max_time:.4f} seconds ({self._evaluate_time(max_time)})
Minimum Computation Time: {min_time:.4f} seconds ({self._evaluate_time(min_time)})
Average Memory Usage: {avg_memory:.2f} MB ({self._evaluate_memory(avg_memory)})
Maximum Memory Usage: {max_memory:.2f} MB
Routes Generated: {avg_routes:.1f} alternatives ({self._evaluate_routes(avg_routes)})
Success Rate: {len(successful_tests)}/{len(self.results)} ({len(successful_tests)/len(self.results)*100:.1f}%)

Graph Statistics:
- Vertices: {V}
- Edges: {E}
- Theoretical Complexity: O((V + E) log V) ≈ O({theoretical_ops:.0f})
- Actual Operations/Second: ~{theoretical_ops/avg_time if avg_time > 0 else 0:.0f}
""")
    
    def _evaluate_time(self, time_seconds: float) -> str:
        """Evaluate computation time performance"""
        if time_seconds < 0.1:
            return "Excellent"
        elif time_seconds < 0.3:
            return "Very Good"
        elif time_seconds < 0.5:
            return "Good"
        elif time_seconds < 1.0:
            return "Acceptable"
        else:
            return "Needs Optimization"
    
    def _evaluate_memory(self, memory_mb: float) -> str:
        """Evaluate memory usage"""
        if memory_mb < 20:
            return "Efficient"
        elif memory_mb < 50:
            return "Good"
        elif memory_mb < 100:
            return "Acceptable"
        else:
            return "High"
    
    def _evaluate_routes(self, num_routes: float) -> str:
        """Evaluate number of routes generated"""
        if num_routes >= 4:
            return "Optimal"
        elif num_routes >= 3:
            return "Good"
        elif num_routes >= 2:
            return "Acceptable"
        else:
            return "Limited"
    
    def save_detailed_report(self, filename='performance_report.txt'):
        """Save detailed report to file"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("KOCHI ROUTE OPTIMIZER - PERFORMANCE ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            for result in self.results:
                f.write(f"Route: {result['start']} → {result['end']}\n")
                f.write(f"Complexity: {result['complexity']}\n")
                
                if result['success']:
                    f.write(f"Computation Time: {result['computation_time']:.4f} seconds\n")
                    f.write(f"Memory Usage: {result['memory_used_mb']:.2f} MB\n")
                    f.write(f"Routes Generated: {result['routes_generated']}\n")
                    
                    if result['routes']:
                        f.write("\nRoute Details:\n")
                        for i, route in enumerate(result['routes'], 1):
                            f.write(f"  {i}. {route.get('strategy', 'Unknown')}: ")
                            f.write(f"₹{route.get('total_cost', 0)} | ")
                            f.write(f"{route.get('total_time', 0)} min | ")
                            f.write(f"{route.get('total_distance', 0)} km\n")
                else:
                    f.write(f"Status: FAILED - {result.get('error', 'Unknown error')}\n")
                
                f.write("-"*80 + "\n\n")
        
        print(f"\n✓ Detailed report saved to: {filename}")

def main():
    """Main function to run performance analysis"""
    
    print("\n" + "🔍"*30)
    print("KOCHI ROUTE OPTIMIZER - PERFORMANCE ANALYSIS")
    print("🔍"*30 + "\n")
    
    analyzer = PerformanceAnalyzer()
    
    # Run analysis
    analyzer.run_analysis()
    
    # Generate comprehensive report
    analyzer.generate_report()
    
    # Save detailed report
    analyzer.save_detailed_report()
    
    print("\n" + "="*80)
    print("✓ Performance analysis complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()