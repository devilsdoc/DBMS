import React, { useState, useEffect } from 'react';
import { tgApi, alertsApi } from '../services/api';
import {
  Users,
  AlertTriangle,
  CheckCircle,
  X,
  BookOpen,
  ChevronRight,
  TrendingDown,
  Mail,
  Phone,
  Sparkles,
  Bell,
  Check,
} from 'lucide-react';

export default function TGDashboard() {
  const [reports, setReports] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [triggeringCron, setTriggeringCron] = useState(false);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedStudent, setSelectedStudent] = useState(null);

  const loadAlerts = async () => {
    try {
      const data = await tgApi.getAlerts();
      setAlerts(data.alerts || []);
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      console.error('Failed to load alerts', e);
    }
  };

  useEffect(() => {
    async function fetchTGData() {
      try {
        setLoading(true);
        const data = await tgApi.getAttendanceReport();
        setReports(data);
        await loadAlerts();
      } catch (err) {
        setErrorMsg(err.message || 'Failed to load Teacher Guardian report.');
      } finally {
        setLoading(false);
      }
    }
    fetchTGData();
  }, []);

  const handleMarkRead = async (alertId) => {
    try {
      await tgApi.markAlertRead(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.alert_id === alertId ? { ...a, is_read: true } : a))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark alert as read', err);
    }
  };

  const handleTriggerDailyCron = async () => {
    setTriggeringCron(true);
    try {
      await alertsApi.triggerCheck();
      await loadAlerts();
    } catch (err) {
      console.error('Failed to trigger daily check', err);
    } finally {
      setTriggeringCron(false);
    }
  };

  const totalStudents = reports.length;
  const defaulters = reports.filter((r) => r.is_defaulter);
  const defaulterCount = defaulters.length;
  const avgAttendance =
    totalStudents > 0
      ? (
          reports.reduce((acc, curr) => acc + curr.attendance_percentage, 0) /
          totalStudents
        ).toFixed(1)
      : 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header with Notifications Bell & Cron Simulator */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs relative">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Teacher Guardian (TG) Mentorship Portal
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Monitoring designated 20-student mentee group across all department courses.
          </p>
        </div>

        {/* Action Controls: Bell Icon & Cron Trigger */}
        <div className="flex items-center space-x-3 self-start sm:self-auto">
          {/* Cron Trigger Button */}
          <button
            type="button"
            onClick={handleTriggerDailyCron}
            disabled={triggeringCron}
            title="Simulate daily 6:00 PM background check"
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200 transition flex items-center space-x-1.5 cursor-pointer"
          >
            <Sparkles className={`w-3.5 h-3.5 text-amber-500 ${triggeringCron ? 'animate-spin' : ''}`} />
            <span>{triggeringCron ? 'Scanning...' : 'Run 6 PM Cron'}</span>
          </button>

          {/* Notifications Bell Icon */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl relative text-slate-700 transition cursor-pointer"
              title="View Defaulter Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-600 text-white rounded-full text-[10px] font-black flex items-center justify-center animate-pulse shadow-sm">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown Tray */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-slate-200 p-4 z-50 animate-scale-in">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center space-x-1.5">
                    <Bell className="w-4 h-4 text-indigo-600" />
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                      Defaulter Alerts ({alerts.length})
                    </span>
                  </div>
                  <span className="text-[11px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full">
                    {unreadCount} Unread
                  </span>
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 my-2">
                  {alerts.length === 0 ? (
                    <div className="py-6 text-center text-xs text-slate-400">
                      No defaulter alerts generated for your mentees.
                    </div>
                  ) : (
                    alerts.map((al) => (
                      <div
                        key={al.alert_id}
                        className={`p-3 rounded-xl transition flex flex-col space-y-1.5 ${
                          al.is_read ? 'bg-white opacity-70' : 'bg-rose-50/50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-1.5">
                            <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0"></span>
                            <span className="text-xs font-bold text-slate-900">
                              {al.student_name} ({al.roll_no})
                            </span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-400">
                            {al.alert_date}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 font-medium leading-relaxed">
                          {al.message}
                        </p>
                        <div className="flex items-center justify-between pt-1">
                          <span className="text-[10px] font-bold text-rose-700 bg-rose-100/60 px-1.5 py-0.5 rounded">
                            Attendance: {al.attendance_percentage}%
                          </span>
                          {!al.is_read && (
                            <button
                              type="button"
                              onClick={() => handleMarkRead(al.alert_id)}
                              className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
                            >
                              <Check className="w-3 h-3" />
                              <span>Mark Read</span>
                            </button>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 text-center">
                  <button
                    type="button"
                    onClick={() => setShowNotifications(false)}
                    className="text-xs font-semibold text-slate-500 hover:text-slate-800"
                  >
                    Close Notification Panel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-sm">
          {errorMsg}
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {/* Card 1: Allotted Mentees */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Allocated Mentees
            </div>
            <div className="text-2xl font-black text-slate-900">
              {loading ? '-' : `${totalStudents} Students`}
            </div>
          </div>
        </div>

        {/* Card 2: Group Average */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Group Average
            </div>
            <div className="text-2xl font-black text-slate-900">
              {loading ? '-' : `${avgAttendance}%`}
            </div>
          </div>
        </div>

        {/* Card 3: Defaulter Summary Card (<75%) */}
        <div className="bg-gradient-to-br from-rose-50 to-rose-100/60 p-5 rounded-2xl border border-rose-200 shadow-xs flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-rose-600 text-white flex items-center justify-center font-bold shadow-md shadow-rose-600/30">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-rose-700">
              Students Below 75%
            </div>
            <div className="text-2xl font-black text-rose-900">
              {loading ? '-' : `${defaulterCount} Defaulters`}
            </div>
          </div>
        </div>
      </div>

      {/* 20-Student Mentee Attendance Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
            Mentee Group Attendance Matrix ({reports.length} Students)
          </h2>
          <span className="text-xs text-slate-600 font-medium">
            Click any student to view course-wise breakdown
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-600 text-sm flex flex-col items-center justify-center space-y-2">
            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Loading 20-student mentorship records...</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 text-xs uppercase tracking-wider font-bold">
                  <th className="py-3 px-4 w-16">#</th>
                  <th className="py-3 px-4 w-28">Roll No</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4 text-center">Conducted</th>
                  <th className="py-3 px-4 text-center">Attended</th>
                  <th className="py-3 px-4 text-center">Overall %</th>
                  <th className="py-3 px-4 text-center w-36">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {reports.map((r, idx) => (
                  <tr
                    key={r.student_id}
                    onClick={() => setSelectedStudent(r)}
                    className="hover:bg-indigo-50/40 cursor-pointer transition duration-150"
                  >
                    <td className="py-3.5 px-4 text-xs font-mono text-slate-600">{idx + 1}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-800">{r.roll_no}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">{r.student_name}</td>
                    <td className="py-3.5 px-4 text-center text-slate-700 font-medium">{r.total_conducted}</td>
                    <td className="py-3.5 px-4 text-center text-slate-700 font-medium">{r.total_attended}</td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="font-extrabold text-sm font-mono text-slate-900">
                        {r.attendance_percentage}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {r.is_defaulter ? (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 bg-rose-100 text-rose-700 font-bold text-xs rounded-full border border-rose-200 shadow-xs">
                          <AlertTriangle className="w-3 h-3 shrink-0" />
                          <span>&lt; 75% Defaulter</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 bg-emerald-100 text-emerald-700 font-bold text-xs rounded-full border border-emerald-200">
                          <CheckCircle className="w-3 h-3 shrink-0" />
                          <span>Good Standing</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        type="button"
                        className="text-indigo-600 hover:text-indigo-800 font-semibold text-xs flex items-center space-x-1 ml-auto"
                      >
                        <span>View</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Course-Wise Breakdown Modal */}
      {selectedStudent && (
        <div
          className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedStudent(null)}
        >
          <div
            className="bg-white rounded-3xl shadow-2xl border border-slate-200 max-w-2xl w-full p-6 space-y-5 animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-slate-100">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {selectedStudent.roll_no}
                  </span>
                  <h3 className="text-lg font-bold text-slate-900">
                    {selectedStudent.student_name}
                  </h3>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Overall Mentee Attendance:{' '}
                  <span className="font-bold text-slate-800">
                    {selectedStudent.attendance_percentage}%
                  </span>{' '}
                  ({selectedStudent.total_attended} / {selectedStudent.total_conducted} sessions)
                </p>
              </div>

              <button
                type="button"
                onClick={() => setSelectedStudent(null)}
                className="p-1.5 rounded-xl bg-slate-100 text-slate-500 hover:bg-slate-200 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Course Breakdown Table */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-indigo-600" />
                <span>Course-by-Course Attendance</span>
              </h4>

              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200">
                      <th className="py-2.5 px-3">Code</th>
                      <th className="py-2.5 px-3">Course Name</th>
                      <th className="py-2.5 px-3 text-center">Held</th>
                      <th className="py-2.5 px-3 text-center">Attended</th>
                      <th className="py-2.5 px-3 text-center">Subject %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {selectedStudent.subject_wise.map((c) => (
                      <tr key={c.course_id} className="hover:bg-slate-50/50">
                        <td className="py-2.5 px-3 font-mono font-bold text-indigo-700">{c.course_code}</td>
                        <td className="py-2.5 px-3 font-medium text-slate-800">{c.course_name}</td>
                        <td className="py-2.5 px-3 text-center text-slate-600">{c.conducted}</td>
                        <td className="py-2.5 px-3 text-center text-slate-600 font-semibold">{c.attended}</td>
                        <td className="py-2.5 px-3 text-center">
                          <span
                            className={`font-bold font-mono px-2 py-0.5 rounded-full text-[11px] ${
                              c.percentage < 75
                                ? 'bg-rose-100 text-rose-700'
                                : 'bg-emerald-100 text-emerald-700'
                            }`}
                          >
                            {c.percentage}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Action Footer */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Teacher Guardian Review Log</span>
              <button
                type="button"
                onClick={() => setSelectedStudent(null)}
                className="px-4 py-2 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition"
              >
                Close View
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
