"use client"

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient, type User } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signInWithGitHub: () => void;
  signOut: () => void;
  refreshSession: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('kairos_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
      }
    }
    setIsLoading(false);
  }, []);

  const refreshSession = () => {
    const savedUser = localStorage.getItem('kairos_user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
      }
    }
  };

  const signInWithGitHub = () => {
    const state = Math.random().toString(36).substring(7);
    sessionStorage.setItem('github_auth_state', state);
    sessionStorage.setItem('github_auth_pending', 'true');
    
    const redirectUri = process.env.NEXT_PUBLIC_GITHUB_REDIRECT_URI || 'http://localhost:3000/login';
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(redirectUri)}&state=${state}&scope=user:email`;
    
    window.location.href = githubAuthUrl;
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem('kairos_user');
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        isLoading, 
        signInWithGitHub, 
        signOut,
        refreshSession 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

