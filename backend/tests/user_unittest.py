from app import create_app
import unittest
import requests
import html_to_json
import json
import os
import random, string
import urllib.parse

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
        
        self.AUTH0_BACKEND_CLIENT_ID = self.app.config['AUTH0_BACKEND_CLIENT_ID']
        self.AUTH0_BACKEND_CLIENT_SECRET = self.app.config['AUTH0_BACKEND_CLIENT_SECRET']
        self.AUTH0_MANAGEMENT_API_AUDIENCE = self.app.config['AUTH0_MANAGEMENT_API_AUDIENCE']
        
        self.AUTH0_M2M_TEST_CLIENT_ID = self.app.config['AUTH0_M2M_TEST_CLIENT_ID']
        self.AUTH0_M2M_TEST_CLIENT_SECRET = self.app.config['AUTH0_M2M_TEST_CLIENT_SECRET']
        
        self.testingUsers = self.app.config['TEST_USERS']
    
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
    
    def get_machine_2_machine_auth_token(self):
        '''
        Gets a machine to machine auth token from Auth0
        Client ID and Client Secret will be for the Test Application in Auth0 not the production application
        '''
        body={
            "client_id": self.AUTH0_M2M_TEST_CLIENT_ID,
            "client_secret": self.AUTH0_M2M_TEST_CLIENT_SECRET,
            "audience": self.AUTH0_AUDIENCE,
            "grant_type": 'client_credentials'
        }
        
        response = requests.post(f'https://{self.AUTH0_DOMAIN}/oauth/token', json=body, headers={'content-type': "application/json"})

        return response.json()['access_token']
    
    # scopes need to be space delimeted
    def get_user_auth_token(self, userName):
        '''
        Gets an auth token for a user stored in the Auth0 database.
        To set up the user:
            1. generate a unique email address (duck email addresses work well)
            2. generate a password
            3. store the username and password in the env_test.py file in the TEST_USERS key
                a. the value of the key should be a JSON object with each test user's id (email address) as the key and the value as the password
            4. in Auth0 go to the User Management section and create a new user
                a. set the Connection to the Username-Password-Authentication connection (Database connection)
                b. give the user a role or the specific permissions required for the test
            5. if required can attempt to login as the user with the first url in the auth0_url.txt file
                a. be sure to use the second url to logout
        
        Each test requires a user and uses this method to get a token for that user.
        Adjust the scope parameter to reflect the scopes available, want to get all scopes available
            Note that the Auth0 API has the Add Permissions in the Access Token turned off because the Auth0 SDK uses the scope attribute of the token
            Only the scopes specified in the token request (below) will be returned. They must be space separated.
        '''
        url = f'https://{self.AUTH0_DOMAIN}/oauth/token' 
        headers = {'content-type': 'application/json'}
        password = self.testingUsers[userName]
        parameter = { "client_id":self.AUTH0_CLIENT_ID, 
                    "client_secret": self.AUTH0_CLIENT_SECRET,
                    "audience": self.AUTH0_AUDIENCE,
                    "grant_type": "password",
                    "username": userName,
                    "password": password,
                    "scope": "openid profile read:user create:user"
                    } 
        
        # do the equivalent of a CURL request from https://auth0.com/docs/quickstart/backend/python/02-using#obtaining-an-access-token-for-testing
        responseDICT = json.loads(requests.post(url, json=parameter, headers=headers).text)
        return responseDICT['access_token']

    def get_management_api_auth_token(self):
        '''
        Gets a machine to machine auth token for the Villas ap from Auth0
        Client ID and Client Secret will be for the Test Application in Auth0 not the production application
        '''
        auth0_base_uri = f'https://{self.AUTH0_DOMAIN}'
        
        body={
            "client_id": self.AUTH0_BACKEND_CLIENT_ID,
            "client_secret": self.AUTH0_BACKEND_CLIENT_SECRET,
            "audience": self.AUTH0_MANAGEMENT_API_AUDIENCE,
            "grant_type": 'client_credentials',
        }
        response = requests.post(f'{auth0_base_uri}/oauth/token', json=body, headers={'content-type': "application/json"})
        
        return response.json()['access_token']

    def random_email_name_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    
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

        user_id = post_response_data_json['user']['id']
        
        get_response = self.client().get(f'/user/{user_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.check_basic_response_format(response,['user'])
        
        user_data['id'] = user_id
        get_response_data_json = json.loads( get_response.data )
        self.assertDictEqual(user_data, get_response_data_json['user'] )

    def test_get_valid_user_returns_200(self):
        
        userName='8bsumgd8@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }
        
        get_response = self.client().get('/user/auth0|6543f5b1cba2fea2618e27c2', headers=headers)
       
        # Assert the response status code is NOT FOUND
        self.assertEqual(get_response.status_code, 200)    
        self.check_basic_response_format(get_response,['user'])
        self.assertIn("user_contact", get_response.json['user'], "response should contain a user_contact element" )
        
    def test_get_user_with_bad_id_returns_404(self):
        
        userName='8bsumgd8@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }
        
        get_response = self.client().get('/user/99999', headers=headers)
       
        # Assert the response status code is NOT FOUND
        self.assertEqual(get_response.status_code, 404)       
        
    def test_post_user_with_no_body_returns_415(self):
        
        userName='8bsumgd8@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }
        
        response = self.client().post('/user', headers=headers)        
        
        # Assert the response status code is UNSUPPORTED MEDIA    
        self.assertEqual(response.status_code, 415)
        
    def test_post_user_with_empty_body_returns_400(self):
                
        userName='8bsumgd8@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }

        response = self.client().post('/user', json={}, headers=headers)        
        
        # Assert the response status code is BAD REQUEST
        self.assertEqual(response.status_code, 400)
        
    def test_post_user_with_a_short_first_name_returns_400(self):
                
        userName='qae9rz92@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }
        user_data = {
                    "first_name": "C",
                    "last_name": "B"
                }
        response = self.client().post('/user', json=user_data, headers=headers)        
        
        # Assert the response status code is BAD REQUEST
        self.assertEqual(response.status_code, 400)
                
    def test_post_user_with_only_first_name_returns_400_with_descriptive_message(self):
                
        userName='qae9rz92@duck.com'
        token = self.get_user_auth_token(userName)
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
        
    def test_attempt_create_user_with_wrong_privileges_results_in_in_401(self):
        
        userName='bdxa559p@duck.com'
        token = self.get_user_auth_token(userName)
        headers = { 'authorization': f'Bearer {token}' }
                
        user_data = {
            "first_name": "Joe",
            "last_name": "Smith"
        }

        response = self.client().post('/user',json=user_data )        
        
        # Assert the response status code is OK
        self.assertEqual(response.status_code, 401)
        
    def test_invite_user_creates_a_new_user_with_correct_permissions(self):
        
        email_address_name = self.random_email_name_string(8)
        email_address = f'{email_address_name}@nowhere.com'
        
        token = self.get_machine_2_machine_auth_token()
        headers = { 'authorization': f'Bearer {token}' }
                
        user_data = {
            "email_address": email_address,
            "user_role": "villa-guest",
            "unit_number": 34
        }

        response = self.client().post('/user-invite',json=user_data, headers=headers )   
        
        self.assertEqual(response.status_code, 200, f'User Invite should return a 200 status. Response:{response.json["message"] if "message" in response.json else "no message" }')
        
        self.check_basic_response_format(response, ['user_id'])
                                         
        user_id = response.json['user_id']
        
        token = self.get_management_api_auth_token()
        
        auth0_base_uri = f'https://{self.AUTH0_DOMAIN}'
        get_user_role_endpoint = f'{auth0_base_uri}/api/v2/users/{urllib.parse.quote(user_id)}/roles'

        headers = {
            'Accept' : 'application/json',
            'Authorization' : f'Bearer {token}'
        }
            
        # need to switch to Requests lib to make a request to the users role endpoint here
        # the flask client gets a 404 with exactly the same URL
        response = requests.request("GET", get_user_role_endpoint, headers=headers)
        
        self.assertEqual(response.status_code, 200, f'Get User Roles should return a 200 status.')
        
        self.assertEqual(1,len(response.json()), "User should have one role: villa-guest")
        role = response.json()[0]['name']
        self.assertEquals(role, 'villa-guest', "User should have role: villa-guest")
        
        # Now delete the user
        delete_user_endpoint = f'{auth0_base_uri}/api/v2/users/{urllib.parse.quote(user_id)}'
        response = requests.request("DELETE", delete_user_endpoint, headers=headers)

        self.assertEqual(response.status_code, 204, f'Delete User should return a 204 status.')
        
        
if __name__ == '__main__':
    unittest.main()