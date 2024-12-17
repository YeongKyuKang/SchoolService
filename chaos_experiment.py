import requests
import time
import random
import logging
from requests.exceptions import RequestException
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, verify_jwt_in_request

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 및 JWTManager 설정

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'  # 실제 운영 환경에서는 안전하게 관리해야 합니다
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 운영 환경에서는 True로 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

BASE_URL = "http://localhost:5001"  # 환경에 맞게 조정

used_ids = set()
used_student_ids = set()
used_emails = set()
used_phone_numbers = set()

def generate_student_data():
    attempts = 0
    while True:
        attempts += 1
        id = random.randint(1000, 9999)
        student_id = f"{random.randint(10000000, 99999999)}"
        email = f"student{random.randint(1, 9999)}@example.com"
        phone_number = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        if id not in used_ids and student_id not in used_student_ids and \
           email not in used_emails and phone_number not in used_phone_numbers:
            used_ids.add(id)
            used_student_ids.add(student_id)
            used_emails.add(email)
            used_phone_numbers.add(phone_number)
            
            student_data = {
                "id": id,
                "student_id": student_id,
                "name": f"Student {random.randint(1, 100)}",
                "email": email,
                "phone_number": phone_number,
                "department": random.choice(["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Business Administration"])
            }
            
            return student_data
        
        if attempts >= 1000:
            raise RuntimeError("Unable to generate unique student data")

def generate_jwt_token(user_id):
    logger.info(f"Attempting to generate JWT token for user_id: {user_id}")
    try:
        with app.app_context():
            access_token = create_access_token(identity=str(user_id))
        logger.info(f"JWT token successfully generated for user_id: {user_id}")
        logger.debug(f"Token preview: {access_token[:20]}...")
        return access_token
    except Exception as e:
        logger.error(f"JWT token generation failed: {str(e)}")
        logger.exception("Detailed traceback:")
        raise

def set_access_token_cookie(response, token):
    """
    응답 객체에 access_token_cookie를 설정합니다.
    """
    with app.app_context():
        set_access_cookies(response, token)
    logger.info("access_token_cookie가 응답 객체에 설정되었습니다.")

def get_student_with_token():
    try:
        student = random.choice(students)
        token = generate_jwt_token(student['id'])
        response = make_response(jsonify({'message': 'Token generated'}))
        set_access_token_cookie(response, token)
        return student, response
    except Exception as e:
        logger.error(f"Error in get_student_with_token: {str(e)}")
        raise

students = [generate_student_data() for _ in range(10)]

def check_system_health():
    try:
        student, response = get_student_with_token()
        cookies = response.headers.get('Set-Cookie')

        headers = {'Cookie': cookies} if cookies else {}
        response = requests.get(f"{BASE_URL}/api/search_courses", headers=headers)
        
        if response.status_code == 200:
            logger.info("System health check successful")
            return True
        else:
            logger.error(f"System health check failed with status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during system health check: {str(e)}")
        return False

