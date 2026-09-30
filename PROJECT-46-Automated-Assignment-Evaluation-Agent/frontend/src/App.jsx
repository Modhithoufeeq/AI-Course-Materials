import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';

// Layout & Protected Route Guards
import { MainLayout } from './components/layout/MainLayout';
import { RoleProtectedRoute } from './components/layout/RoleProtectedRoute';

// Auth Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

// Teacher Pages
import { TeacherDashboard } from './pages/teacher/TeacherDashboard';
import { AssignmentsPage } from './pages/teacher/AssignmentsPage';
import { CreateAssignmentPage } from './pages/teacher/CreateAssignmentPage';
import { AssignmentDetailPage } from './pages/teacher/AssignmentDetailPage';
import { SubmissionsPage } from './pages/teacher/SubmissionsPage';
import { EvaluationDetailPage } from './pages/teacher/EvaluationDetailPage';
import { PublishedResultsPage } from './pages/teacher/PublishedResultsPage';
import { StudentsPage } from './pages/teacher/StudentsPage';

// Student Pages
import { StudentDashboard } from './pages/student/StudentDashboard';
import { MyAssignmentsPage } from './pages/student/MyAssignmentsPage';
import { MyResultsPage } from './pages/student/MyResultsPage';
import { StudentResultDetailPage } from './pages/student/StudentResultDetailPage';

// 404
import { NotFoundPage } from './pages/NotFoundPage';

export const App = () => {
  const { user, isAuthenticated } = useAuth();

  // Root redirect logic
  const getRootRedirect = () => {
    if (!isAuthenticated || !user) {
      return <Navigate to="/login" replace />;
    }
    if (user.role === 'teacher' || user.role === 'admin') {
      return <Navigate to="/teacher/dashboard" replace />;
    }
    return <Navigate to="/student/dashboard" replace />;
  };

  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Root redirection */}
      <Route path="/" element={getRootRedirect()} />

      {/* Teacher Portal Protected Routes */}
      <Route
        path="/teacher"
        element={
          <RoleProtectedRoute allowedRoles={['teacher', 'admin']}>
            <MainLayout />
          </RoleProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/teacher/dashboard" replace />} />
        <Route path="dashboard" element={<TeacherDashboard />} />
        <Route path="assignments" element={<AssignmentsPage />} />
        <Route path="assignments/create" element={<CreateAssignmentPage />} />
        <Route path="assignments/:id" element={<AssignmentDetailPage />} />
        <Route path="submissions" element={<SubmissionsPage />} />
        <Route path="evaluations/:submissionId" element={<EvaluationDetailPage />} />
        <Route path="published-results" element={<PublishedResultsPage />} />
        <Route path="students" element={<StudentsPage />} />
      </Route>

      {/* Student Portal Protected Routes */}
      <Route
        path="/student"
        element={
          <RoleProtectedRoute allowedRoles={['student']}>
            <MainLayout />
          </RoleProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/student/dashboard" replace />} />
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="assignments" element={<MyAssignmentsPage />} />
        <Route path="results" element={<MyResultsPage />} />
        <Route path="results/:id" element={<StudentResultDetailPage />} />
      </Route>

      {/* 404 Page */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
