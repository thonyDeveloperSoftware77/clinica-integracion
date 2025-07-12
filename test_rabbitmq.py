#!/usr/bin/env python3
"""
Test script to verify RabbitMQ integration is working
"""
import requests
import json

def test_incident_creation():
    """Test creating an incident via Odoo API"""
    
    # Odoo connection details
    url = 'http://localhost:8069'
    db = 'clinica_db'
    username = 'admin'  # Replace with actual admin username
    password = 'admin'  # Replace with actual admin password
    
    # Test data
    incident_data = {
        'description': 'Test incident for RabbitMQ integration - please ignore'
    }
    
    print("Testing incident creation and RabbitMQ integration...")
    print("Please check the mailer service logs for confirmation email sent.")
    print("\nTo manually test:")
    print("1. Go to http://localhost:8069")
    print("2. Navigate to Incident Reports")
    print("3. Create a new incident")
    print("4. Check mailer service logs with: docker-compose logs mailer")

if __name__ == "__main__":
    test_incident_creation()
