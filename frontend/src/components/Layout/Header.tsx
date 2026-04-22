import { CalendarDays, UserCircle2 } from 'lucide-react'

const Header = (): JSX.Element => {
  const formattedDate = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex items-center justify-between px-4 py-4 md:px-8">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Espace medecin</p>
          <h2 className="text-lg font-semibold text-[color:#1e3a5f]">Dr Camille Moreau</h2>
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-600">
          <span className="hidden items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 sm:flex">
            <CalendarDays size={16} className="text-[color:#3b82f6]" />
            {formattedDate}
          </span>
          <UserCircle2 size={30} className="text-[color:#1e3a5f]" />
        </div>
      </div>
    </header>
  )
}

export default Header
