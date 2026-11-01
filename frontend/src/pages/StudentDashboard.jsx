import React, { useState, useEffect } from 'react';
import { studentApi } from '../services/api';
import {
  GraduationCap,
  Calendar,
  AlertTriangle,
  CheckCircle,
  BookOpen,
  Clock,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function StudentDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    async function loadAttendance() {
      try {
        setLoading(true);
        const res = await studentApi.getMyAttendance();
        setData(res);
      } catch (err) {
        setErrorMsg(err.message || 'Failed to load student attendance dashboard.');
      } finally {
        setLoading(false);
      }
    }
    loadAttendance();
  }, []);

  if (loading) {
    return (
      <div className="p-16 text-center text-slate-500 text-sm flex flex-col items-center justify-center space-y-3">
        <div className="w-9 h-9 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        <span>Loading your personal attendance records...</span>
      </div>
    );
  }

  if (errorMsg || !data) {
    return (
      <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-sm">
        {errorMsg || 'Unable to retrieve attendance data.'}
      </div>
    );
  }

  const {
    student_name,
    roll_no,
    div_name,
    total_conducted,
    total_attended,
    overall_percentage,
    is_defaulter,
    courses,
    absent_dates,
  } = data;

  const totalMissed = total_conducted - total_attended;

  // Pie chart data
  const chartData = [
    { name: 'Attended', value: total_attended, color: '#10b981' }, // Emerald
    { name: 'Missed', value: totalMissed, color: '#f43f5e' }, // Rose
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Student Welcome & Profile Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-3xl shadow-xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center font-bold text-xl text-indigo-300">
              <GraduationCap className="w-8 h-8 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-black tracking-tight">{student_name}</h1>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                  {div_name}
                </span>
              </div>
              <p className="text-xs text-indigo-200/80 font-mono mt-0.5">
                Roll No: {roll_no} &bull; CSE Department
              </p>
            </div>
          </div>

          {/* Standing Badge */}
          <div>
            {is_defaulter ? (
              <div className="px-4 py-2 bg-rose-500/20 border border-rose-400/40 rounded-2xl flex items-center space-x-2 text-rose-300">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">Defaulter Alert</div>
                  <div className="text-[11px] text-rose-200">Attendance is under the 75% threshold</div>
                </div>
              </div>
            ) : (
              <div className="px-4 py-2 bg-emerald-500/20 border border-emerald-400/40 rounded-2xl flex items-center space-x-2 text-emerald-300">
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">Good Standing</div>
                  <div className="text-[11px] text-emerald-200">Above mandated 75% attendance</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Stats: Overall Percentage & Progress Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Percentage Card with Chart */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
              Overall Attendance Status
            </h2>
            <div className="flex items-baseline space-x-2">
              <span className="text-4xl font-black text-slate-900 font-mono">
                {overall_percentage}%
              </span>
              <span
                className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  is_defaulter
                    ? 'bg-rose-100 text-rose-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                {is_defaulter ? 'Shortfall' : 'Compliant'}
              </span>
            </div>
          </div>

          {/* Recharts Pie Visualization */}
          <div className="h-44 my-2 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={68}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-xl font-bold font-mono text-slate-800">
                {total_attended} / {total_conducted}
              </span>
              <span className="text-[10px] text-slate-400 uppercase font-semibold">
                Attended
              </span>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100 text-center">
            <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-800">
              <div className="text-[11px] font-bold uppercase">Lectures Attended</div>
              <div className="text-lg font-black font-mono">{total_attended}</div>
            </div>
            <div className="p-2.5 rounded-xl bg-rose-50 text-rose-800">
              <div className="text-[11px] font-bold uppercase">Lectures Missed</div>
              <div className="text-lg font-black font-mono">{totalMissed}</div>
            </div>
          </div>
        </div>

        {/* Course-Wise Progress Grid */}
        <div className="lg:col-span-2 bg-white p-6 rounded-3xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
              <BookOpen className="w-4 h-4 text-indigo-600" />
              <span>Course Breakdown ({courses.length} Subjects)</span>
            </h2>
            <span className="text-xs text-slate-600 font-medium">Target: &ge; 75% per course</span>
          </div>

          <div className="space-y-3.5">
            {courses.map((c) => {
              const isCourseDefaulter = c.percentage < 75.0;
              return (
                <div key={c.course_id} className="p-3.5 bg-slate-50/70 rounded-2xl border border-slate-100">
                  <div className="flex items-center justify-between mb-1.5">
                    <div>
                      <span className="font-mono text-xs font-bold text-indigo-700 mr-2">
                        {c.course_code}
                      </span>
                      <span className="text-sm font-semibold text-slate-800">
                        {c.course_name}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-600 font-mono">
                        {c.attended} / {c.conducted}
                      </span>
                      <span
                        className={`text-xs font-extrabold font-mono px-2 py-0.5 rounded-md ${
                          isCourseDefaulter
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}
                      >
                        {c.percentage}%
                      </span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isCourseDefaulter ? 'bg-rose-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(c.percentage, 100)}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Recent Absences Log */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-xs p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
            <Clock className="w-4 h-4 text-rose-600" />
            <span>Recent Absences Record</span>
          </h2>
          <span className="text-xs text-slate-600">
            {absent_dates.length} sessions missed across past weeks
          </span>
        </div>

        {absent_dates.length === 0 ? (
          <div className="p-6 bg-emerald-50 text-emerald-800 rounded-2xl text-xs font-semibold flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <span>Perfect attendance recorded! No missed lectures in the archive.</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {absent_dates.slice(0, 9).map((ab, idx) => (
              <div
                key={idx}
                className="p-3 bg-slate-50 border border-slate-200/80 rounded-xl flex items-start space-x-3 text-xs"
              >
                <div className="w-8 h-8 rounded-lg bg-rose-100 text-rose-700 font-bold flex items-center justify-center shrink-0">
                  S{ab.slot_no}
                </div>
                <div>
                  <div className="font-bold text-slate-900">{ab.date}</div>
                  <div className="text-[11px] text-slate-500 font-medium truncate">
                    {ab.course_code} - {ab.course_name}
                  </div>
                  <span className="inline-block mt-1 text-[10px] font-bold text-rose-700 bg-rose-50 px-1.5 py-0.2 rounded">
                    Unexcused Absence
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
