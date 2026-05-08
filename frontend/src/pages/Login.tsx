import { Building2, Loader2, LogIn, Mail, UserPlus } from 'lucide-react'
import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import type { SocialProvider } from '../types'

const Login = (): JSX.Element => {
  const { login, register, socialLogin, isAuthenticated, isLoading } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState<string>('dr_martin')
  const [password, setPassword] = useState<string>('mediwatch2024')
  const [email, setEmail] = useState<string>('')
  const [fullName, setFullName] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')
  const [submitting, setSubmitting] = useState<boolean>(false)
  const [socialSubmitting, setSocialSubmitting] = useState<SocialProvider | null>(null)
  const navigate = useNavigate()
  const location = useLocation()

  const redirectPath = (location.state as { from?: string } | null)?.from ?? '/dashboard'

  if (!isLoading && isAuthenticated) {
    return <Navigate to={redirectPath} replace />
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setSubmitting(true)
    try {
      if (mode === 'login') {
        await login({ username, password })
      } else {
        await register({ username, email, full_name: fullName, password })
      }
      if (mode === 'register') {
        setSuccess('Votre compte a été créé avec succès. Bienvenue au sein de l\'écosystème MediWatch.')
      }
      navigate(redirectPath, { replace: true })
    } catch {
      setError(
        mode === 'login'
          ? 'Identifiants invalides ou service temporairement indisponible.'
          : 'L\'inscription a échoué. Veuillez vérifier vos informations ou contacter le support technique.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  const handleSocialLogin = async (provider: SocialProvider): Promise<void> => {
    setError('')
    setSuccess('')
    setSocialSubmitting(provider)
    try {
      const fallbackFullName = fullName.trim() || 'Praticien MediWatch'
      const fallbackEmail = email.trim() || `${provider}.user@mediwatch.app`
      await socialLogin({ provider, email: fallbackEmail, full_name: fallbackFullName })
      navigate(redirectPath, { replace: true })
    } catch {
      setError('L\'authentification via tiers est actuellement indisponible. Veuillez utiliser vos identifiants directs.')
    } finally {
      setSocialSubmitting(null)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <section className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Plateforme MediWatch</p>
        <h1 className="mt-2 text-2xl font-bold text-[color:#1e3a5f]">
          {mode === 'login' ? 'Espace Praticien Sécurisé' : 'Rejoindre MediWatch'}
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          {mode === 'login'
            ? 'Accédez à vos outils d\'aide à la décision clinique et gérez vos dossiers patients en toute confidentialité.'
            : 'Créez votre compte professionnel pour bénéficier de nos solutions d\'assistance clinique assistée.'}
        </p>

        <div className="mt-5 grid grid-cols-2 gap-2 rounded-lg bg-slate-100 p-1 text-sm">
          <button
            type="button"
            onClick={() => {
              setMode('login')
              setError('')
              setSuccess('')
            }}
            className={`rounded-md px-3 py-2 font-semibold transition ${
              mode === 'login' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Connexion
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('register')
              setError('')
              setSuccess('')
            }}
            className={`rounded-md px-3 py-2 font-semibold transition ${
              mode === 'register' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Inscription
          </button>
        </div>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {mode === 'register' ? (
            <label className="block text-sm font-medium text-slate-700">
              Nom complet
              <input
                type="text"
                placeholder="Dr. Jean Dupont"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                autoComplete="name"
                required
              />
            </label>
          ) : null}

          <label className="block text-sm font-medium text-slate-700">
            Nom d'utilisateur
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              autoComplete="username"
              required
            />
          </label>

          {mode === 'register' ? (
            <label className="block text-sm font-medium text-slate-700">
              Adresse e-mail professionnelle
              <input
                type="email"
                placeholder="nom@etablissement.fr"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                autoComplete="email"
                required
              />
            </label>
          ) : null}

          <label className="block text-sm font-medium text-slate-700">
            Mot de passe
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              autoComplete="current-password"
              required
            />
          </label>

          {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 border border-red-100">{error}</p> : null}
          {success ? <p className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-700 border border-emerald-100">{success}</p> : null}

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[color:#1e3a5f] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[color:#16304d] disabled:opacity-70"
          >
            {submitting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : mode === 'login' ? (
              <LogIn size={16} />
            ) : (
              <UserPlus size={16} />
            )}
            {mode === 'login' ? 'Accéder à mon espace' : 'Créer mon compte'}
          </button>

          <div className="relative pt-2">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase tracking-wider text-slate-500">
              <span className="bg-white px-2">Ou continuer avec</span>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => void handleSocialLogin('google')}
              disabled={socialSubmitting !== null}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              {socialSubmitting === 'google' ? <Loader2 size={15} className="animate-spin" /> : <Mail size={15} />}
              Google
            </button>
            <button
              type="button"
              onClick={() => void handleSocialLogin('microsoft')}
              disabled={socialSubmitting !== null}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              {socialSubmitting === 'microsoft' ? (
                <Loader2 size={15} className="animate-spin" />
              ) : (
                <Building2 size={15} />
              )}
              Microsoft
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default Login
