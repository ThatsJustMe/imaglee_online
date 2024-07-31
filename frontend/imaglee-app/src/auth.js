import gql from 'graphql-tag';
import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client';
import fetch from 'node-fetch';
import dockerSecret from 'docker-secret';

// Načtení Docker secrets pro GraphQL přihlášení
const username = dockerSecret('graphql_query_username') || process.env.GRAPHQL_QUERY_USERNAME;
const password = dockerSecret('graphql_query_password') || process.env.GRAPHQL_QUERY_PASSWORD;
let jwtToken = dockerSecret('jwt_secret') || process.env.JWT_SECRET;

const client = new ApolloClient({
  link: new HttpLink({ uri: process.env.GRAPHQL_HTTP, fetch }),
  cache: new InMemoryCache()
});

const LOGIN_MUTATION = gql`
  mutation TokenAuth($username: String!, $password: String!) {
	tokenAuth(username: $username, password: $password) {
	  token
	  refreshToken
	}
  }
`;

const REFRESH_TOKEN_MUTATION = gql`
  mutation RefreshToken($refreshToken: String!) {
	refreshToken(refreshToken: $refreshToken) {
	  token
	}
  }
`;

async function login() {
  try {
	const response = await client.mutate({
	  mutation: LOGIN_MUTATION,
	  variables: { username, password }
	});
	jwtToken = response.data.tokenAuth.token;
	const refreshToken = response.data.tokenAuth.refreshToken;
	localStorage.setItem('jwtToken', jwtToken); // Uložení tokenu do localStorage
	localStorage.setItem('refreshToken', refreshToken); // Uložení refresh tokenu do localStorage
	console.log('JWT Token:', jwtToken);
	return jwtToken;
  } catch (error) {
	console.error('Error logging in:', error);
	throw error;
  }
}

async function refreshTokenIfNeeded() {
  const storedRefreshToken = localStorage.getItem('refreshToken');
  if (!storedRefreshToken) {
	await login();
  } else {
	try {
	  const response = await client.mutate({
		mutation: REFRESH_TOKEN_MUTATION,
		variables: { refreshToken: storedRefreshToken }
	  });
	  jwtToken = response.data.refreshToken.token;
	  localStorage.setItem('jwtToken', jwtToken); // Uložení obnoveného tokenu do localStorage
	  console.log('JWT Token refreshed:', jwtToken);
	  return jwtToken;
	} catch (error) {
	  console.error('Error refreshing token:', error);
	  await login();
	}
  }
}

function getJwtToken() {
  return jwtToken || localStorage.getItem('jwtToken');
}

export { login, refreshTokenIfNeeded, getJwtToken };