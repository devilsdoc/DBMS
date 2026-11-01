import React, { useState, useEffect } from 'react';
import { teacherApi } from '../services/api';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Send,
  AlertCircle,
  Calendar,
  Layers,
  Search,
  Filter,
  Sparkles,
} from 'lucide-react';

export default function CourseTeacherDashboard() {
  const [courses, setCourses] = useState([]);
  const [selectedCourseKey, setSelectedCourseKey] = useState('');
  const [sessionDate, setSessionDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [slotNo, setSlotNo] = useState(1);
  const [topicsCovered, setTopicsCovered] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // 60 students attendance map: { student_id: 'Present' | 'Absent' | 'Late' }
  const [attendanceMap, setAttendanceMap] = useState({});
  const [students, setStudents] = useState([]);

  const [loadingCourses, setLoadingCourses] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // 1. Fetch Assigned Courses on Mount
  useEffect(() => {
    async function loadCourses() {
      try {
        setLoadingCourses(true);
        const data = await teacherApi.getMyCourses();
        setCourses(data);
        if (data.length > 0) {
          const firstKey = `${data[0].course_id}|${data[0].div_id}`;
          setSelectedCourseKey(firstKey);
        }
      } catch (err) {
        setErrorMsg(err.message || 'Failed to load assigned courses.');
      } finally {
        setLoadingCourses(false);
      }
    }
    loadCourses();
  }, []);

  // 2. Generate / Load the 60 students for the selected division
  useEffect(() => {
    if (!selectedCourseKey) return;
    const [, divId] = selectedCourseKey.split('|');

    // Generate 60 students for this division based on Div_ID
    // DIV01: S001 to S060, DIV02: S061 to S120, DIV03: S121 to S180
    let startIdx = 1;
    let rollPrefix = 'SYA';
    if (divId === 'DIV02') {
      startIdx = 61;
      rollPrefix = 'SYB';
    } else if (divId === 'DIV03') {
      startIdx = 121;
      rollPrefix = 'TYA';
    }

    const initialStudents = [];
    const initialMap = {};

    for (let i = 0; i < 60; i++) {
      const num = startIdx + i;
      const sId = `S${String(num).padStart(3, '0')}`;
      const rollNo = `${rollPrefix}${String(i + 1).padStart(3, '0')}`;
      initialStudents.push({
        student_id: sId,
        roll_no: rollNo,
        student_name: `Student ${sId} (${rollNo})`,
      });
      initialMap[sId] = 'Present'; // Default to Present
    }

    setStudents(initialStudents);
    setAttendanceMap(initialMap);
  }, [selectedCourseKey]);

  // Bulk actions
  const markAll = (status) => {
    const updated = {};
    students.forEach((s) => {
      updated[s.student_id] = status;
    });
    setAttendanceMap(updated);
  };

  const handleStatusChange = (studentId, status) => {
    setAttendanceMap((prev) => ({
      ...prev,
      [studentId]: status,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');

    if (!selectedCourseKey) {
      setErrorMsg('Please select a course and division.');
      return;
    }

    const [courseId, divId] = selectedCourseKey.split('|');

    const records = Object.entries(attendanceMap).map(([studentId, status]) => ({
      student_id: studentId,
      status,
    }));

    const payload = {
      session_date: sessionDate,
      slot_no: parseInt(slotNo, 10),
      course_id: courseId,
      div_id: divId,
      topics_covered: topicsCovered || `Lecture slot ${slotNo} for ${courseId}.`,
      records,
    };

    setSubmitting(true);
    try {
      const res = await teacherApi.submitAttendance(payload);
      setSuccessMsg(res.message || 'Attendance recorded and committed successfully!');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit attendance.');
    } finally {
      setSubmitting(false);
    }
  };

  const presentCount = Object.values(attendanceMap).filter(
    (s) => s === 'Present'
  ).length;
  const absentCount = Object.values(attendanceMap).filter(
    (s) => s === 'Absent'
  ).length;
  const lateCount = Object.values(attendanceMap).filter(
    (s) => s === 'Late'
  ).length;

  const filteredStudents = students.filter(
    (s) =>
      s.roll_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.student_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Title & Overview */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Record Slot Attendance
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Conduct atomic attendance submission with automatic rollback and duplication protection.
          </p>
        </div>

        {/* Live Counters */}
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-xs font-bold flex items-center space-x-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Present: {presentCount}</span>
          </span>
          <span className="px-3 py-1.5 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold flex items-center space-x-1.5">
            <XCircle className="w-3.5 h-3.5" />
            <span>Absent: {absentCount}</span>
          </span>
          <span className="px-3 py-1.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-xl text-xs font-bold flex items-center space-x-1.5">
            <Clock className="w-3.5 h-3.5" />
            <span>Late: {lateCount}</span>
          </span>
        </div>
      </div>

      {/* Notifications */}
      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center space-x-3 text-emerald-800 text-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span className="font-medium">{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center space-x-3 text-rose-800 text-sm animate-fade-in">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span className="font-medium">{errorMsg}</span>
        </div>
      )}

      {/* Control Panel: Course, Division, Date, Slot */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
          <Layers className="w-4 h-4 text-indigo-600" />
          <span>Session Configuration</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Course & Division Dropdown */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Assigned Course & Division
            </label>
            {loadingCourses ? (
              <div className="h-10 bg-slate-100 rounded-xl animate-pulse"></div>
            ) : courses.length === 0 ? (
              <p className="text-xs text-rose-600 font-medium">No courses assigned to your Emp ID.</p>
            ) : (
              <select
                value={selectedCourseKey}
                onChange={(e) => setSelectedCourseKey(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
              >
                {courses.map((c) => (
                  <option key={`${c.course_id}|${c.div_id}`} value={`${c.course_id}|${c.div_id}`}>
                    {c.course_code} - {c.course_name} ({c.div_name})
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Date Picker */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Session Date
            </label>
            <input
              type="date"
              value={sessionDate}
              onChange={(e) => setSessionDate(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            />
          </div>

          {/* Slot Number */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Lecture Slot (1 to 6)
            </label>
            <select
              value={slotNo}
              onChange={(e) => setSlotNo(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            >
              <option value={1}>Slot 1 (09:00 - 10:00)</option>
              <option value={2}>Slot 2 (10:00 - 11:00)</option>
              <option value={3}>Slot 3 (11:15 - 12:15)</option>
              <option value={4}>Slot 4 (13:15 - 14:15)</option>
              <option value={5}>Slot 5 (14:15 - 15:15)</option>
              <option value={6}>Slot 6 (15:30 - 16:30)</option>
            </select>
          </div>

          {/* Topics Covered */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Topics Covered (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Binary Search Trees & AVL"
              value={topicsCovered}
              onChange={(e) => setTopicsCovered(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none transition"
            />
          </div>
        </div>

        {/* Quick Bulk Marking Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-500">Quick Actions:</span>
            <button
              type="button"
              onClick={() => markAll('Present')}
              className="px-3 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-lg transition"
            >
              Mark All Present
            </button>
            <button
              type="button"
              onClick={() => markAll('Absent')}
              className="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold rounded-lg transition"
            >
              Mark All Absent
            </button>
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Filter by roll or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* 60-Student Attendance Entry Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-slate-100/75 border-b border-slate-200 text-slate-600 text-xs uppercase tracking-wider font-bold">
                <th className="py-3 px-4 w-16">#</th>
                <th className="py-3 px-4 w-28">Roll No</th>
                <th className="py-3 px-4 w-32">Student ID</th>
                <th className="py-3 px-4">Student Name</th>
                <th className="py-3 px-6 text-center w-72">Attendance Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredStudents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400 text-sm">
                    No matching students found in this division.
                  </td>
                </tr>
              ) : (
                filteredStudents.map((st, idx) => {
                  const currentStatus = attendanceMap[st.student_id] || 'Present';
                  return (
                    <tr
                      key={st.student_id}
                      className={`hover:bg-slate-50/80 transition ${
                        currentStatus === 'Absent' ? 'bg-rose-50/30' : ''
                      }`}
                    >
                      <td className="py-3 px-4 text-xs font-mono text-slate-600">{idx + 1}</td>
                      <td className="py-3 px-4 font-mono font-bold text-slate-800">{st.roll_no}</td>
                      <td className="py-3 px-4 text-xs font-mono text-slate-600">{st.student_id}</td>
                      <td className="py-3 px-4 font-medium text-slate-900">{st.student_name}</td>
                      <td className="py-3 px-6">
                        <div className="flex items-center justify-center space-x-1.5 bg-slate-100 p-1 rounded-xl">
                          <button
                            type="button"
                            onClick={() => handleStatusChange(st.student_id, 'Present')}
                            className={`flex-1 py-1 px-3 text-xs font-bold rounded-lg transition ${
                              currentStatus === 'Present'
                                ? 'bg-emerald-600 text-white shadow-xs'
                                : 'text-slate-600 hover:text-slate-900'
                            }`}
                          >
                            Present
                          </button>
                          <button
                            type="button"
                            onClick={() => handleStatusChange(st.student_id, 'Absent')}
                            className={`flex-1 py-1 px-3 text-xs font-bold rounded-lg transition ${
                              currentStatus === 'Absent'
                                ? 'bg-rose-600 text-white shadow-xs'
                                : 'text-slate-600 hover:text-slate-900'
                            }`}
                          >
                            Absent
                          </button>
                          <button
                            type="button"
                            onClick={() => handleStatusChange(st.student_id, 'Late')}
                            className={`flex-1 py-1 px-3 text-xs font-bold rounded-lg transition ${
                              currentStatus === 'Late'
                                ? 'bg-amber-500 text-white shadow-xs'
                                : 'text-slate-600 hover:text-slate-900'
                            }`}
                          >
                            Late
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Submit Attendance Sticky Action Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-slate-500 font-medium">
            Ready to commit attendance for <span className="font-bold text-slate-700">{students.length} students</span>.
            Transactions ensure atomic commit with zero partial saves.
          </div>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting || students.length === 0}
            className="w-full sm:w-auto px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-xl shadow-md shadow-indigo-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer"
          >
            {submitting ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Submit Attendance Batch</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
