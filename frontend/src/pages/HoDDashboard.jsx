import React, { useState, useEffect } from 'react';
import { reportsApi } from '../services/api';
import { useAuth } from '../context/AuthContext';
import {
  BarChart3,
  Users,
  AlertTriangle,
  CheckCircle,
  Building2,
  Download,
  Search,
  BookOpen,
  Mail,
  Phone,
  Layers,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

export default function HoDDashboard() {
  const { user } = useAuth();
  const isHod = user?.roles?.includes('HOD') || user?.id === 'EMP001';

  // Allowed divisions
  const [selectedDiv, setSelectedDiv] = useState(
    isHod ? 'DIV01' : user?.assigned_division || 'DIV01'
  );

  const [divisionReport, setDivisionReport] = useState(null);
  const [allDivisionAverages, setAllDivisionAverages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // 1. Fetch current division report
  useEffect(() => {
    async function loadReport() {
      try {
        setLoading(true);
        setErrorMsg('');
        const data = await reportsApi.getDivisionReport(selectedDiv);
        setDivisionReport(data);
      } catch (err) {
        setErrorMsg(err.message || 'Failed to load division report.');
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [selectedDiv]);

  // 2. If HoD, fetch comparative averages across all 3 divisions
  useEffect(() => {
    if (!isHod) return;
    async function loadComparisons() {
      try {
        const divs = ['DIV01', 'DIV02', 'DIV03'];
        const results = await Promise.all(
          divs.map((d) => reportsApi.getDivisionReport(d).catch(() => null))
        );
        const mapped = results
          .filter(Boolean)
          .map((r) => ({
            name: r.div_name,
            average: r.division_average_percentage,
            defaulters: r.defaulters_count,
            students: r.total_students,
          }));
        setAllDivisionAverages(mapped);
      } catch (e) {
        console.error('Failed to load multi-division comparisons', e);
      }
    }
    loadComparisons();
  }, [isHod]);

  const defaultersList = divisionReport?.defaulters || [];
  const filteredDefaulters = defaultersList.filter(
    (d) =>
      d.roll_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.student_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Prepare Course Bar Chart Data
  const courseChartData =
    divisionReport?.course_statistics?.map((c) => ({
      name: c.course_code,
      fullName: c.course_name,
      average: c.average_percentage,
    })) || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Division Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            {isHod ? 'Department Attendance & Defaulter Analytics' : 'Class Teacher Division Portal'}
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Aggregated statistics, course performance metrics, and compliance monitoring (<span className="text-rose-600 font-bold">&lt; 75%</span> threshold).
          </p>
        </div>

        {/* Division Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Division:
          </label>
          {isHod ? (
            <select
              value={selectedDiv}
              onChange={(e) => setSelectedDiv(e.target.value)}
              className="px-3.5 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-bold text-indigo-700 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            >
              <option value="DIV01">SY-A (DIV01)</option>
              <option value="DIV02">SY-B (DIV02)</option>
              <option value="DIV03">TY-A (DIV03)</option>
            </select>
          ) : (
            <span className="px-3 py-1 bg-indigo-50 text-indigo-700 font-bold text-sm rounded-xl border border-indigo-200">
              {divisionReport?.div_name || user?.assigned_division}
            </span>
          )}

          {/* Export CSV Button */}
          <button
            type="button"
            onClick={async () => {
              try {
                await reportsApi.downloadCsv(selectedDiv);
              } catch (err) {
                alert('Export failed: ' + err.message);
              }
            }}
            className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition flex items-center space-x-1.5 cursor-pointer"
            title="Export full attendance report as CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-sm">
          {errorMsg}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
            Division Average %
          </div>
          <div className="text-3xl font-black text-slate-900 font-mono">
            {loading ? '-' : `${divisionReport?.division_average_percentage}%`}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Class Teacher: <span className="font-semibold text-slate-700">{divisionReport?.class_teacher_name || 'Assigned'}</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
            Total Students Enrolled
          </div>
          <div className="text-3xl font-black text-slate-900 font-mono">
            {loading ? '-' : `${divisionReport?.total_students}`}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Division: <span className="font-semibold text-slate-700">{divisionReport?.div_name}</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
            Conducted Sessions
          </div>
          <div className="text-3xl font-black text-slate-900 font-mono">
            {loading ? '-' : `${divisionReport?.total_sessions_conducted}`}
          </div>
          <div className="text-xs text-slate-500 mt-1">Past 10 working days</div>
        </div>

        <div className="bg-gradient-to-br from-rose-50 to-rose-100/50 p-5 rounded-2xl border border-rose-200 shadow-xs">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-700 mb-1">
            Defaulter Students (&lt;75%)
          </div>
          <div className="text-3xl font-black text-rose-900 font-mono">
            {loading ? '-' : `${divisionReport?.defaulters_count}`}
          </div>
          <div className="text-xs text-rose-700 mt-1 font-medium">Require parent intimation</div>
        </div>
      </div>

      {/* Visual Analytics Charts (Recharts) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Course-wise Attendance in Division */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
              <BookOpen className="w-4 h-4 text-indigo-600" />
              <span>Course Attendance Performance ({divisionReport?.div_name})</span>
            </h2>
            <span className="text-xs text-slate-500 font-medium">Avg % per subject</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={courseChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${val}%`, 'Average Attendance']}
                  labelFormatter={(name) => `Course Code: ${name}`}
                />
                <Bar dataKey="average" radius={[6, 6, 0, 0]}>
                  {courseChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.average < 75 ? '#f43f5e' : '#6366f1'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Cross-Division Comparison (HoD Exclusive) */}
        {isHod && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
                <BarChart3 className="w-4 h-4 text-indigo-600" />
                <span>Department Cross-Division Benchmark</span>
              </h2>
              <span className="text-xs text-slate-500 font-medium">SY-A vs SY-B vs TY-A</span>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={allDivisionAverages} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(val) => [`${val}%`, 'Division Average']} />
                  <Bar dataKey="average" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* Defaulter Students Table (< 75%) */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-rose-500 animate-pulse"></div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
              Division Defaulter Roster (&lt; 75% Attendance)
            </h2>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-700">
              {defaultersList.length} Found
            </span>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search roll or student..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500 text-sm">Loading defaulters list...</div>
        ) : filteredDefaulters.length === 0 ? (
          <div className="p-8 text-center text-emerald-700 text-sm font-medium flex items-center justify-center space-x-2">
            <CheckCircle className="w-5 h-5 text-emerald-600" />
            <span>All students in {divisionReport?.div_name} are maintaining &ge; 75% attendance!</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 text-xs uppercase tracking-wider font-bold">
                  <th className="py-3 px-4 w-28">Roll No</th>
                  <th className="py-3 px-4 w-32">Student ID</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4 text-center">Sessions Held</th>
                  <th className="py-3 px-4 text-center">Attended</th>
                  <th className="py-3 px-4 text-center">Attendance %</th>
                  <th className="py-3 px-4">Contact Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredDefaulters.map((d) => (
                  <tr key={d.student_id} className="hover:bg-rose-50/20 transition">
                    <td className="py-3 px-4 font-mono font-bold text-slate-800">{d.roll_no}</td>
                    <td className="py-3 px-4 text-xs font-mono text-slate-600">{d.student_id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-900">{d.student_name}</td>
                    <td className="py-3 px-4 text-center text-slate-600 font-medium">{d.total_conducted}</td>
                    <td className="py-3 px-4 text-center text-slate-600 font-medium">{d.total_attended}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-extrabold font-mono text-xs px-2.5 py-1 rounded-full bg-rose-100 text-rose-700 border border-rose-200">
                        {d.attendance_percentage}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-xs text-slate-500 space-y-0.5">
                      <div className="flex items-center space-x-1.5">
                        <Mail className="w-3 h-3 text-slate-400" />
                        <span>{d.email}</span>
                      </div>
                      <div className="flex items-center space-x-1.5 font-mono">
                        <Phone className="w-3 h-3 text-slate-400" />
                        <span>+91 {d.phone}</span>
                      </div>
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
