import { useState } from 'react'
import StudentStatus from './components/StudentStatus.jsx'

export default function App() {
  const [studentId, setStudentId] = useState('STU001')
  const [submittedId, setSubmittedId] = useState('STU001')

  function handleLookup(e) {
    e.preventDefault()
    setSubmittedId(studentId.trim())
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-sm">
          Z
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Zenkai</h1>
          <p className="text-xs text-gray-500">Self-healing ERP Recovery — Student Dashboard</p>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-3xl mx-auto px-4 py-10 space-y-6">
        {/* Lookup form */}
        <form onSubmit={handleLookup} className="flex gap-3">
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="Student ID (e.g. STU001)"
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
          />
          <button
            type="submit"
            className="rounded-lg bg-green-500 px-5 py-2 text-sm font-medium text-white hover:bg-green-600 transition-colors"
          >
            Look up
          </button>
        </form>

        {/* Status panel */}
        <StudentStatus studentId={submittedId} />
      </main>
    </div>
  )
}
