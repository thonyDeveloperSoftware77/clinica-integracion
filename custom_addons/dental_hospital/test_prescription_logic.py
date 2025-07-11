#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose prescription appointment selection issue
"""

# Simulate the prescription logic
import datetime
from datetime import timedelta

# Test data
today = datetime.date.today()
test_appointments = [
    {'id': 1, 'patient_id': 1, 'appointment_date': today - timedelta(days=1), 'state': 'done'},
    {'id': 2, 'patient_id': 1, 'appointment_date': today, 'state': 'confirmed'},
    {'id': 3, 'patient_id': 1, 'appointment_date': today + timedelta(days=7), 'state': 'confirmed'},
    {'id': 4, 'patient_id': 2, 'appointment_date': today + timedelta(days=3), 'state': 'draft'},
    {'id': 5, 'patient_id': 1, 'appointment_date': today - timedelta(days=45), 'state': 'done'},  # Too old
    {'id': 6, 'patient_id': 1, 'appointment_date': today - timedelta(days=15), 'state': 'cancelled'},  # Cancelled
]

def test_appointment_domain(patient_id=None):
    """Test the appointment domain logic"""
    print(f"Testing appointment domain for patient_id: {patient_id}")
    print(f"Today: {today}")
    
    # Base domain: exclude cancelled appointments
    domain = [('state', '!=', 'cancelled')]
    
    # If a patient is already selected, filter by patient
    if patient_id:
        domain.append(('patient_id', '=', patient_id))
    
    # Date filter: appointments from last 30 days to future
    cutoff_date = today - timedelta(days=30)
    domain.append(('appointment_date', '>=', cutoff_date))
    
    print(f"Domain: {domain}")
    print(f"Cutoff date: {cutoff_date}")
    
    # Simulate search
    filtered_appointments = []
    for apt in test_appointments:
        include = True
        
        # Check state
        if apt['state'] == 'cancelled':
            include = False
            
        # Check patient
        if patient_id and apt['patient_id'] != patient_id:
            include = False
            
        # Check date
        if apt['appointment_date'] < cutoff_date:
            include = False
            
        if include:
            filtered_appointments.append(apt)
    
    print(f"Filtered appointments: {filtered_appointments}")
    print(f"Found {len(filtered_appointments)} appointments")
    return filtered_appointments

# Test scenarios
print("=== Test 1: All appointments (no patient selected) ===")
test_appointment_domain()

print("\n=== Test 2: Patient 1 appointments ===")
test_appointment_domain(patient_id=1)

print("\n=== Test 3: Patient 2 appointments ===")
test_appointment_domain(patient_id=2)
