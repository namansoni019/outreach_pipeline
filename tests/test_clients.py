"""
Tests for API clients with mocked HTTP responses via respx.
"""

from __future__ import annotations

import httpx
import respx
import pytest

from outreach.stages.prospeo import ProspeoClient
from outreach.stages.brevo import BrevoClient
from outreach.models import EmailDraft


@respx.mock
def test_prospeo_pagination():
    """Verify ProspeoClient iterates pages correctly until limit is hit or no results."""
    # Mock page 1: 5 results
    respx.post("https://api.prospeo.io/search-person").mock(
        side_effect=[
            httpx.Response(
                200, 
                json={"results": [{"name": f"P1_{i}", "title": "VP", "linkedin_url": "url"} for i in range(5)]}
            ),
            httpx.Response(
                200, 
                json={"results": [{"name": f"P2_{i}", "title": "VP", "linkedin_url": "url"} for i in range(3)]}
            ),
            httpx.Response(200, json={"results": []})  # Page 3 empty
        ]
    )

    client = ProspeoClient(api_key="test-key")
    
    # Should fetch all 8 results across 2 pages and stop at empty page
    results = client.find_decision_makers("example.com", limit_per_company=10)
    assert len(results) == 8
    assert results[0].full_name == "P1_0"
    assert results[5].full_name == "P2_0"
    
    # Check calls
    calls = respx.calls
    assert len(calls) == 3
    
    # Test early stopping when limit is reached
    respx.clear()
    respx.calls.clear()
    respx.post("https://api.prospeo.io/search-person").mock(
        side_effect=[
            httpx.Response(
                200, 
                json={"results": [{"name": f"P1_{i}", "title": "VP", "linkedin_url": "url"} for i in range(5)]}
            ),
            httpx.Response(
                200, 
                json={"results": [{"name": f"P2_{i}", "title": "VP", "linkedin_url": "url"} for i in range(5)]}
            )
        ]
    )
    
    results = client.find_decision_makers("example.com", limit_per_company=7)
    assert len(results) == 7  # Limited to 7
    # Should only make 2 calls
    calls = respx.calls
    assert len(calls) == 2


@respx.mock
def test_brevo_payload_structure():
    """Verify BrevoClient sends correctly structured payload."""
    
    def check_payload(request):
        payload = request.read().decode("utf-8")
        import json
        data = json.loads(payload)
        
        assert data["sender"]["email"] == "sender@example.com"
        assert data["sender"]["name"] == "Test Sender"
        assert data["to"][0]["email"] == "target@example.com"
        assert data["to"][0]["name"] == "Target Name"
        assert data["subject"] == "Test Subject"
        assert data["textContent"] == "Test Body"
        
        return httpx.Response(200, json={"messageId": "msg-123"})

    respx.post("https://api.brevo.com/v3/smtp/email").mock(side_effect=check_payload)
    
    client = BrevoClient(api_key="test-key", sender_email="sender@example.com", sender_name="Test Sender")
    
    draft = EmailDraft(
        to_email="target@example.com",
        subject="Test Subject",
        body="Test Body",
        contact_name="Target Name",
        company_domain="example.com"
    )
    
    result = client.send_email(draft)
    
    assert result.status == "sent"
    assert result.provider_message_id == "msg-123"
    assert len(respx.calls) == 1
