import React, { useEffect, useState } from "react";
import { useAuth0 } from '@auth0/auth0-react';
import jwt_decode from 'jwt-decode';
import { TextField, Button, FormControlLabel, Container, Box, Grid, Avatar, Typography, Select, InputLabel, MenuItem, Link } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';


export const UserProfile = ({authenticatedUserScope}) => {
    const { isAuthenticated } = useAuth0();
    const [ showForm, setShowForm ] = useState( false )

    let whatToShow=(<button onClick={() => setShowForm(true)}>User Profile</button>);

    if (showForm){
        whatToShow = (<UserProfileForm setShowForm={(x) => setShowForm(x)}/>);
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

function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="https://villas-management.qqq/">
        Villas Management
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

export const UserProfileForm = ({setShowForm}) => {
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
    const [email, setEmail] = useState('');
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
      <Container component="main" maxWidth="xs">

        <Box
          sx={{
            marginTop:8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Create User
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt:3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  autoComplete="given-name"
                  label="First Name"
                  id="first_name"
                  name="first_name"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                  fullWidth
                  autoFocus
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  autoComplete="family-name"
                  label="Last Name"
                  id="last_name"
                  name="last_name"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Phone Number"
                  id="phone_number"
                  name="phone_number"
                  autoComplete="phone-number"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Street Address Line 1"
                  id="street_address_line_1"
                  name="street_address_line_1"
                  value={streetAddressLine1}
                  onChange={(e) => setStreetAddressLine1(e.target.value)}
                  required
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Street Address Line 2"
                  id="street_address_line_2"
                  name="street_address_line_2"
                  value={streetAddressLine2}
                  onChange={(e) => setStreetAddressLine2(e.target.value)}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="City"
                  name="city"
                  id="city"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  required
                  fullWidth
                  autoComplete="city"
                />
              </Grid>
              <Grid item xs={12}>
                <Select
                  label="Province"
                  id="province"
                  value={province}
                  onChange={(e) => setProvince(e.target.value)}
                  required
                  fullWidth
                >
                  <MenuItem value="AB">Alberta</MenuItem>
                  <MenuItem value="BC">British Columbia</MenuItem>
                </Select>
              </Grid>              
              <Grid item xs={12}>
                <Select
                  label="Country"
                  id="country"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  required
                  fullWidth
                >
                  <MenuItem value="CAN">Canada</MenuItem>
                  <MenuItem value="US">United States of America</MenuItem>
                </Select>  
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Postal Code"
                  id="postal_code"
                  name="postal_code"
                  value={postalCode}
                  onChange={(e) => setPostalCode(e.target.value)}
                  required
                  fullWidth
                />

              </Grid>
              <Button 
                fullWidth 
                variant="contained" 
                type="submit"
                sx={{ mt: 3, mb:2 }}
              >
                Create User
              </Button>
            </Grid>            
          </Box>
        </Box>
        <Copyright sx={{ mt: 5 }} />
      </Container>      
    );
  };