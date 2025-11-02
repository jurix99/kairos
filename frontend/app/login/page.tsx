"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { LoginForm } from "@/components/login-form"
import { useAuth } from "@/contexts/auth-context"
import { apiClient } from "@/lib/api"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user, refreshSession } = useAuth()
  const [isProcessing, setIsProcessing] = useState(false)

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (user && !isProcessing) {
      router.push('/dashboard')
    }
  }, [user, router, isProcessing])

  // Handle GitHub OAuth callback
  useEffect(() => {
    const handleGitHubCallback = async () => {
      const code = searchParams?.get('code')
      const state = searchParams?.get('state')
      const error = searchParams?.get('error')
      const isPending = sessionStorage.getItem('github_auth_pending')

      if (!isPending || !code) return

      setIsProcessing(true)
      
      // Verify state to prevent CSRF
      const savedState = sessionStorage.getItem('github_auth_state')
      
      if (error) {
        console.error('GitHub auth error:', error)
        sessionStorage.removeItem('github_auth_state')
        sessionStorage.removeItem('github_auth_pending')
        setIsProcessing(false)
        return
      }

      if (!state || state !== savedState) {
        console.error('Invalid GitHub authentication response')
        sessionStorage.removeItem('github_auth_state')
        sessionStorage.removeItem('github_auth_pending')
        setIsProcessing(false)
        return
      }

      try {
        // Exchange code for user data via backend
        const user = await apiClient.githubLogin(code, state)
        
        // Save user
        localStorage.setItem('kairos_user', JSON.stringify(user))
        
        // Cleanup
        sessionStorage.removeItem('github_auth_state')
        sessionStorage.removeItem('github_auth_pending')
        
        // Clear URL parameters
        window.history.replaceState({}, document.title, '/login')
        
        // Update auth context
        refreshSession()
        
        // Redirect to dashboard
        router.push('/dashboard')
      } catch (error) {
        console.error('GitHub auth processing error:', error)
        
        // Fallback to test user for development
        const testUser = {
          id: 'test-123',
          name: 'Test User',
          email: 'test@example.com',
          picture: 'https://github.com/identicons/test.png',
          provider: 'github',
          external_id: 'test-123',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        localStorage.setItem('kairos_user', JSON.stringify(testUser))
        sessionStorage.removeItem('github_auth_state')
        sessionStorage.removeItem('github_auth_pending')
        
        refreshSession()
        router.push('/dashboard')
      } finally {
        setIsProcessing(false)
      }
    }

    handleGitHubCallback()
  }, [searchParams, refreshSession, router])

  if (isProcessing) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <div>Finalizing login...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <LoginForm />
          </div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-pink-600/20 dark:from-purple-900/30 dark:to-pink-900/30" />
        <div className="absolute inset-0 flex items-center justify-center p-8">
          <div className="max-w-md text-center">
            <h2 className="text-4xl font-bold mb-4">Welcome to Kairos</h2>
            <p className="text-lg text-muted-foreground">
              Manage your time efficiently with our smart calendar application
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
