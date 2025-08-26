"""
Simple test to verify the application starts and basic endpoints work
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import_main():
    """Test that main module can be imported"""
    try:
        from app.main import app
        print("✅ Successfully imported main app")
        return True
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
        return False

def test_import_services():
    """Test that services can be imported"""
    try:
        from app.services.ai_orchestrator import AIOrchestrator
        from app.services.document_processor import DocumentProcessor
        from app.services.security_manager import SecurityManager
        print("✅ Successfully imported all services")
        return True
    except Exception as e:
        print(f"❌ Failed to import services: {e}")
        return False

def test_import_models():
    """Test that models can be imported"""
    try:
        from app.models.schemas import UserModel, DocumentAnalysisRequest
        print("✅ Successfully imported models")
        return True
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        return False

def test_app_creation():
    """Test that FastAPI app can be created"""
    try:
        from app.main import app
        
        # Check if app has required attributes
        assert hasattr(app, 'title')
        assert hasattr(app, 'version')
        assert app.title == "Legal Assistant GenAI"
        assert app.version == "1.5.0"
        
        print("✅ FastAPI app created successfully")
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        return True
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.5.0"
        
        print("✅ Health endpoint works correctly")
        print(f"   Response: {data}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic application tests...\n")
    
    tests = [
        test_import_main,
        test_import_services,
        test_import_models,
        test_app_creation,
        test_health_endpoint
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Application is ready.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above.")
        sys.exit(1)