def fetch_dropdown_options(headers):
    logger.info("Starting to fetch dropdown options")
    try:
        url = f"{BASE_URL}/api/dropdown_options"
        logger.debug(f"Sending GET request to {url}")
        logger.debug(f"Request headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        logger.debug(f"Received response with status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
    
        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug(f"Response data: {data}")
                
                if data.get("success"):
                    credits = data.get("credits")
                    departments = data.get("departments")
                    logger.info(f"Successfully fetched dropdown options. Credits: {credits}, Departments: {departments}")
                    return credits, departments
                else:
                    logger.warning(f"API request was successful, but 'success' flag in response was False. Message: {data.get('message', 'No message provided')}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response content: {response.text}")
        else:
            logger.error(f"Failed to fetch dropdown options. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
        
        logger.error("Failed to fetch dropdown options")
        return None, None
    except RequestException as e:
        logger.error(f"Network error occurred while fetching dropdown options: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching dropdown options: {str(e)}")
        return None, None
        
def search_courses(headers, credits=None, department=None, course_name=None):
    params = {}
    if credits:
        params['credits'] = credits
    if department:
        params['department'] = department
    if course_name:
        params['course_name'] = course_name
    
    response = requests.get(f"{BASE_URL}/api/search_courses", params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info(f"Found {len(data.get('courses', []))} courses")
            return data.get("courses")
    logger.error("Failed to search courses")
    return []

def apply_course(headers, course_key):
    logger.info(f"Applying for course: {course_key}")
    response = requests.post(f"{BASE_URL}/api/apply_course", json={"course_key": course_key}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Course application successful")
            return True
    logger.error("Course application failed")
    return False

def cancel_course(headers, course_key):
    logger.info(f"Cancelling course: {course_key}")
    response = requests.post(f"{BASE_URL}/api/cancel_course", json={"course_key": course_key}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Course cancellation successful")
            return True
    logger.error("Course cancellation failed")
    return False

def simulate_course_registration():
    logger.info("Starting course registration simulation")
    try:
        with app.app_context():
            student, response = get_student_with_token()
            cookies = response.headers.get('Set-Cookie')
            headers = {'Cookie': cookies} if cookies else {}

            logger.info("Fetching dropdown options")
            credits, departments = fetch_dropdown_options(headers)
            if not credits or not departments:
                logger.error("Failed to fetch dropdown options")
                return False
            logger.debug(f"Fetched credits: {credits}, departments: {departments}")

            selected_credits = random.choice(credits)
            selected_department = random.choice(departments)
            logger.info(f"Selected credits: {selected_credits}, department: {selected_department}")

            logger.info("Searching for courses")
            courses = search_courses(headers, credits=selected_credits, department=selected_department)
            if not courses:
                logger.error("No courses found for selected criteria")
                return False
            logger.debug(f"Found {len(courses)} courses")

            selected_course = random.choice(courses)
            logger.info(f"Selected course: {selected_course['course_key']}")

            logger.info(f"Attempting to apply for course: {selected_course['course_key']}")
            if apply_course(headers, selected_course['course_key']):
                logger.info(f"Successfully applied for course: {selected_course['course_key']}")
                time.sleep(random.uniform(0.5, 2))  # Simulate some time passing
                if random.random() < 0.3:  # 30% chance to cancel the course
                    logger.info(f"Attempting to cancel course: {selected_course['course_key']}")
                    cancel_result = cancel_course(headers, selected_course['course_key'])
                    logger.info(f"Course cancellation result: {'Success' if cancel_result else 'Failed'}")
                    return cancel_result
                return True
            else:
                logger.error(f"Failed to apply for course: {selected_course['course_key']}")
                return False
    except Exception as e:
        logger.exception(f"Unexpected error in simulate_course_registration: {str(e)}")
        return False
    finally:
        logger.info("Course registration simulation completed")

def simulate_concurrent_registrations(num_concurrent=10):
    logger.info(f"Starting simulation of {num_concurrent} concurrent course registrations")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        logger.debug(f"Created ThreadPoolExecutor with {num_concurrent} workers")
        futures = [executor.submit(simulate_course_registration) for _ in range(num_concurrent)]
        logger.debug(f"Submitted {num_concurrent} course registration tasks")
        
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                logger.debug(f"Task completed with result: {result}")
            except Exception as e:
                logger.exception(f"Task failed with exception: {str(e)}")
                results.append(False)
    
    end_time = time.time()
    duration = end_time - start_time
    
    successful_registrations = sum(1 for result in results if result)
    logger.info(f"Concurrent registration test completed: {successful_registrations}/{num_concurrent} successful")
    logger.info(f"Total time taken for concurrent registrations: {duration:.2f} seconds")
    logger.info(f"Average time per registration: {duration/num_concurrent:.2f} seconds")
    
    return successful_registrations == num_concurrent

def inject_network_delay(headers):
    logger.info("Injecting network delay...")
    original_get = requests.get
    original_post = requests.post

    def delayed_request(method, *args, **kwargs):
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        return method(*args, **kwargs)

    requests.get = lambda *args, **kwargs: delayed_request(original_get, *args, **kwargs)
    requests.post = lambda *args, **kwargs: delayed_request(original_post, *args, **kwargs)

    # Test the delay
    start_time = time.time()
    fetch_dropdown_options(headers)
    end_time = time.time()

    requests.get = original_get
    requests.post = original_post

    if end_time - start_time > 1:
        logger.info("Network delay injection successful")
        return True
    else:
        logger.error("Network delay injection failed")
        return False

def simulate_high_load():
    logger.info("Simulating high load...")
    num_requests = 50
    successful_requests = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_course_registration) for _ in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    successful_requests = sum(1 for result in results if result)
    logger.info(f"High load test: {successful_requests}/{num_requests} successful")
    return successful_requests > num_requests * 0.8  # Consider success if 80% of requests succeed

def wait_for_recovery(timeout=30, interval=5):
    logger.info(f"Waiting for system to recover (timeout: {timeout}s)...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_system_health():
            logger.info("System recovered successfully")
            return True
        time.sleep(interval)
    logger.error("System failed to recover within the timeout period")
    return False

def run_chaos_experiment():
    logger.info("Starting chaos engineering experiment for course_service")
    
    with app.app_context():
        if not check_system_health():
            logger.error("System is not healthy at the start. Aborting experiment.")
            return
        
        # Test 1: Concurrent Registrations
        if not simulate_concurrent_registrations(20):
            logger.error("System failed to handle concurrent registrations properly")
            if not wait_for_recovery():
                return

        # Test 2: Network Delay
        student, response = get_student_with_token()
        cookies = response.headers.get('Set-Cookie')
        headers = {'Cookie': cookies} if cookies else {}

        if inject_network_delay(headers):
            if not wait_for_recovery():
                logger.error("System failed to recover from network delay")
                return

        # Test 3: High Load
        if not simulate_high_load():
            logger.error("System failed under high load")
            if not wait_for_recovery():
                return

        if check_system_health():
            logger.info("System remained healthy after all experiments. Chaos engineering test passed!")
        else:
            logger.error("System health check failed after experiments. Further investigation needed.")

if __name__ == "__main__":
    run_chaos_experiment()

