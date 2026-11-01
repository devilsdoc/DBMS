import React, { useState, useEffect } from 'react';
import { auditApi } from '../services/api';
import {
  ShieldAlert,
  Search,
  RefreshCw,
  Clock,
  ArrowRight,
  User,
  BookOpen,
  Calendar,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';

export default function AuditTrailPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setErrorMsg('');
      const data = await auditApi.getLogs();
      setLogs(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to load audit trail logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(
    (l) =>
      l.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.roll_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.modified_by_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.course_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.reason.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-indigo-600" />
            <span>Attendance Modification Audit Trail</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Immutable log of all retroactive attendance changes, including authorized faculty, timestamps, and justifications.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition flex items-center space-x-1.5 self-start sm:self-auto cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Logs</span>
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Showing {filteredLogs.length} Logged Entries
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by student, roll, faculty, reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-16 text-center text-slate-500 text-sm flex flex-col items-center justify-center space-y-2">
            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Loading audit trail logs...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No attendance modification records found matching search.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase tracking-wider font-bold">
                  <th className="py-3 px-4 w-28">Log Date & Time</th>
                  <th className="py-3 px-4 w-36">Student</th>
                  <th className="py-3 px-4 w-32">Course</th>
                  <th className="py-3 px-4 w-28">Lecture Slot</th>
                  <th className="py-3 px-4 text-center w-40">Status Change</th>
                  <th className="py-3 px-4 w-44">Modified By</th>
                  <th className="py-3 px-4">Authorized Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLogs.map((log) => (
                  <tr key={log.audit_id} className="hover:bg-slate-50/70 transition">
                    {/* Timestamp */}
                    <td className="py-3 px-4 text-slate-500 font-mono">
                      <div>{log.timestamp ? log.timestamp.split('T')[0] : 'N/A'}</div>
                      <div className="text-[10px] text-slate-400">
                        {log.timestamp ? log.timestamp.split('T')[1].slice(0, 8) : ''}
                      </div>
                    </td>

                    {/* Student */}
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-800">{log.student_name}</div>
                      <div className="font-mono text-[11px] text-indigo-700">
                        {log.roll_no} &bull; {log.div_name}
                      </div>
                    </td>

                    {/* Course */}
                    <td className="py-3 px-4">
                      <div className="font-mono font-bold text-slate-700">{log.course_code}</div>
                      <div className="text-[11px] text-slate-500 truncate max-w-[140px]">
                        {log.course_name}
                      </div>
                    </td>

                    {/* Lecture Date & Slot */}
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      <div>{log.attendance_date}</div>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700">
                        Slot {log.slot_no}
                      </span>
                    </td>

                    {/* Status Change (Old -> New) */}
                    <td className="py-3 px-4 text-center">
                      <div className="inline-flex items-center space-x-1.5 p-1 bg-slate-50 border border-slate-200 rounded-lg text-[11px]">
                        <span
                          className={`font-bold px-1.5 py-0.5 rounded ${
                            log.old_value === 'Absent'
                              ? 'bg-rose-100 text-rose-700'
                              : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {log.old_value}
                        </span>
                        <ArrowRight className="w-3 h-3 text-slate-400" />
                        <span
                          className={`font-bold px-1.5 py-0.5 rounded ${
                            log.new_value === 'Present'
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-rose-100 text-rose-700'
                          }`}
                        >
                          {log.new_value}
                        </span>
                      </div>
                    </td>

                    {/* Faculty */}
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-800">{log.modified_by_name}</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {log.modified_by_emp_id} &bull; {log.ip_address || '127.0.0.1'}
                      </div>
                    </td>

                    {/* Reason */}
                    <td className="py-3 px-4 text-slate-600">
                      <p className="bg-slate-50 p-2 rounded-lg border border-slate-100 text-[11px] font-medium leading-relaxed">
                        &ldquo;{log.reason}&rdquo;
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
