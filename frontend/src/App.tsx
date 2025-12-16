import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { Feedback } from '@/components/ui/Feedback'
import { AuthProvider } from '@/contexts/AuthContext'
import { FeedbackProvider } from '@/contexts/FeedbackContext'
import { ModalProvider } from '@/contexts/ModalContext'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import {
  HomePage,
  DashboardPage,
  ScorecardPage,
  LoginPage,
  SignupPage,
  VerifyEmailPage,
  ForgotPasswordPage,
  ResetPasswordPage,
  AdminPage,
  NotFoundPage,
} from '@/pages'
import { AdminRoute } from '@/components/auth/AdminRoute'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <FeedbackProvider>
          <ModalProvider>
            <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          
          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scorecard"
            element={
              <ProtectedRoute>
                <ScorecardPage />
              </ProtectedRoute>
            }
          />
          
          {/* Admin routes */}
          <Route
            path="/adm"
            element={
              <AdminRoute>
                <AdminPage />
              </AdminRoute>
            }
          />
          
          {/* 404 page */}
          <Route path="*" element={<NotFoundPage />} />
            </Routes>
            <Toaster />
            <Feedback />
          </ModalProvider>
        </FeedbackProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

