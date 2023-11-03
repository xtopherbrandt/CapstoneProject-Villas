import React, { useEffect, useState } from "react";
import { useAuth0 } from '@auth0/auth0-react';
import jwt_decode from 'jwt-decode';
import { TextField, Button, Snackbar, Container, Box, Grid, Avatar, Typography, Link } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import MuiAlert from '@mui/material/Alert';

const HOST = process.env.REACT_APP_SERVER_HOST;

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export const UserInvitation = ({authenticatedUserScope}) => {
    const { isAuthenticated } = useAuth0();
    const [ showForm, setShowForm ] = useState( false )
    const [completionStatus, setCompletionStatus ] = useState(0); //for now 0: not started, 1: success, 2: warning (user exists), 3: error
    const [emailAddress, setEmailAddress] = useState('');
    const [unitNumber, setUnitNumber] = useState('');
    const [userRole, setUserRole] = useState('');
    

    let whatToShow=(<button onClick={() => setShowForm(true)}>User Invitation</button>);

    if (showForm){
        whatToShow = (
          <UserInvitationForm 
            setShowForm={setShowForm} 
            setCompletionStatus={setCompletionStatus} 
            setEmailAddress={setEmailAddress}
            emailAddress={emailAddress}
            unitNumber={unitNumber}
            setUnitNumber={setUnitNumber}
            userRole={userRole}
            setUserRole={setUserRole}
          />
        );
    }


    return (
        ( isAuthenticated && authenticatedUserScope.includes('create:user') && (
            <div>
                {whatToShow}
                <UserInvitationCompleteSnack setCompletionStatus={setCompletionStatus} completionStatus={completionStatus} emailAddress={emailAddress}/>
            </div>
          )
        )
        
    );
};

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

export const UserInvitationForm = ({setShowForm, setCompletionStatus, emailAddress, setEmailAddress, unitNumber, setUnitNumber, userRole, setUserRole}) => {
    const { isAuthenticated, getAccessTokenSilently } = useAuth0();

    const postUserInvitation = async () => {
        const domain = 'dev-boa4pqqkkm3qz05i.us.auth0.com';

        try {
            const accessToken = await getAccessTokenSilently({
                authorizationParams: {
                    audience: 'https://villa-systems.net',
                    scope: 'read:user create:user update:user delete:user',
                },
            });

            const villaUserUrl = `${HOST}/user-invite`;
            const body = {
              "email_address": emailAddress,
              "user_role": userRole,
              "unit_number": unitNumber
            }

            const villaUserResponse = await fetch(villaUserUrl, {
                method: 'post',
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": 'application/json',
                },
                body:JSON.stringify(body),
                mode: 'cors'
            });

            if ( villaUserResponse.status == 200 ){
              setCompletionStatus(1);
            }
            else if ( villaUserResponse.status == 409 ){
              setCompletionStatus(2);
            }
            else{
              setCompletionStatus(3);
            }
            
        } 
        catch (e) {
            console.log(e.message);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setShowForm(false);

        postUserInvitation();

    };
  
    return (
      <div>
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
                <Grid item xs={12}>
                  <TextField
                    required
                    fullWidth
                    id="email_address"
                    label="Email Address"
                    name="email_address"
                    autoComplete="email"
                    value={emailAddress}
                    onChange={(e) => setEmailAddress(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Unit Number"
                    id="unit_number"
                    name="unit_number"
                    value={unitNumber}
                    onChange={(e) => setUnitNumber(e.target.value)}
                    required
                    fullWidth
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="User Role"
                    id="user_role"
                    name="user_role"
                    value={userRole}
                    onChange={(e) => setUserRole(e.target.value)}
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
                  Invite User
                </Button>
              </Grid>
            </Box>
          </Box>
          <Copyright sx={{ mt: 5 }} />
        </Container>      

      </div>
    );
  };

  export const UserInvitationCompleteSnack = ({setCompletionStatus, completionStatus, emailAddress}) => { 
    const [snackBarOpen, setSnackBarOpen] = React.useState(false);
  
    const handleClose = (event, reason) => {
      if (reason === 'clickaway') {
        return;
      }
  
      setSnackBarOpen(false);
      setCompletionStatus(0);
    };

    let message= "";
    
    let severity = "success";

    switch (completionStatus){
      case 0 : {
        if (snackBarOpen){
          setSnackBarOpen(false);
        }
        break;
      }
      case 1 : {
        message= `Invite sent to: ${emailAddress}.`;
        severity = "success"

        if (!snackBarOpen){
          setSnackBarOpen(true);
        }
        break;
      }
      case 2 : {
        severity = "warning"
        message = `${emailAddress} has already been invited.`
  
        if (!snackBarOpen){
          setSnackBarOpen(true);
        }
        break;
      }
      case 3 : {
        severity = "error"
        message = `An error occurred trying to send the invite.`
  
        if (!snackBarOpen){
          setSnackBarOpen(true);
        }
        break;
      }
      default : {
        console.log('default')
      }
    }

    return (
        <Snackbar 
          open={snackBarOpen}
          autoHideDuration={6000}
        >
          <Alert onClose={handleClose} severity={severity} sx={{ width: '100%' }}>
            {message}
        </Alert>
        </Snackbar>
    );    
  };