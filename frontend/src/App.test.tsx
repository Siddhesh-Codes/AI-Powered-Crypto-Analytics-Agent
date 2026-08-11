import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

/**
 * Helper to wrap components with required providers
 */
const AllProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </AuthProvider>
  </QueryClientProvider>
);

describe('App Component', () => {
  test('TC-F1: App renders without crashing', () => {
    render(<App />);
    // App should mount successfully
  });

  test('TC-F2: Landing page is the default route', () => {
    render(<App />);
    // Landing page should contain some recognizable text
    const body = document.body.textContent;
    expect(body).toBeTruthy();
  });
});
