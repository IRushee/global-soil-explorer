import React from 'react'
import { Link } from 'react-router-dom'

export const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-slate-950 text-slate-100 font-sans gap-4">
      <h1 className="text-4xl font-extrabold text-teal-400">404</h1>
      <p className="text-slate-400">Page not found.</p>
      <Link to="/" className="px-4 py-2 bg-teal-650 hover:bg-teal-600 rounded text-sm transition-colors text-slate-100">
        Back to Explorer
      </Link>
    </div>
  )
}
