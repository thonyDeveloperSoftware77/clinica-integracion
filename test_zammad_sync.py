#!/usr/bin/env python3
"""
Test script to verify Zammad sync functionality
"""

import requests
import json
from datetime import datetime
import re

def test_zammad_sync():
    """Test the Zammad sync functionality"""
    
    # Zammad configuration
    zammad_url = 'http://172.17.0.1:8080'
    zammad_token = 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2'
    
    headers = {
        'Authorization': f'Token token={zammad_token}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Get ticket states
    print("=== Testing Ticket States ===")
    states_response = requests.get(f'{zammad_url}/api/v1/ticket_states', headers=headers)
    if states_response.status_code == 200:
        states = states_response.json()
        state_mapping = {state['id']: state['name'] for state in states}
        print("State mapping:", state_mapping)
    else:
        print(f"Failed to get states: {states_response.status_code}")
        return
    
    # Test 2: Get tickets
    print("\n=== Testing Tickets ===")
    tickets_response = requests.get(f'{zammad_url}/api/v1/tickets', headers=headers)
    if tickets_response.status_code == 200:
        tickets = tickets_response.json()
        if tickets:
            ticket = tickets[0]  # Get first ticket
            print(f"Ticket ID: {ticket['id']}")
            print(f"Number: {ticket['number']}")
            print(f"State ID: {ticket['state_id']} -> {state_mapping.get(ticket['state_id'], 'Unknown')}")
            print(f"Title: {ticket['title']}")
            
            # Test 3: Get articles for this ticket
            print(f"\n=== Testing Articles for Ticket {ticket['id']} ===")
            articles_response = requests.get(
                f"{zammad_url}/api/v1/ticket_articles/by_ticket/{ticket['id']}", 
                headers=headers
            )
            if articles_response.status_code == 200:
                articles = articles_response.json()
                print(f"Found {len(articles)} articles")
                
                for i, article in enumerate(articles):
                    print(f"\nArticle {i+1}:")
                    print(f"  From: {article.get('from', 'Unknown')}")
                    print(f"  Type: {article.get('type', 'Unknown')}")
                    print(f"  Sender: {article.get('sender', 'Unknown')}")
                    print(f"  Internal: {article.get('internal', False)}")
                    print(f"  Content-Type: {article.get('content_type', 'Unknown')}")
                    print(f"  Created: {article.get('created_at', 'Unknown')}")
                    
                    # Test date formatting
                    created_at = article.get('created_at', '')
                    if created_at:
                        try:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                            print(f"  Formatted Date: {formatted_date}")
                        except Exception as e:
                            print(f"  Date formatting error: {e}")
                    
                    # Test body cleaning
                    body = article.get('body', '')
                    if body:
                        if article.get('content_type') == 'text/html':
                            body_clean = re.sub(r'<[^>]+>', '', body)
                            body_clean = body_clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()
                        else:
                            body_clean = body.strip()
                        print(f"  Body (first 100 chars): {body_clean[:100]}...")
            else:
                print(f"Failed to get articles: {articles_response.status_code}")
        else:
            print("No tickets found")
    else:
        print(f"Failed to get tickets: {tickets_response.status_code}")

if __name__ == "__main__":
    test_zammad_sync()
