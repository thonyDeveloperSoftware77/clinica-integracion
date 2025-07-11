#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test prescription appointment selection directly in Odoo
"""

# This script should be run inside the Odoo shell: odoo-bin shell -d your_database

import datetime
from datetime import timedelta

def test_prescription_appointment_logic():
    """Test the prescription appointment logic directly"""
    
    # Get the environment
    env = self.env if hasattr(self, 'env') else None
    if not env:
        print("This script should be run inside the Odoo shell")
        return
    
    print("=== Testing Prescription Appointment Logic ===")
    
    # Check if we have appointment data
    appointments = env['dental.appointment'].search([])
    print(f"Total appointments in database: {len(appointments)}")
    
    for apt in appointments:
        print(f"  - {apt.appointment_no}: {apt.patient_id.name} on {apt.appointment_date} ({apt.state})")
    
    # Check if we have patients
    patients = env['res.partner'].search([('is_patient', '=', True)])
    print(f"\nTotal patients in database: {len(patients)}")
    
    for patient in patients:
        print(f"  - {patient.name} (ID: {patient.id})")
    
    # Test the prescription logic
    if patients:
        test_patient = patients[0]
        print(f"\n=== Testing with patient: {test_patient.name} ===")
        
        # Create a mock prescription record to test the logic
        prescription = env['dental.prescription'].new({
            'patient_id': test_patient.id,
        })
        
        # Test the compute method
        prescription._compute_appointment_ids()
        
        print(f"Available appointments for {test_patient.name}:")
        for apt_id in prescription.appointment_ids:
            apt = env['dental.appointment'].browse(apt_id)
            print(f"  - {apt.appointment_no}: {apt.appointment_date} ({apt.state})")
        
        # Test without patient
        prescription2 = env['dental.prescription'].new({})
        prescription2._compute_appointment_ids()
        
        print(f"\nAvailable appointments (no patient selected):")
        for apt_id in prescription2.appointment_ids:
            apt = env['dental.appointment'].browse(apt_id)
            print(f"  - {apt.appointment_no}: {apt.patient_id.name} on {apt.appointment_date} ({apt.state})")

if __name__ == '__main__':
    test_prescription_appointment_logic()
