import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "../components/firebase";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(
        err.code === "auth/user-not-found"
          ? "No user found with this email."
          : err.code === "auth/wrong-password"
          ? "Incorrect password."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
    setError("");
    setLoading(true);
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      navigate("/dashboard");
    } catch (err) {
      setError("Google sign-in failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-200 via-white to-purple-100">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 border border-blue-100">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-[#2f3f7d] p-3 rounded-full mb-2">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[#2f3f7d]">Smart Help Desk</h1>
          <div className="text-gray-500 mt-1 text-sm">Sign in to your account</div>
        </div>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-gray-700 font-medium mb-1">Email</label>
            <input
              className="w-full border border-blue-200 rounded px-3 py-2 focus:ring-2 focus:ring-blue-400"
              type="email"
              autoFocus
              required
              autoComplete="username"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="block text-gray-700 font-medium mb-1">Password</label>
            <input
              className="w-full border border-blue-200 rounded px-3 py-2 focus:ring-2 focus:ring-blue-400"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          {error && <div className="text-red-600 text-sm">{error}</div>}
          <button
            className="w-full bg-[#2f3f7d] hover:bg-[#4052a0] text-white font-semibold py-2 rounded transition"
            type="submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <div className="my-4 flex items-center">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="mx-4 text-xs text-gray-400">or</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>
        <button
          onClick={handleGoogleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-white border border-gray-200 text-gray-700 font-medium py-2 rounded shadow hover:bg-gray-50 transition"
        >
          <svg className="w-5 h-5" viewBox="0 0 48 48">
            <g>
              <path fill="#4285F4" d="M44.5 20H24v8.5h11.8C34.1 35 29.6 38 24 38a14 14 0 1 1 0-28c3.6 0 7 1.3 9.6 3.8l7.2-7.2C36.5 2.4 30.6 0 24 0 10.7 0 0 10.7 0 24s10.7 24 24 24c12.1 0 22-8.6 22-24 0-1.6-.2-3.2-.5-4.7z"/>
              <path fill="#34A853" d="M6.3 14.7l7 5.1c1.9-3.7 5.3-6.3 9.2-6.3 2.6 0 4.9.9 6.7 2.5l8-8C33.9 4.5 29.2 2 24 2c-7.9 0-14.6 5-17.7 12.2z"/>
              <path fill="#FBBC05" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7-5.7c-2 1.4-4.6 2.2-8.2 2.2-6.3 0-11.6-4.2-13.5-9.8l-7.2 5.6C6.8 43.1 14.8 48 24 48z"/>
              <path fill="#EA4335" d="M44.5 20H24v8.5h11.8C34.1 35 29.6 38 24 38c-4.4 0-8.4-1.5-11.4-4.1l-7.2 5.6C10.7 43.7 17 48 24 48c12.1 0 22-8.6 22-24 0-1.6-.2-3.2-.5-4.7z"/>
              <path fill="none" d="M0 0h48v48H0z"/>
            </g>
          </svg>
          {loading ? "Connecting..." : "Sign in with Google"}
        </button>
      </div>
    </div>
  );
}