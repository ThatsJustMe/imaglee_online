import { ApolloClient, InMemoryCache, HttpLink, ApolloLink } from '@apollo/client/core';
import { setContext } from '@apollo/client/link/context';
import fetch from 'node-fetch';
import { login, refreshTokenIfNeeded, getJwtToken } from './auth';
import dockerSecret from 'docker-secret';

// Konfigurace HTTP linky pro Apollo Clienta
const httpLink = new HttpLink({
  uri: process.env.PUBLIC_GRAPHQL_HTTP,
  fetch
});

// Konfigurace autentizační linky pro Apollo Clienta
const authLink = setContext(async (_, { headers }) => {
  await refreshTokenIfNeeded(); // Obnovení tokenu pokud je potřeba

  let token = getJwtToken();
  if (!token) {
	await login();
	token = getJwtToken();
  }

  return {
	headers: {
	  ...headers,
	  authorization: token ? `Bearer ${token}` : '',
	}
  };
});

// Inicializace Apollo Clienta
const client = new ApolloClient({
  link: ApolloLink.from([authLink, httpLink]),
  cache: new InMemoryCache()
});

export default client;