import React, { useEffect, useState } from "react";
import { useAuth0 } from '@auth0/auth0-react';

// The set of Auth0 components for authentication and profile

export const LoginButton = () => {
    const { loginWithRedirect, isAuthenticated } = useAuth0();
  
    return (
      !isAuthenticated && (
        (<button onClick={() => loginWithRedirect()}>Log In</button>)
      )
    );
  };
  
export const LogoutButton = () => {
    const { logout, isAuthenticated } = useAuth0();
  
    return (
      isAuthenticated && (
        <button onClick={() => logout({ logoutParams: { returnTo: window.location.origin }})}>
          Log Out
        </button>
      )
    );
  };
  
