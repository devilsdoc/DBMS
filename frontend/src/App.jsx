import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import LoginPage from './pages/LoginPage';
import CourseTeacherDashboard from './pages/CourseTeacherDashboard';
import TGDashboard from './pages/TGDashboard';
import StudentDashboard from './pages/StudentDashboard';
import HoDDashboard from './pages/HoDDashboard';
import AuditTrailPage from './pages/AuditTrailPage';

function AppContent() {
  const { isAuthenticated, user, activeRole } = useAuth();
  const [currentView, setCurrentView] = useState('course_teacher');

  // Set default view based on user roles upon login or role switch
  useEffect(() => {
    if (!user) return;
    const role = activeRole || user.roles?.[0];
    if (role === 'HOD') setCurrentView('hod');
    else if (role === 'CLASS_TEACHER') setCurrentView('class_teacher');
    else if (role === 'COURSE_TEACHER') setCurrentView('course_teacher');
    else if (role === 'TEACHER_GUARDIAN') setCurrentView('tg');
    else if (role === 'STUDENT') setCurrentView('student');
    else setCurrentView('course_teacher');
  }, [user, activeRole]);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const titles = {
    hod: 'Department Level Attendance & Compliance Analytics',
    class_teacher: `Class Teacher Division Monitoring (${user?.assigned_division || ''})`,
    audit_trail: 'Attendance Modification Audit Trail Logs',
    course_teacher: 'Course Teacher Slot Attendance Entry',
    tg: 'Teacher Guardian Mentorship Group (20 Students)',
    student: 'Student Personal Attendance Portal',
  };

  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden font-sans">
      {/* Dynamic Role-Based Sidebar */}
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar currentTitle={titles[currentView]} />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {currentView === 'hod' && <HoDDashboard />}
          {currentView === 'class_teacher' && <HoDDashboard />}
          {currentView === 'audit_trail' && <AuditTrailPage />}
          {currentView === 'course_teacher' && <CourseTeacherDashboard />}
          {currentView === 'tg' && <TGDashboard />}
          {currentView === 'student' && <StudentDashboard />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
