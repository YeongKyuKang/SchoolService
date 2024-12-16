import requests
import time
import random
import jwt
import logging
from requests.exceptions import RequestException
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5001"  # 환경에 맞게 조정
SECRET_KEY = "jwt_secret_key"  # 실제 운영 환경에서는 안전하게 관리해야 합니다

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
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        logger.info(f"JWT token successfully generated for user_id: {user_id}")
        logger.debug(f"Token preview: {access_token[:20]}...")
        
        return access_token
    except Exception as e:
        logger.error(f"JWT token generation failed: {str(e)}")
        logger.exception("Detailed traceback:")
        raise

def set_access_token_cookie(session, token):
    """
    세션에 access_token_cookie를 설정합니다.
    """
    session.cookies.set('access_token_cookie', token, domain='localhost', path='/')
    logger.info("access_token_cookie가 세션에 설정되었습니다.")

def get_student_with_token():
    try:
        student = random.choice(students)
        token = generate_jwt_token(student['id'])
        return student, token
    except IndexError:
        raise
    except Exception as e:
        raise

students = [generate_student_data() for _ in range(10)]

def check_system_health():
    try:
        student = generate_student_data()
        token = generate_jwt_token(student['id'])

        session = requests.Session()
        set_access_token_cookie(session, token)

        response = session.get(f"{BASE_URL}/api/search_courses")
        
        if response.status_code == 200:
            logger.info("System health check successful")
            return True
        else:
            logger.error(f"System health check failed with status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error during system health check: {str(e)}")
        return False

def fetch_dropdown_options(session):
    logger.info("Starting to fetch dropdown options")
    try:
        url = f"{BASE_URL}/api/dropdown_options"
        logger.debug(f"Sending GET request to {url}")
        logger.debug(f"Request headers: {session.headers}")
        
        response = session.get(url, timeout=10)
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
        
def search_courses(session, credits=None, department=None, course_name=None):
    params = {}
    if credits:
        params['credits'] = credits
    if department:
        params['department'] = department
    if course_name:
        params['course_name'] = course_name
    
    response = session.get(f"{BASE_URL}/api/search_courses", params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info(f"Found {len(data.get('courses', []))} courses")
            return data.get("courses")
    logger.error("Failed to search courses")
    return []

def apply_course(session, course_key):
    logger.info(f"Applying for course: {course_key}")
    response = session.post(f"{BASE_URL}/api/apply_course", json={"course_key": course_key})
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Course application successful")
            return True
    logger.error("Course application failed")
    return False

def cancel_course(session, course_key):
    logger.info(f"Cancelling course: {course_key}")
    response = session.post(f"{BASE_URL}/api/cancel_course", json={"course_key": course_key})
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
        student = generate_student_data()
        token = generate_jwt_token(student['id'])

        session = requests.Session()
        set_access_token_cookie(session, token)

        logger.info("Fetching dropdown options")
        credits, departments = fetch_dropdown_options(session)
        if not credits or not departments:
            logger.error("Failed to fetch dropdown options")
            return False
        logger.debug(f"Fetched credits: {credits}, departments: {departments}")

        selected_credits = random.choice(credits)
        selected_department = random.choice(departments)
        logger.info(f"Selected credits: {selected_credits}, department: {selected_department}")

        logger.info("Searching for courses")
        courses = search_courses(session, credits=selected_credits, department=selected_department)
        if not courses:
            logger.error("No courses found for selected criteria")
            return False
        logger.debug(f"Found {len(courses)} courses")

        selected_course = random.choice(courses)
        logger.info(f"Selected course: {selected_course['course_key']}")

        logger.info(f"Attempting to apply for course: {selected_course['course_key']}")
        if apply_course(session, selected_course['course_key']):
            logger.info(f"Successfully applied for course: {selected_course['course_key']}")
            time.sleep(random.uniform(0.5, 2))  # Simulate some time passing
            if random.random() < 0.3:  # 30% chance to cancel the course
                logger.info(f"Attempting to cancel course: {selected_course['course_key']}")
                cancel_result = cancel_course(session, selected_course['course_key'])
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

def inject_network_delay(session):
    logger.info("Injecting network delay...")
    original_get = session.get
    original_post = session.post

    def delayed_request(method, *args, **kwargs):
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        return method(*args, **kwargs)

    session.get = lambda *args, **kwargs: delayed_request(original_get, *args, **kwargs)
    session.post = lambda *args, **kwargs: delayed_request(original_post, *args, **kwargs)

    # Test the delay
    start_time = time.time()
    fetch_dropdown_options(session)
    end_time = time.time()

    session.get = original_get
    session.post = original_post

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
    
    if not check_system_health():
        logger.error("System is not healthy at the start. Aborting experiment.")
        return
    
    # Test 1: Concurrent Registrations
    if not simulate_concurrent_registrations(20):
        logger.error("System failed to handle concurrent registrations properly")
        if not wait_for_recovery():
            return

    # Test 2: Network Delay
    session = requests.Session()
    token = generate_jwt_token(get_student_with_token()[0]['id'])
    set_access_token_cookie(session, token)

    if inject_network_delay(session):
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

