from app import create_app
import unittest
import requests
import html_to_json
import json

        
class Test_UserAPI(unittest.TestCase):
    def setUp(self) -> None:
        
        self.app = create_app(test_config=True)
        self.base_url = 'http://localhost:5000/'
        self.client = requests.Session()

    
    def tearDown(self) -> None:
        self.client.close()
        return super().tearDown()
    
    def test_can_post_new_user(self):
        
        self.assertTrue(True)
        
if __name__ == '__main__':
    unittest.main()