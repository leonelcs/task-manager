#!/usr/bin/env python3
"""
Debug script to test task creation with comprehensive logging.
This will help identify where the task creation process is failing.
"""
import requests
import json
import logging
from datetime import datetime
import sys # Added
import os # Added

# Add the parent directory (task-manager) to sys.path to find generate_test_token
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))) # Added
from generate_test_token import generate_test_token # Added

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_task_creation():
    """Test the complete task creation flow"""
    
    logger.info("🧪 Starting task creation debug test - POST and GET /api/tasks") # Modified
    logger.info("="*60)
    
    # Step 1: Test health endpoint (Commented out for now)
    # logger.info("1️⃣ Testing health endpoint...")
    # try:
    #     response = requests.get(f"{BASE_URL}/health")
    #     logger.info(f"Health check: {response.status_code} - {response.text}")
    #     if response.status_code != 200:
    #         logger.error("❌ Health check failed!")
    #         return
    # except Exception as e:
    #     logger.error(f"❌ Cannot connect to API: {e}")
    #     return
    
    # Step 2: Check if we need authentication (Commented out for now)
    # logger.info("2️⃣ Testing unauthenticated task creation...")
    # task_data = {
    #     "title": "Debug Test Task",
    #     "description": "Testing task creation with debug logging",
    #     "priority": "medium",
    #     "task_type": "project",
    #     "impact_size": "pebbles",
    #     "estimated_duration": 30
    # }
    # 
    # try:
    #     response = requests.post(
    #         f"{BASE_URL}/api/tasks",
    #         json=task_data,
    #         headers={"Content-Type": "application/json"},
    #         allow_redirects=False  # Prevent automatic redirection
    #     )
    #     logger.info(f"Unauthenticated request: {response.status_code}")
    #     logger.info(f"Response Headers: {response.headers}") # Log all headers
    #     # Always log raw response text for debugging
    #     logger.info(f"Raw Response Text for unauthenticated request: {response.text}")
    #
    #     if response.status_code == 401:
    #         logger.info("✅ Authentication is required (as expected)")
    #     elif response.status_code == 422:
    #         logger.error("❌ Validation error (422) received during unauthenticated task creation.")
    #         try:
    #             error_detail = response.json()
    #             logger.error(f"Validation error details (JSON): {json.dumps(error_detail, indent=2)}")
    #         except json.JSONDecodeError:
    #             logger.error("❌ Failed to parse JSON from 422 response. Raw text was logged above.")
    #     elif response.status_code == 307:
    #         location = response.headers.get('Location')
    #         logger.warning(f"⚠️ Received 307 Temporary Redirect. Location: {location}")
    #     else:
    #         logger.warning(f"⚠️ Unexpected status code: {response.status_code}")
    #         
    # except Exception as e:
    #     logger.error(f"❌ Request failed: {e}")
    
    # Step 3: Generate a real token and test authenticated task creation (POST)
    logger.info("3️⃣ Generating real token and testing authenticated POST to /api/tasks...") # Modified log message
    token, user_id = generate_test_token()

    if not token:
        logger.error("❌ Failed to generate a real token. Halting authenticated test.")
        return 
    else:
        logger.info(f"🔑 Successfully obtained token for user_id: {user_id}")
        
        # (POST /api/tasks - Re-enabled)
        authenticated_task_data = {
            "title": f"Authenticated Test Task - {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "Testing authenticated task creation with a real token.",
            "priority": "high",
            "task_type": "project", 
            "impact_size": "boulders", 
            "estimated_duration": 60,
        }
        
        try:
            logger.info(f"Attempting POST to {BASE_URL}/api/tasks with token.")
            response = requests.post(
                f"{BASE_URL}/api/tasks", 
                json=authenticated_task_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                allow_redirects=False 
            )
            logger.info(f"Authenticated POST /api/tasks status: {response.status_code}")
            logger.info(f"Authenticated POST /api/tasks Headers: {response.headers}")
            logger.info(f"Authenticated POST /api/tasks Text: {response.text}")

            if response.status_code == 201 or response.status_code == 200: # 201 is more typical for creation
                logger.info("✅ Authenticated task creation (POST) successful!")
                try:
                    logger.info(f"Response JSON: {json.dumps(response.json(), indent=2)}")
                except json.JSONDecodeError:
                    logger.info("Response was not JSON, raw text logged above.")
            elif response.status_code == 422:
                logger.error("❌ Validation error (422) received during authenticated task creation (POST).")
                try:
                    error_detail = response.json()
                    logger.error(f"Validation error details (JSON): {json.dumps(error_detail, indent=2)}")
                except json.JSONDecodeError:
                    logger.error("❌ Failed to parse JSON from 422 response. Raw text was logged above.")
            elif response.status_code == 307:
                location = response.headers.get('Location')
                logger.warning(f"⚠️ Received 307 Temporary Redirect for authenticated POST /api/tasks. Location: {location}")
                logger.warning("This might indicate an issue with trailing slashes or HTTP/HTTPS for POST requests.")
            elif response.status_code == 401:
                logger.error("❌ Received 401 Unauthorized for POST /api/tasks even with a token. Check token validity or auth logic.")
            else:
                logger.warning(f"⚠️ Unexpected status code for authenticated POST /api/tasks: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Request for POST /api/tasks failed: {e}")

    # Step 4: Test GET /api/tasks with authentication
    logger.info("4️⃣ Testing GET /api/tasks with authentication...")
    if not token:
        logger.warning("⚠️ Skipping GET /api/tasks as token generation failed earlier.")
    else:
        try:
            logger.info(f"Attempting GET to {BASE_URL}/api/tasks with token.")
            response = requests.get(
                f"{BASE_URL}/api/tasks", # Ensure this is the correct endpoint
                headers={
                    "Authorization": f"Bearer {token}"
                },
                allow_redirects=False # Keep this to observe redirects
            )
            logger.info(f"Authenticated GET /api/tasks status: {response.status_code}")
            logger.info(f"Authenticated GET /api/tasks Headers: {response.headers}")
            logger.info(f"Authenticated GET /api/tasks Text: {response.text}")

            if response.status_code == 200:
                logger.info("✅ Authenticated GET /api/tasks successful!")
                try:
                    logger.info(f"Response JSON: {json.dumps(response.json(), indent=2)}")
                except json.JSONDecodeError:
                    logger.info("Response was not JSON, raw text logged above.")
            elif response.status_code == 307:
                location = response.headers.get('Location')
                logger.warning(f"⚠️ Received 307 Temporary Redirect for authenticated GET /api/tasks. Location: {location}")
                # Attempt to follow the redirect once
                if location:
                    logger.info(f"Attempting to follow redirect to: {location}")
                    # Ensure the location is a full URL if it's relative
                    if location.startswith('/'):
                        redirect_url = f"{BASE_URL}{location}"
                    else:
                        redirect_url = location
                    
                    response_redirected = requests.get(
                        redirect_url,
                        headers={"Authorization": f"Bearer {token}"},
                        allow_redirects=False # To see if there's another redirect
                    )
                    logger.info(f"Redirected GET /api/tasks status: {response_redirected.status_code}")
                    logger.info(f"Redirected GET /api/tasks Headers: {response_redirected.headers}")
                    logger.info(f"Redirected GET /api/tasks Text: {response_redirected.text}")
                    if response_redirected.status_code == 200:
                         logger.info("✅ Authenticated GET /api/tasks successful after following redirect!")
                         try:
                             logger.info(f"Response JSON: {json.dumps(response_redirected.json(), indent=2)}")
                         except json.JSONDecodeError:
                             logger.info("Response was not JSON, raw text logged above.")
                    else:
                        logger.warning(f"⚠️ GET /api/tasks failed even after following redirect. Status: {response_redirected.status_code}")
            elif response.status_code == 401:
                logger.error("❌ Received 401 Unauthorized for GET /api/tasks even with a token.")
            else:
                logger.warning(f"⚠️ Unexpected status code for authenticated GET /api/tasks: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Request for GET /api/tasks failed: {e}")

    # Step 5: Test with fake authorization (Commented out for now)
    # logger.info("5️⃣ Testing with fake authorization header...")
    # try:
    #     response = requests.post(
    #         f"{BASE_URL}/api/tasks",
    #         json=task_data, # task_data would be undefined here if step 2 is commented, ensure it's defined or this step is fully commented
    #         headers={
    #             "Content-Type": "application/json",
    #             "Authorization": "Bearer fake-token-for-testing"
    #         }
    #     )
    #     logger.info(f"Fake auth request: {response.status_code}")
    #     logger.info(f"Response: {response.text}")
    #     
    # except Exception as e:
    #     logger.error(f"❌ Request with fake auth failed: {e}")
    
    # Step 6: Check available endpoints (Commented out for now)
    # logger.info("6️⃣ Checking available endpoints...")
    # try:
    #     response = requests.get(f"{BASE_URL}/docs")
    #     if response.status_code == 200:
    #         logger.info("✅ API docs available at /docs")
    #     else:
    #         logger.info(f"API docs status: {response.status_code}")
    #         
    #     # Try OpenAPI JSON
    #     response = requests.get(f"{BASE_URL}/openapi.json")
    #     if response.status_code == 200:
    #         logger.info("✅ OpenAPI spec available")
    #     else:
    #         logger.info(f"OpenAPI spec status: {response.status_code}")
    #         
    # except Exception as e:
    #     logger.error(f"❌ Error checking docs: {e}")
    
    # Step 7: Test authentication endpoints (Commented out for now)
    # logger.info("7️⃣ Testing authentication endpoints...")
    # auth_endpoints = [
    #     "/api/auth/google/login",
    #     "/api/auth/me"
    # ]
    # 
    # for endpoint in auth_endpoints:
    #     try:
    #         response = requests.get(f"{BASE_URL}{endpoint}")
    #         logger.info(f"Auth endpoint {endpoint}: {response.status_code}")
    #         if response.status_code == 302:
    #             location = response.headers.get('Location', 'No Location header')
    #             logger.info(f"  Redirects to: {location}")
    #     except Exception as e:
    #         logger.error(f"❌ Error testing {endpoint}: {e}")
    
    logger.info("="*60)
    logger.info("🧪 Debug test completed")

if __name__ == "__main__":
    test_task_creation()
