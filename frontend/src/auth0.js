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
    const { user, isAuthenticated, isLoading } = useAuth0();
  
    if (isLoading) {
      return (<div>Loading...</div>);
    }
  
    return (
      isAuthenticated && (
        <div>
          <img src={user.picture} alt={user.name} />
          <h2>{user.name}</h2>
          <p>{user.email}</p>
        </div>
      )
    );
  } 