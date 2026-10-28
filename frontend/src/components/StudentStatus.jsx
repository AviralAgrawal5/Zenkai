import { useEffect, useState } from 'react'
import axios from 'axios'

const SEMESTER_ID = 'SEM-2026-A'

function Badge({ ok, label }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
        ok ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
      {label}
    </span>
  )
}

function Section({ title, children, loading, error }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm space-y-3">
      <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{title}</h2>
      {loading && <p className="text-sm text-gray-400 animate-pulse">Loading…</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}
      {!loading && !error && children}
    </div>
  )
}

export default function StudentStatus({ studentId }) {
  const [clearance, setClearance] = useState(null)
  const [clearanceErr, setClearanceErr] = useState(null)
  const [clearanceLoading, setClearanceLoading] = useState(false)

  const [enrollments, setEnrollments] = useState([])
  const [enrollErr, setEnrollErr] = useState(null)
  const [enrollLoading, setEnrollLoading] = useState(false)

  const [access, setAccess] = useState([])
  const [accessErr, setAccessErr] = useState(null)
  const [accessLoading, setAccessLoading] = useState(false)

  useEffect(() => {
    if (!studentId) return

    // Fee clearance
    setClearanceLoading(true)
    setClearanceErr(null)
    axios
      .get(`/api/finance/students/${studentId}/fee-clearance`, {
        params: { semester_id: SEMESTER_ID },
      })
      .then((r) => setClearance(r.data))
      .catch((e) =>
        setClearanceErr(e.response?.data?.detail ?? 'Could not reach Finance service'),
      )
      .finally(() => setClearanceLoading(false))

    // Enrollments
    setEnrollLoading(true)
    setEnrollErr(null)
    axios
      .get(`/api/registration/enrollments/${studentId}`)
      .then((r) => setEnrollments(r.data))
      .catch((e) =>
        setEnrollErr(e.response?.data?.detail ?? 'Could not reach Registration service'),
      )
      .finally(() => setEnrollLoading(false))

    // Course access
    setAccessLoading(true)
    setAccessErr(null)
    axios
      .get(`/api/learning/access/${studentId}`)
      .then((r) => setAccess(r.data))
      .catch((e) =>
        setAccessErr(e.response?.data?.detail ?? 'Could not reach Learning service'),
      )
      .finally(() => setAccessLoading(false))
  }, [studentId])

  return (
    <div className="space-y-4">
      {/* Fee Clearance */}
      <Section title="Fee Clearance" loading={clearanceLoading} error={clearanceErr}>
        {clearance && (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                Semester: <span className="font-medium">{clearance.semester_id}</span>
              </p>
              <p className="text-sm text-gray-600">
                Amount paid:{' '}
                <span className="font-medium">
                  ₹{clearance.amount_paid?.toLocaleString('en-IN')}
                </span>
              </p>
            </div>
            <Badge ok={clearance.cleared} label={clearance.cleared ? 'Cleared' : 'Pending'} />
          </div>
        )}
      </Section>

      {/* Enrollments */}
      <Section title="Semester Enrollments" loading={enrollLoading} error={enrollErr}>
        {enrollments.length === 0 ? (
          <p className="text-sm text-gray-400">No enrollment records found.</p>
        ) : (
          <ul className="space-y-2">
            {enrollments.map((e) => (
              <li key={e.id} className="flex items-center justify-between text-sm">
                <span className="text-gray-700">
                  {e.semester_id}{' '}
                  <span className="text-gray-400 text-xs">— {e.created_at?.slice(0, 10)}</span>
                </span>
                <Badge ok={e.status === 'enrolled'} label={e.status} />
              </li>
            ))}
          </ul>
        )}
      </Section>

      {/* Course Access */}
      <Section title="Course Access" loading={accessLoading} error={accessErr}>
        {access.length === 0 ? (
          <p className="text-sm text-gray-400">No course access provisioned.</p>
        ) : (
          <ul className="space-y-2">
            {access.map((c) => (
              <li key={c.id} className="flex items-center justify-between text-sm">
                <span className="text-gray-700">
                  <span className="font-mono font-medium">{c.course_code}</span>{' '}
                  {c.course_name && <span className="text-gray-500">— {c.course_name}</span>}
                </span>
                <Badge ok={c.status === 'active'} label={c.status} />
              </li>
            ))}
          </ul>
        )}
      </Section>
    </div>
  )
}
