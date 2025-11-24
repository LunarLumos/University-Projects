#!/usr/bin/env python3
"""
Script to add comprehensive test data to the DUTP database
Run this after starting the Flask app to populate with more routes and buses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Route, Bus
from datetime import time

def add_test_data():
    with app.app_context():
        print("Adding additional test routes and buses...")

        # Check current counts
        current_routes = Route.query.count()
        current_buses = Bus.query.count()
        print(f"Current: {current_routes} routes, {current_buses} buses")

        # Add new routes if they don't exist
        new_routes = [
            {
                'name': 'Campus ⇄ Dhanmondi',
                'start': 'DIU Main Campus',
                'end': 'Dhanmondi 27',
                'distance': 18.0,
                'duration': 50
            },
            {
                'name': 'Campus ⇄ Gulshan',
                'start': 'DIU Main Campus',
                'end': 'Gulshan Circle 1',
                'distance': 25.0,
                'duration': 70
            },
            {
                'name': 'Campus ⇄ Banani',
                'start': 'DIU Main Campus',
                'end': 'Banani DOHS',
                'distance': 20.0,
                'duration': 55
            }
        ]

        added_routes = 0
        for route_data in new_routes:
            # Check if route already exists
            existing = Route.query.filter_by(route_name=route_data['name']).first()
            if not existing:
                route = Route(
                    route_name=route_data['name'],
                    start_point=route_data['start'],
                    end_point=route_data['end'],
                    distance=route_data['distance'],
                    duration=route_data['duration'],
                    status='active'
                )
                db.session.add(route)
                added_routes += 1
                print(f"Added route: {route_data['name']}")

        db.session.commit()  # Commit routes to get IDs

        # Add new buses
        new_buses = [
            # Additional buses for existing routes
            {'number': '🌼 DIU BUS 05', 'capacity': 40, 'driver': 'Mohammad Ali', 'route_name': 'Campus ⇄ Mirpur', 'time': time(16, 0)},
            {'number': '🌼 DIU BUS 06', 'capacity': 35, 'driver': 'Rafiq Islam', 'route_name': 'Campus ⇄ Uttara', 'time': time(12, 30)},
            {'number': '🌼 DIU BUS 07', 'capacity': 40, 'driver': 'Sultan Ahmed', 'route_name': 'Campus ⇄ Uttara', 'time': time(15, 0)},

            # Buses for new routes
            {'number': '🌼 DIU BUS 08', 'capacity': 35, 'driver': 'Shamim Reza', 'route_name': 'Campus ⇄ Dhanmondi', 'time': time(8, 45)},
            {'number': '🌼 DIU BUS 09', 'capacity': 40, 'driver': 'Fazlul Karim', 'route_name': 'Campus ⇄ Dhanmondi', 'time': time(10, 30)},
            {'number': '🌼 DIU BUS 10', 'capacity': 35, 'driver': 'Anwar Hossain', 'route_name': 'Campus ⇄ Dhanmondi', 'time': time(13, 15)},

            {'number': '🌼 DIU BUS 11', 'capacity': 40, 'driver': 'Rashed Khan', 'route_name': 'Campus ⇄ Gulshan', 'time': time(9, 0)},
            {'number': '🌼 DIU BUS 12', 'capacity': 35, 'driver': 'Kamal Uddin', 'route_name': 'Campus ⇄ Gulshan', 'time': time(11, 30)},
            {'number': '🌼 DIU BUS 13', 'capacity': 40, 'driver': 'Jamal Ahmed', 'route_name': 'Campus ⇄ Gulshan', 'time': time(14, 0)},

            {'number': '🌼 DIU BUS 14', 'capacity': 35, 'driver': 'Tariq Rahman', 'route_name': 'Campus ⇄ Banani', 'time': time(9, 15)},
            {'number': '🌼 DIU BUS 15', 'capacity': 40, 'driver': 'Nasir Uddin', 'route_name': 'Campus ⇄ Banani', 'time': time(11, 45)},
            {'number': '🌼 DIU BUS 16', 'capacity': 35, 'driver': 'Faruk Ahmed', 'route_name': 'Campus ⇄ Banani', 'time': time(14, 15)},
        ]

        added_buses = 0
        for bus_data in new_buses:
            # Check if bus already exists
            existing = Bus.query.filter_by(bus_number=bus_data['number']).first()
            if not existing:
                # Get route ID by name
                route = Route.query.filter_by(route_name=bus_data['route_name']).first()
                if route:
                    bus = Bus(
                        bus_number=bus_data['number'],
                        capacity=bus_data['capacity'],
                        driver_name=bus_data['driver'],
                        route_id=route.route_id,
                        start_time=bus_data['time'],
                        status='active'
                    )
                    db.session.add(bus)
                    added_buses += 1
                    print(f"Added bus: {bus_data['number']} for route: {bus_data['route_name']}")

        db.session.commit()

        # Final counts
        final_routes = Route.query.count()
        final_buses = Bus.query.count()
        print("\nSummary:")
        print(f"Routes added: {added_routes} (Total: {final_routes})")
        print(f"Buses added: {added_buses} (Total: {final_buses})")
        print("\nTest data added successfully!")

if __name__ == '__main__':
    add_test_data()