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
  EditProfilePage,
  AccountSettingsPage,
  ScorecardPage,
  LoginPage,
  SignupPage,
  VerifyEmailPage,
  ForgotPasswordPage,
  ResetPasswordPage,
  AdminPage,
  AdminKnockoutPage,
  AdminUsersPage,
  NotFoundPage,
  CreateLeaguePage,
  GlobalLeaguesPage,
  LeagueDetailPage,
  FaqPage,
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
            path="/profile"
            element={
              <ProtectedRoute>
                <EditProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/account"
            element={
              <ProtectedRoute>
                <AccountSettingsPage />
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
          <Route
            path="/faq"
            element={
              <ProtectedRoute>
                <FaqPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leagues/create"
            element={
              <ProtectedRoute>
                <CreateLeaguePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leagues/browse"
            element={
              <ProtectedRoute>
                <GlobalLeaguesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leagues/:leagueId"
            element={
              <ProtectedRoute>
                <LeagueDetailPage />
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
          <Route
            path="/adm/knockout"
            element={
              <AdminRoute>
                <AdminKnockoutPage />
              </AdminRoute>
            }
          />
          <Route
            path="/adm/users"
            element={
              <AdminRoute>
                <AdminUsersPage />
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

