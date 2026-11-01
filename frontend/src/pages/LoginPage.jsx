import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Lock, User, AlertCircle, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const { login, loading } = useAuth();
  const [username, setUsername] = useState('EMP001');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    }
  };

  const setDemoRole = (userVal) => {
    setUsername(userVal);
    setPassword('password123');
    setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md">
        {/* Department Crest / Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-blue-600 items-center justify-center shadow-xl shadow-indigo-500/25 mb-3 border border-indigo-400/30">
            <GraduationCap className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            CSE Department
          </h1>
          <p className="text-sm text-slate-300 font-medium mt-1">
            Centralized Attendance Management & Monitoring System
          </p>
        </div>

        {/* Card Form */}
        <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-8 space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Welcome back</h2>
            <p className="text-xs text-slate-500">Sign in with your Emp ID (EMPxxx) or Student ID (Sxxx)</p>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-start space-x-2.5 text-rose-700 text-xs animate-shake">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                User Identifier
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  placeholder="e.g. EMP001 or S001"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="password"
                  required
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition duration-150 flex items-center justify-center space-x-2 disabled:opacity-60 cursor-pointer"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>Sign In to Portal</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Role Logins */}
          <div className="pt-4 border-t border-slate-100">
            <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-500 mb-2.5 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>One-Click Role Demonstration</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => setDemoRole('EMP001')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition font-medium"
              >
                <div className="font-bold text-indigo-700">HoD</div>
                <div className="text-[11px] text-slate-500">Dr. Ramesh (EMP001)</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('EMP002')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition font-medium"
              >
                <div className="font-bold text-indigo-700">Class Teacher</div>
                <div className="text-[11px] text-slate-500">Dr. Sunita (SY-A)</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('EMP005')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition font-medium"
              >
                <div className="font-bold text-indigo-700">Course Teacher</div>
                <div className="text-[11px] text-slate-500">Prof. Vikram (DS)</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('EMP006')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 transition font-medium"
              >
                <div className="font-bold text-indigo-700">Teacher Guardian</div>
                <div className="text-[11px] text-slate-500">Prof. Neha (TG01)</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('S001')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-emerald-400 hover:bg-emerald-50/50 transition font-medium"
              >
                <div className="font-bold text-emerald-700">Student (Good)</div>
                <div className="text-[11px] text-slate-500">Aarav Sharma (91%)</div>
              </button>

              <button
                type="button"
                onClick={() => setDemoRole('S005')}
                className="p-2 text-left rounded-lg border border-slate-200 hover:border-rose-400 hover:bg-rose-50/50 transition font-medium"
              >
                <div className="font-bold text-rose-700">Student (Defaulter)</div>
                <div className="text-[11px] text-slate-500">Karan M. (56%)</div>
              </button>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          &copy; {new Date().getFullYear()} CSE Attendance System. Secured with Bcrypt & JWT.
        </p>
      </div>
    </div>
  );
}
