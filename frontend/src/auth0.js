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
  
export const Profile = () => {
    const { user, isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();
    const [userMetadata, setUserMetadata] = useState(null);

    useEffect(() => {
        const getUserMetadata = async () => {
            const domain = "dev-boa4pqqkkm3qz05i.us.auth0.com";

            try {
                const accessToken = await getAccessTokenSilently({
                    authorizationParams: {
                        audience: `https://${domain}/api/v2/`,
                        scope: "read:current_user",
                    },
                });

                const userDetailsByIdUrl = `https://${domain}/api/v2/users/${user.sub}`;

                console.log(userDetailsByIdUrl);

                const metadataResponse = await fetch(userDetailsByIdUrl, {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                });

                const { user_metadata } = await metadataResponse.json();

                setUserMetadata(user_metadata);
            }
            catch(e) {
                console.log(e.message);
            }
        };

        getUserMetadata();

    }, [getAccessTokenSilently, user?.sub]);
  
    if (isLoading) {
        return (<div>Loading...</div>);
    }
  
    return (
        isAuthenticated && (
          <div>
            <img src={user.picture} alt={user.name} />
            <h2>{user.name}</h2>
            <p>{user.email}</p>
            <h3>User Metadata</h3>
            {userMetadata ? (
              <pre>{JSON.stringify(userMetadata, null, 2)}</pre>
            ) : ( "No user metadata defined" )}
          </div>
        )
      );     
}