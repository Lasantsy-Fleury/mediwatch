import { Menu } from 'lucide-react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'
import Consultation from './pages/Consultation'
import Dashboard from './pages/Dashboard'
import Patient from './pages/Patient'
import Simulation from './pages/Simulation'

const App = (): JSX.Element => {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Sidebar />

        <main className="md:ml-64">
          <Header />
          <div className="mx-auto max-w-[1400px] px-4 py-6 pb-24 md:px-8 md:py-8 md:pb-8">
            <div className="mb-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-600 md:hidden">
              <Menu size={14} /> Navigation disponible sur ecran large
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
    </BrowserRouter>
  )
}

export default App
