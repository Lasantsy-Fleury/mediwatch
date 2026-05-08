import { CalendarDays, LogOut, UserCircle2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthProvider'

const Header = (): JSX.Element => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const formattedDate = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  const handleLogout = async (): Promise<void> => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-4 md:px-8">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Portail Praticien</p>
          <h2 className="text-lg font-semibold text-[color:#1e3a5f]">{user?.full_name ?? 'Praticien'}</h2>
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-600">
          <span className="hidden items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 sm:flex">
            <CalendarDays size={16} className="text-[color:#3b82f6]" />
            {formattedDate}
          </span>
          <button
            type="button"
            onClick={handleLogout}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <LogOut size={14} />
            Se déconnecter
          </button>
          <UserCircle2 size={30} className="text-[color:#1e3a5f]" />
        </div>
      </div>
    </header>
  )
}

export default Header
