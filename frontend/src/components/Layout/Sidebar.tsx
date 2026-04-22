import { FlaskConical, LayoutDashboard, Stethoscope, UserRound } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/consultation', label: 'Consultation', icon: Stethoscope },
  { to: '/patient/PT-1001', label: 'Patient', icon: UserRound },
  { to: '/simulation', label: 'Simulation', icon: FlaskConical },
]

const Sidebar = (): JSX.Element => {
  return (
    <>
      <aside className="fixed left-0 top-0 z-30 hidden h-screen w-64 border-r border-slate-200 bg-white md:block">
        <div className="flex h-full flex-col px-5 py-6">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">MediWatch</p>
            <h1 className="mt-1 text-2xl font-bold text-[color:#1e3a5f]">Assistant Clinique</h1>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition ${
                      isActive
                        ? 'bg-slate-100 text-[color:#1e3a5f] border border-slate-200'
                        : 'text-slate-600 hover:bg-slate-50 hover:text-[color:#1e3a5f]'
                    }`
                  }
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>
        </div>
      </aside>

      <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-slate-200 bg-white md:hidden">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex flex-1 flex-col items-center justify-center gap-1 py-2 text-[11px] font-medium ${
                  isActive ? 'text-[color:#1e3a5f]' : 'text-slate-500'
                }`
              }
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>
    </>
  )
}

export default Sidebar
