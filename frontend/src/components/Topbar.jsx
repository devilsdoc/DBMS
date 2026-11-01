import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Bell, Calendar, Shield } from 'lucide-react';

export default function Topbar({ currentTitle }) {
  const { user, logout, activeRole } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
      {/* Title & Context */}
      <div className="flex items-center space-x-3">
        <div className="h-7 w-1.5 bg-indigo-600 rounded-full"></div>
        <div>
          <h2 className="text-lg font-bold text-slate-800 tracking-tight leading-tight">
            {currentTitle || 'Attendance Management System'}
          </h2>
          <p className="text-xs text-slate-600">
            CSE Department &bull; Mon–Fri Academic Schedule (6 Slots/Day)
          </p>
        </div>
      </div>

      {/* Right User Actions */}
      <div className="flex items-center space-x-4">
        {/* Academic Calendar Tag */}
        <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 bg-slate-100 text-slate-700 rounded-lg text-xs font-medium">
          <Calendar className="w-3.5 h-3.5 text-slate-500" />
          <span>AY 2024–2025</span>
        </div>

        {/* User Card */}
        <div className="flex items-center space-x-3 pl-2 border-l border-slate-200">
          <div className="w-9 h-9 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-sm border border-indigo-200">
            {user?.name ? user.name.charAt(0) : 'U'}
          </div>
          <div className="hidden md:block text-left">
            <div className="text-sm font-semibold text-slate-800 leading-tight">
              {user?.name}
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xs text-slate-600">{user?.id}</span>
              <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                {activeRole || user?.roles?.[0]}
              </span>
            </div>
          </div>
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          title="Sign out"
          className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition duration-150 cursor-pointer"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
}
