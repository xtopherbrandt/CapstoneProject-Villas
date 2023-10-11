from app import create_app
import unittest
import requests
import html_to_json
import json
import os

        
class Test_UserAPI(unittest.TestCase):
    def setUp(self) -> None:
        
        os.environ['CONFIG_FILE_NAME'] = "env_test.json"
        self.app = create_app()
        self.base_url = 'http://localhost:5000/'
        self.client = self.app.test_client

    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def check_basic_response_format(self, result, response_keys = [] ):
        '''Helper function to check the standard parts of the response are correct and consistent'''
        result_data_json = json.loads( result.data )
        self.assertTrue('success' in result_data_json.keys(), 'Incorrect response format. Missing "success" key' )       

        if int( result.status_code / 100 ) == 2 :
            self.assertEqual( result_data_json['success'], True, f'Incorrect response message. Status code == {result.status_code}, response message not True' ) 
            for key in response_keys:
                self.assertIn( key, result_data_json, f'Incorrect response message. Missing the key: {key}' )
        else:
            self.assertEqual( result_data_json['success'], False, f'Incorrect response message. Status code == {result.status_code}, response message not False' )
            self.assertEqual( result_data_json['error'], result.status_code, f'HTTP response status code {result.status_code} does not match response message error code {result_data_json["error"]}')
            self.assertIn('message', result_data_json, 'Incorrect response message, missing error message')
        return
    
    def test_can_post_new_user_and_get_user(self):
        url = self.base_url + 'user'
        user_data = {
            "first_name": "Joe",
            "last_name": "Smith",
            "phone_number": "555-444-1212",
            "home_address_line_1": "123 Anywhere St.",
            "home_address_line_2": "#98",
            "home_city": "Somewhereville",
            "home_province": "AB",
            "home_country": "CAN",
            "home_postal_code": "x1xy2y"
        }
        response = self.client().post('/user',json=user_data)        
        
        # Assert the response status code is OK
        self.assertEqual(response.status_code, 200)
        self.check_basic_response_format(response,['user'])
        
        post_response_data_json = json.loads( response.data )
        print(post_response_data_json)
        user_id = post_response_data_json['user']['id']
        
        get_response = self.client().get(f'/user/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.check_basic_response_format(response,['user'])
        
        user_data['id'] = user_id
        get_response_data_json = json.loads( get_response.data )
        self.assertDictEqual(user_data, get_response_data_json['user'] )

if __name__ == '__main__':
    unittest.main()