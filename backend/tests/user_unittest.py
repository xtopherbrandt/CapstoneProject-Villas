from app import create_app
import unittest
import requests
import html_to_json
import json
import os


        
testingUsers = {
    'qae9rz92@duck.com': 'sqQcj_B3E8rs4.jA',
    'bdxa559p@duck.com': '-GPihnLU@hPqG9U2'
    }

class Test_UserAPI(unittest.TestCase):
    def setUp(self) -> None:
        
        os.environ['CONFIG_FILE_NAME'] = "env_test.json"
        self.app = create_app()
        self.base_url = 'http://localhost:5000/'
        self.app.testing = True
        self.client = self.app.test_client
        
        self.AUTH0_DOMAIN = self.app.config['AUTH0_DOMAIN']
        self.AUTH0_CLIENT_ID = self.app.config['AUTH0_CLIENT_ID']
        self.AUTH0_CLIENT_SECRET = self.app.config['AUTH0_CLIENT_SECRET']
        self.AUTH0_AUDIENCE = self.app.config['AUTH0_AUDIENCE']
    
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
    
    def get_auth_token(self):
        body={
            "client_id": self.AUTH0_CLIENT_ID,
            "client_secret": self.AUTH0_CLIENT_SECRET,
            "audience": self.AUTH0_AUDIENCE,
            "grant_type": 'client_credentials'
        }
        response = requests.post(f'https://{self.AUTH0_DOMAIN}/oauth/token', json=body, headers={'content-type': "application/json"})
        
        return response.json()['access_token']
    
    def get_user_auth_token(self, userName):
        url = f'https://{self.AUTH0_DOMAIN}/oauth/token' 
        headers = {'content-type': 'application/json'}
        password = testingUsers[userName]
        parameter = { "client_id":self.AUTH0_CLIENT_ID, 
                    "client_secret": self.AUTH0_CLIENT_SECRET,
                    "audience": self.AUTH0_AUDIENCE,
                    "grant_type": "password",
                    "username": userName,
                    "password": password, 
                    "scope": "openid, user:create, user:read"} 
        
        # do the equivalent of a CURL request from https://auth0.com/docs/quickstart/backend/python/02-using#obtaining-an-access-token-for-testing
        responseDICT = json.loads(requests.post(url, json=parameter, headers=headers).text)
        return responseDICT['access_token']
    
    def test_can_post_new_user_and_get_user(self):
        
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
        
        userName='qae9rz92@duck.com'
        token = self.get_user_auth_token(userName)

        headers = { 'authorization': f'Bearer {token}' }

        response = self.client().post('/user',json=user_data, headers=headers)        
        
        # Assert the response status code is OK
        self.assertEqual(response.status_code, 200)
        self.check_basic_response_format(response,['user'])
        
        post_response_data_json = json.loads( response.data )
        print(post_response_data_json)
        user_id = post_response_data_json['user']['id']
        
        get_response = self.client().get(f'/user/{user_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.check_basic_response_format(response,['user'])
        
        user_data['id'] = user_id
        get_response_data_json = json.loads( get_response.data )
        self.assertDictEqual(user_data, get_response_data_json['user'] )

    def test_get_valid_user_returns_200(self):
        
        userName='qae9rz92@duck.com'
        token = self.get_user_auth_token(userName)
        
        headers = { 'authorization': f'Bearer {token}' }
        
        get_response = self.client().get('/user/1', headers=headers)
       
        # Assert the response status code is NOT FOUND
        self.assertEqual(get_response.status_code, 200)    
        self.check_basic_response_format(get_response,['user'])
        
    def test_get_user_with_bad_id_returns_404(self):
        
        token = self.get_auth_token()
        headers = { 'authorization': f'Bearer {token}' }
        
        get_response = self.client().get('/user/99999', headers=headers)
       
        # Assert the response status code is NOT FOUND
        self.assertEqual(get_response.status_code, 404)       
        
    def test_post_user_with_no_body_returns_415(self):
        
        token = self.get_auth_token()
        headers = { 'authorization': f'Bearer {token}' }
        
        response = self.client().post('/user', headers=headers)        
        
        # Assert the response status code is UNSUPPORTED MEDIA    
        self.assertEqual(response.status_code, 415)
        
    def test_post_user_with_empty_body_returns_400(self):
                
        token = self.get_auth_token()
        headers = { 'authorization': f'Bearer {token}' }

        response = self.client().post('/user', json={}, headers=headers)        
        
        # Assert the response status code is BAD REQUEST
        self.assertEqual(response.status_code, 400)
        
    def test_post_user_with_only_first_name_returns_400_with_descriptive_message(self):
                
        token = self.get_auth_token()
        headers = { 'authorization': f'Bearer {token}' }

        user_data = {
            'first_name': 'test'
        }
        response = self.client().post('/user', json=user_data, headers=headers)        
        
        # Assert the response status code is BAD REQUEST
        self.assertEqual(response.status_code, 400)        
        
        response_data_json = json.loads(response.data)
        self.assertTrue('last_name' in response_data_json['message'], "Response message should contain information pointing to the missing last_name field")
        
    def test_attempt_create_user_without_token_results_in_401(self):
        
        user_data = {
            "first_name": "Joe",
            "last_name": "Smith"
        }

        response = self.client().post('/user',json=user_data )        
        
        # Assert the response status code is OK
        self.assertEqual(response.status_code, 401)
        
    def test_attempt_create_user_with_wrong_privileges_results_in_in_403(self):
        
        user_data = {
            "first_name": "Joe",
            "last_name": "Smith"
        }

        response = self.client().post('/user',json=user_data )        
        
        # Assert the response status code is OK
        self.assertEqual(response.status_code, 401)
        
if __name__ == '__main__':
    unittest.main()