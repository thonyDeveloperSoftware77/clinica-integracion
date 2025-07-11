# Dental Hospital - Incident Report Integration

## Overview

This module extends the Dental Hospital Management system with incident reporting functionality that integrates with Zammad ticketing system.

## Features

- **Patient Incident Reporting**: Patients can report incidents through a user-friendly form
- **Zammad Integration**: Automatic ticket creation in Zammad when incidents are submitted
- **User Authentication**: Supports Clerk SSO OpenID Connect authentication
- **Status Tracking**: Track incident status from draft to resolution
- **Priority Management**: Categorize incidents by priority (Low, Normal, High, Urgent)
- **Category Classification**: Classify incidents by type (Technical, Service, Billing, Appointment, Other)

## Configuration

### Zammad Setup

1. Go to **Settings > General Settings > Zammad Integration**
2. Configure the following parameters:
   - **Zammad URL**: Your Zammad instance URL (e.g., http://localhost:8080)
   - **Zammad API Token**: API token for authentication
   - **Default Group ID**: Default group ID for new tickets

### API Authentication

The module supports Zammad's Token Access authentication:

```bash
curl -H "Authorization: Token token=YOUR_TOKEN" http://localhost:8080/api/v1/groups
```

## Usage

### For Patients

1. Navigate to **Incident Reports > Report Incident**
2. Fill out the incident form:
   - **Title**: Brief description of the incident
   - **Category**: Select appropriate category
   - **Priority**: Set priority level
   - **Description**: Detailed description of the incident
3. Click **Submit Report** to create a ticket in Zammad

### For Administrators

1. Navigate to **Incident Reports > All Incidents** to view all reported incidents
2. Monitor ticket status and Zammad integration
3. Configure Zammad settings in system parameters

## Technical Details

### Models

- **incident.report**: Main model for incident reports
- **res.config.settings**: Extended for Zammad configuration

### API Integration

The module uses Zammad's REST API for:
- Creating tickets
- Managing customers
- Retrieving ticket information

### Security

- Portal users can create and view their own incidents
- Internal users can manage all incidents
- Proper access controls implemented

## Installation

1. Install the module dependencies:
   ```bash
   pip install requests
   ```

2. Update the module in Odoo:
   - Go to Apps
   - Search for "Dental Hospital Management"
   - Click Update

3. Configure Zammad integration in Settings

## Requirements

- Odoo 18.0+
- Python `requests` library
- Zammad instance with API access
- Clerk SSO OpenID Connect (for authentication)

## Support

For issues and questions, please create an incident report through the system or contact the development team.
