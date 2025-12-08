"""
Tests para autenticación
"""
import pytest
import json


def test_registro_exitoso(client):
    """Test registro de usuario exitoso"""
    response = client.post('/register', json={
        'nombre': 'New User',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['usuario']['nombre'] == 'New User'
    assert data['usuario']['email'] == 'newuser@example.com'


def test_registro_email_duplicado(client, usuario):
    """Test registro con email duplicado"""
    response = client.post('/register', json={
        'nombre': 'Another User',
        'email': usuario.email,
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_registro_password_corto(client):
    """Test registro con contraseña corta"""
    response = client.post('/register', json={
        'nombre': 'User',
        'email': 'user@example.com',
        'password': '123'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_login_exitoso(client, usuario):
    """Test login exitoso"""
    response = client.post('/login', json={
        'email': usuario.email,
        'password': 'testpass123'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['usuario']['email'] == usuario.email


def test_login_password_incorrecta(client, usuario):
    """Test login con contraseña incorrecta"""
    response = client.post('/login', json={
        'email': usuario.email,
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_login_email_inexistente(client):
    """Test login con email inexistente"""
    response = client.post('/login', json={
        'email': 'noexiste@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_logout(auth_client):
    """Test logout"""
    response = auth_client.post('/logout')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
