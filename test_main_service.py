#import unittest
#from flask import url_for
#from main_service import app

#class TestMainService(unittest.TestCase):
#    def setUp(self):
#        app.config['TESTING'] = True
#        self.app = app.test_client()
#
#    def test_home_redirect(self):
#        response = self.app.get('/main')
#        if app.config['TESTING']:
#            self.assertEqual(response.status_code, 200)  # Expecting successful response in testing mode
#        else:
#            self.assertEqual(response.status_code, 302)
#
#    def test_course_registration_redirect(self):
#        response = self.app.get('/course_registration')
#        self.assertEqual(response.status_code, 302)
#        self.assertIn('http://kangyk.com/course_registration', response.location)
#
#    def test_festival_redirect(self):
#        response = self.app.get('/festival')
#        self.assertEqual(response.status_code, 302)
#        self.assertIn('http://kangyk.com/festival', response.location)
#
#    def test_news_redirect(self):
#        response = self.app.get('/notice')
#        self.assertEqual(response.status_code, 302)
#        self.assertIn('http://kangyk.com/notice', response.location)
#
#    def test_logout_redirect(self):
#        response = self.app.get('/logout')
#        self.assertEqual(response.status_code, 302)
#        self.assertIn('http://kangyk.com/login', response.location)

    # def test_api_festivals(self):
    #     response = self.app.get('/api/festivals')
    #     if app.config['TESTING']:
    #         self.assertEqual(response.status_code, 200)  # Expecting successful response in testing mode
    #         data = response.get_json()
    #         self.assertTrue(data['success'])
    #         self.assertEqual(len(data['festivals']), 1)
    #         self.assertEqual(data['festivals'][0]['name'], 'Test Festival')
    #     else:
    #         self.assertEqual(response.status_code, 401)  # Failing without JWT in non-testing mode

#if __name__ == '__main__':
#    unittest.main()
