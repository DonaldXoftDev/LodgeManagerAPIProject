import { LoginForm } from "../components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-linear-to-br from-indigo-100 via-white to-rose-100 flex flex-col items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-black text-indigo-900 tracking-tight mb-2">
            LodgeManager
          </h1>
          <p className="text-indigo-600 text-sm font-medium">
            Sign in to manage your properties
          </p>
        </div>

        <div className="bg-white/90 backdrop-blur-xl rounded-2xl border border-white/20 shadow-xl p-8 space-y-6">
          <LoginForm />

          <div className="text-center text-sm">
            <span className="text-indigo-700/70">Don't have an account? </span>
            <a
              href="/register"
              className="text-indigo-700 font-semibold hover:text-indigo-600 transition-colors"
            >
              Create one
            </a>
          </div>
        </div>

        <div className="mt-8 text-center text-xs text-indigo-600/60">
          <p>Demo credentials available on request</p>
        </div>
      </div>
    </div>
  );
}
