import { Menu } from 'lucide-react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './auth/ProtectedRoute'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'
import Consultation from './pages/Consultation'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Patient from './pages/Patient'
import Simulation from './pages/Simulation'

const AppShell = (): JSX.Element => {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />

      <main className="md:ml-64">
        <Header />
        <div className="mx-auto max-w-[1400px] px-4 py-6 pb-24 md:px-8 md:py-8 md:pb-8">
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 md:hidden">
            <Menu size={14} /> La navigation complète est disponible sur écran large
          </div>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/consultation" element={<Consultation />} />
            <Route path="/patient/:id" element={<Patient />} />
            <Route path="/simulation" element={<Simulation />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

const App = (): JSX.Element => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<ProtectedRoute />}>
          <Route path="*" element={<AppShell />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
