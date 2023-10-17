import ListItem from '@mui/material/ListItem';
import IconButton from '@mui/material/IconButton';
import ListItemText from '@mui/material/ListItemText';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import moment from 'moment';
import { ButtonGroup, Stack, Typography } from '@mui/material';
import React, { useEffect, useState } from "react";
import { useAuth0 } from '@auth0/auth0-react';
import jwt_decode from 'jwt-decode';
import { TextField, Button } from '@mui/material';

export const CreateUser = ({authenticatedUserScope}) => {
    const { isAuthenticated } = useAuth0();
    const [ showForm, setShowForm ] = useState( false )

    let whatToShow=(<button onClick={() => setShowForm(true)}>Create User</button>);
    
    if (showForm){
        whatToShow = (<CreateUserForm setShowForm={(x) => setShowForm(x)}/>);
    }

    return (
        ( isAuthenticated && authenticatedUserScope.includes('create:user') && (
            <div>
                {whatToShow}
            </div>
            )
        )
        
    );
  };

export const AuthenticatedUser = ({setUserScope}) => {
    const { isAuthenticated, getAccessTokenSilently } = useAuth0();
    const [ villaUser, setVillaUser] = useState(null);
    const [ isLoading, setIsLoading ] = useState(true);

    useEffect(() => {
        const getVillaUser = async () => {
            const domain = 'dev-boa4pqqkkm3qz05i.us.auth0.com';

            try {
                const accessToken = await getAccessTokenSilently({
                    authorizationParams: {
                        audience: 'https://villa-systems.net',
                        scope: 'read:user create:user update:user delete:user',
                    },
                });
 
                setUserScope( jwt_decode(accessToken).scope )

                const villaUserUrl = 'http://localhost:5000/user/1';

                const villaUserResponse = await fetch(villaUserUrl, {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });

                const villaUser_responseJson = await villaUserResponse.json();
                
                setVillaUser( villaUser_responseJson.user );

                setIsLoading(false);
                
            } 
            catch (e) {
                console.log(e.message);
            }
        };

        getVillaUser();
    }, [getAccessTokenSilently] );

    if (isLoading) {
        return (<div>Loading...</div>);
    }

    return (
        isAuthenticated && (
            <div>
                <h2>Villa User</h2>
                <p>{villaUser.first_name} {villaUser.last_name}</p>
            </div>
        )
    )
}

export const CreateUserForm = ({setShowForm}) => {
    const { isAuthenticated, getAccessTokenSilently } = useAuth0();
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [streetAddressLine1, setStreetAddressLine1] = useState('');
    const [streetAddressLine2, setStreetAddressLine2] = useState('');
    const [city, setCity] = useState('');
    const [province, setProvince] = useState('');
    const [postalCode, setPostalCode] = useState('');
    const [country, setCountry] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [ isLoading, setIsLoading ] = useState(true);

    const postVillaUser = async () => {
        const domain = 'dev-boa4pqqkkm3qz05i.us.auth0.com';

        try {
            const accessToken = await getAccessTokenSilently({
                authorizationParams: {
                    audience: 'https://villa-systems.net',
                    scope: 'read:user create:user update:user delete:user',
                },
            });

            const villaUserUrl = 'http://localhost:5000/user';
            const body = {
              "first_name": firstName,
              "last_name": lastName,
              "home_address_line_1": streetAddressLine1,
              "home_address_line_2": streetAddressLine2,
              "home_city": city,
              "home_country": country,
              "home_postal_code": postalCode,
              "home_province": province,
              "phone_number": phoneNumber
            }
            console.log(body);
            const villaUserResponse = await fetch(villaUserUrl, {
                method: 'post',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": 'application/json',
                },
                body:JSON.stringify(body),
                mode: 'cors'
            });

            const villaUser_responseJson = await villaUserResponse.json();
            
            console.log( villaUser_responseJson.user );

            setIsLoading(false);
            
        } 
        catch (e) {
            console.log(e.message);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setShowForm(false);

        postVillaUser();

        console.log('Form submitted!');
    };
  
    return (
      <form onSubmit={handleSubmit}>
        <TextField
          label="First Name"
          variant="outlined"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
  
        <TextField
          label="Last Name"
          variant="outlined"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
  
        <TextField
          label="Street Address Line 1"
          variant="outlined"
          value={streetAddressLine1}
          onChange={(e) => setStreetAddressLine1(e.target.value)}
          required
        />
  
        <TextField
          label="Street Address Line 2"
          variant="outlined"
          value={streetAddressLine2}
          onChange={(e) => setStreetAddressLine2(e.target.value)}
        />
  
        <TextField
          label="City"
          variant="outlined"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          required
        />
  
        <TextField
          label="Province/State"
          variant="outlined"
          value={province}
          onChange={(e) => setProvince(e.target.value)}
          required
        />
  
        <TextField
          label="Country"
          variant="outlined"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          required
        />
  
        <TextField
          label="Postal Code"
          variant="outlined"
          value={postalCode}
          onChange={(e) => setPostalCode(e.target.value)}
          required
        />
  
        <TextField
          label="Phone Number"
          variant="outlined"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          required
        />
  
        <Button variant="contained" type="submit">
          Create User
        </Button>
      </form>
    );
  };