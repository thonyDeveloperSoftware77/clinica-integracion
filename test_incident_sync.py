#!/usr/bin/env python3
"""
Script to test the incident report functionality
"""

import requests
import json

def test_incident_sync():
    """Test that we can sync incident data properly"""
    
    # Zammad configuration
    zammad_url = 'http://172.17.0.1:8080'
    zammad_token = 'yYXUM8mJauxf74j5SaV0EPu7H-4ZhYRZUGSyfJ91rDqvMSfVUw_hIa33isD8TJR2'
    
    headers = {
        'Authorization': f'Token token={zammad_token}',
        'Content-Type': 'application/json'
    }
    
    print("=== Testing Zammad Connection ===")
    
    # Test connection
    try:
        response = requests.get(f'{zammad_url}/api/v1/tickets', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Connection to Zammad successful")
            tickets = response.json()
            print(f"Found {len(tickets)} tickets")
            
            # Test sync for a specific ticket
            if tickets:
                ticket = tickets[-1]  # Get last ticket
                ticket_id = ticket['id']
                
                print(f"\n=== Testing Sync for Ticket {ticket_id} ===")
                
                # Get ticket details
                ticket_response = requests.get(f'{zammad_url}/api/v1/tickets/{ticket_id}', headers=headers)
                if ticket_response.status_code == 200:
                    ticket_data = ticket_response.json()
                    print(f"Ticket Number: {ticket_data['number']}")
                    print(f"State ID: {ticket_data['state_id']}")
                    print(f"Title: {ticket_data['title']}")
                    
                    # Get articles
                    articles_response = requests.get(f'{zammad_url}/api/v1/ticket_articles/by_ticket/{ticket_id}', headers=headers)
                    if articles_response.status_code == 200:
                        articles = articles_response.json()
                        print(f"Articles: {len(articles)}")
                        
                        # Test the sync logic
                        state_id_mapping = {
                            1: 'new',
                            2: 'open', 
                            3: 'pending reminder',
                            4: 'closed',
                            5: 'merged',
                            6: 'pending close'
                        }
                        
                        state_mapping = {
                            'new': 'sent',
                            'open': 'in_progress',
                            'pending reminder': 'in_progress',
                            'pending close': 'in_progress',
                            'closed': 'closed',
                            'merged': 'closed'
                        }
                        
                        zammad_state_id = ticket_data.get('state_id', 1)
                        zammad_state_name = state_id_mapping.get(zammad_state_id, 'new')
                        new_state = state_mapping.get(zammad_state_name, 'sent')
                        
                        print(f"State mapping: {zammad_state_id} -> {zammad_state_name} -> {new_state}")
                        
                        # Test article formatting
                        formatted_responses = []
                        for article in articles:
                            article_type = article.get('type', 'note')
                            sender_type = article.get('sender', 'Agent')
                            is_internal = article.get('internal', False)
                            
                            if not is_internal and article_type in ['note', 'web', 'email']:
                                sender = article.get('from', 'Unknown')
                                created_at = article.get('created_at', '')
                                body = article.get('body', '')
                                
                                # Format the date
                                try:
                                    from datetime import datetime
                                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    formatted_date = created_at
                                
                                # Clean HTML from body if present
                                import re
                                if article.get('content_type') == 'text/html':
                                    body_clean = re.sub(r'<[^>]+>', '', body)
                                    body_clean = body_clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()
                                else:
                                    body_clean = body.strip()
                                
                                if body_clean:
                                    sender_display = f"{sender} ({sender_type})"
                                    formatted_responses.append(
                                        f"=== {sender_display} - {formatted_date} ===\n{body_clean}\n"
                                    )
                        
                        print(f"\nFormatted conversation:")
                        print("="*50)
                        for response in formatted_responses:
                            print(response)
                        print("="*50)
                        
                        print("✅ Sync logic test successful")
                    else:
                        print(f"❌ Failed to get articles: {articles_response.status_code}")
                else:
                    print(f"❌ Failed to get ticket details: {ticket_response.status_code}")
            else:
                print("No tickets found to test")
                
        else:
            print(f"❌ Failed to connect to Zammad: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

if __name__ == "__main__":
    test_incident_sync()
