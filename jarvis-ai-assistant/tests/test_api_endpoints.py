"""
Tests for Flask API endpoints.
"""

import pytest
import json

from requests import patch
from jarvis.api.flask_server import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAPIEndpoints:
    
    def test_status_endpoint(self, client):
        response = client.get('/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'online'
        assert 'jarvis_name' in data
    
    def test_command_endpoint_success(self, client):
        with patch('jarvis.api.flask_server.remote_controller') as mock_rc:
            mock_rc.handle_remote_command.return_value = {
                "success": True,
                "action": "app_launch",
                "message": "Done!"
            }
            
            response = client.post('/command',
                data=json.dumps({"command": "open chrome"}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_command_endpoint_missing_field(self, client):
        response = client.post('/command',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_type_endpoint(self, client):
        with patch('jarvis.api.flask_server.remote_controller') as mock_rc:
            mock_rc.handle_type_command.return_value = {
                "success": True,
                "action": "type_text",
                "message": "Typed 5 chars!"
            }
            
            response = client.post('/type',
                data=json.dumps({"text": "hello"}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_ask_endpoint(self, client):
        with patch('jarvis.api.flask_server.ai_engine') as mock_ai:
            mock_ai.generate_reply.return_value = "Hello there!"
            
            response = client.post('/ask',
                data=json.dumps({"message": "hi"}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] == "Hello there!"
    
    def test_404_error(self, client):
        response = client.get('/nonexistent')
        assert response.status_code == 404