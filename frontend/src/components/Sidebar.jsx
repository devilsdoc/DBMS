import React from 'react';
import { useAuth } from '../context/AuthContext';
import {
  GraduationCap,
  Users,
  BookOpen,
  BarChart3,
  CheckCircle2,
  Calendar,
  Layers,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';

export default function Sidebar({ currentView, setCurrentView }) {
  const { user, activeRole, setActiveRole } = useAuth();
  if (!user) return null;

  const roles = user.roles || [];

  // Determine navigable tabs based on assigned roles
  const navItems = [];

  if (roles.includes('HOD')) {
    navItems.push({
      id: 'hod',
      label: 'HoD Department Analytics',
      icon: BarChart3,
      badge: 'Dept Head',
    });
  }

  if (roles.includes('CLASS_TEACHER')) {
    navItems.push({
      id: 'class_teacher',
      label: `Class Teacher (${user.assigned_division || 'Division'})`,
      icon: Layers,
      badge: user.assigned_division,
    });
  }

  if (roles.includes('HOD') || roles.includes('CLASS_TEACHER')) {
    navItems.push({
      id: 'audit_trail',
      label: 'Audit Trail Logs',
      icon: ShieldAlert,
      badge: 'Audits',
    });
  }

  if (roles.includes('COURSE_TEACHER')) {
    navItems.push({
      id: 'course_teacher',
      label: 'Mark Slot Attendance',
      icon: CheckCircle2,
      badge: 'Course Faculty',
    });
  }

  if (roles.includes('TEACHER_GUARDIAN')) {
    navItems.push({
      id: 'tg',
      label: 'TG Mentorship (20 Students)',
      icon: Users,
      badge: user.tg_id || 'TG Group',
    });
  }

  if (roles.includes('STUDENT')) {
    navItems.push({
      id: 'student',
      label: 'My Attendance Portal',
      icon: GraduationCap,
      badge: 'Student',
    });
  }

  return (
    <aside className="w-72 bg-slate-900 text-slate-100 flex flex-col border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3 bg-slate-950/40">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <GraduationCap className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight text-white leading-tight">
            CSE Attendance
          </h1>
          <p className="text-xs text-indigo-400 font-medium">Department Portal</p>
        </div>
      </div>

      {/* User Hybrid Role Badge Switcher */}
      {roles.length > 1 && (
        <div className="px-4 py-3 bg-slate-800/40 border-b border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5 font-medium">
            <span>SWITCH ACTIVE ROLE:</span>
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {roles.map((r) => (
              <button
                key={r}
                onClick={() => {
                  setActiveRole(r);
                  if (r === 'HOD') setCurrentView('hod');
                  else if (r === 'CLASS_TEACHER') setCurrentView('class_teacher');
                  else if (r === 'COURSE_TEACHER') setCurrentView('course_teacher');
                  else if (r === 'TEACHER_GUARDIAN') setCurrentView('tg');
                  else if (r === 'STUDENT') setCurrentView('student');
                }}
                className={`text-[11px] font-semibold px-2 py-0.5 rounded transition ${
                  activeRole === r
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {r.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Links */}
      <div className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Dashboard Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition duration-150 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    isActive
                      ? 'bg-indigo-500 text-white'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/30 text-xs text-slate-400 space-y-1">
        <div className="flex items-center justify-between">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-medium text-slate-300">Live DB Connected</span>
          </span>
          <span className="text-[11px] text-slate-500">AY 2024-25</span>
        </div>
        <p className="text-[11px] text-slate-400 truncate">Emp/ID: {user.id}</p>
      </div>
    </aside>
  );
}
