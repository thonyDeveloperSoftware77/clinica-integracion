#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to verify the dental hospital module setup
"""

import sys
import os

def check_module_files():
    """Check that all required files exist"""
    base_path = "/home/thony/Projects/UNIVERSITY/SEMESTRE 9/Integracion/clinica-integracion/custom_addons/dental_hospital"
    
    required_files = [
        "models/dental_prescription.py",
        "models/dental_appointment.py",
        "views/dental_prescription_views.xml",
        "data/sample_appointments.xml",
        "security/ir.model.access.csv",
        "__manifest__.py"
    ]
    
    print("=== Checking Required Files ===")
    for file in required_files:
        full_path = os.path.join(base_path, file)
        if os.path.exists(full_path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NOT FOUND")
    
    print("\n=== Checking Model Definitions ===")
    
    # Check prescription model
    prescription_path = os.path.join(base_path, "models/dental_prescription.py")
    if os.path.exists(prescription_path):
        with open(prescription_path, 'r') as f:
            content = f.read()
            if "_compute_appointment_ids" in content:
                print("✅ _compute_appointment_ids method found")
            else:
                print("❌ _compute_appointment_ids method NOT found")
                
            if "_onchange_patient_id" in content:
                print("✅ _onchange_patient_id method found")
            else:
                print("❌ _onchange_patient_id method NOT found")
    
    # Check appointment model
    appointment_path = os.path.join(base_path, "models/dental_appointment.py")
    if os.path.exists(appointment_path):
        with open(appointment_path, 'r') as f:
            content = f.read()
            if "name_get" in content:
                print("✅ name_get method found in appointment model")
            else:
                print("❌ name_get method NOT found in appointment model")
                
            if "name_search" in content:
                print("✅ name_search method found in appointment model")
            else:
                print("❌ name_search method NOT found in appointment model")
    
    print("\n=== Checking Sample Data ===")
    sample_data_path = os.path.join(base_path, "data/sample_appointments.xml")
    if os.path.exists(sample_data_path):
        with open(sample_data_path, 'r') as f:
            content = f.read()
            if "sample_appointment_1" in content:
                print("✅ Sample appointments data found")
            else:
                print("❌ Sample appointments data NOT found")
    
    print("\n=== Checking Manifest ===")
    manifest_path = os.path.join(base_path, "__manifest__.py")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            content = f.read()
            if "sample_appointments.xml" in content:
                print("✅ Sample appointments included in manifest")
            else:
                print("❌ Sample appointments NOT included in manifest")

if __name__ == "__main__":
    check_module_files()
