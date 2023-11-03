import React, { useEffect, useState } from "react";
import { useAuth0 } from '@auth0/auth0-react';

// The set of Auth0 components for authentication and profile

export const LoginButton = () => {
  const { loginWithRedirect, isAuthenticated } = useAuth0();

  const handleLogin = async () => {
    await loginWithRedirect({
      appState: {
        returnTo: "/profile",
      },
    });
  };

  return ( !isAuthenticated && (
    <button className="button__login" onClick={handleLogin}>
      Log In
    </button> )
  );
};
  
export const LogoutButton = () => {
    const { logout, isAuthenticated } = useAuth0();
    
    const handleLogout = () => {
      logout({
        logoutParams: {
          returnTo: window.location.origin,
        },
      });
    };

    return (
      isAuthenticated && (
        <button className="button__logout" onClick={ handleLogout }>
          Log Out
        </button>
      )
    );
  };
  
export const Auth0Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth0();
  
  if (isLoading) {
    return <div>Loading User...</div>;
  }

  console.log(user)
  return (
    isAuthenticated && (
      <div>
        <p>id: {user.sub}</p>  
      </div>
    )
  );
};