import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Layout.jsx
 *
 * - Sidebar stays visible always.
 * - When logged out: links are disabled (no navigation), main area shows only Login button.
 * - Logout button fixed at bottom.
 */

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const username = user?.email ? user.email.split("@")[0] : "Guest";
  const displayName = user?.displayName || username;
  const email = user?.email || "";
  const phone = user?.phoneNumber || "";

  // Logout handler
  const handleLogout = async () => {
    try {
      await logout();
      // after logout, navigate to / (or keep on same page). We still show Login button here.
      navigate("/"); // optional: you can change to '/login' if you prefer direct redirect
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  // WHEN USER IS LOGGED OUT -> show static sidebar + centered Login button
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex">
        {/* Sidebar always visible, but links disabled */}
        <aside
          className={`${sidebarOpen ? "w-64" : "w-20"} bg-[#2f3f7d] text-white transition-all duration-300 flex flex-col justify-between`}
        >
          <nav className="p-4 flex flex-col gap-2">
            {/* Disabled links: they look like links but do not navigate */}
            <SidebarItem disabled collapsed={!sidebarOpen} active={pathname === "/"}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              {sidebarOpen && <span>Home</span>}
            </SidebarItem>

            <SidebarItem disabled collapsed={!sidebarOpen} active={pathname === "/dashboard"}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {sidebarOpen && <span>Dashboard</span>}
            </SidebarItem>
          </nav>

          {/* Logout fixed at bottom (still visible even when logged out) */}
          <div className="p-4 border-t border-white/20">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2 rounded-lg w-full text-white/80 hover:bg-white/10 hover:text-white transition"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 11-4 0v-1" />
              </svg>
              {sidebarOpen && <span>Logout</span>}
            </button>
          </div>
        </aside>

        {/* Center: only Login button (no children or other page content) */}
        <div className="flex-1 flex items-center justify-center">
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-3 bg-blue-600 text-white text-lg rounded-lg shadow-lg hover:bg-blue-700"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  // USER IS LOGGED IN -> show normal dashboard with interactive links
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-[#2f3f7d] text-white border-b border-blue-700">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-white/80 hover:text-white">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <span className="text-xl font-semibold">Smart Help Desk</span>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-sm border-r border-blue-400 pr-6">
              <div className="text-white/70">Current UTC Time</div>
              <div className="font-mono text-lg">{new Date().toISOString().replace("T", " ").slice(0, 19)}</div>
            </div>
            <div>
              <div className="font-medium">{username}</div>
              <div className="text-xs text-white/70">{displayName}</div>
              <div className="text-xs text-white/50">{email}</div>
              {phone && <div className="text-xs text-white/50">{phone}</div>}
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar with active, clickable links */}
        <aside
          className={`${sidebarOpen ? "w-64" : "w-20"} bg-[#2f3f7d] text-white transition-all duration-300 flex flex-col justify-between`}
        >
          <nav className="p-4 flex flex-col gap-2">
            <SidebarItem to="/" active={pathname === "/"} collapsed={!sidebarOpen}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              {sidebarOpen && <span>Home</span>}
            </SidebarItem>

            <SidebarItem to="/dashboard" active={pathname === "/dashboard"} collapsed={!sidebarOpen}>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {sidebarOpen && <span>Dashboard</span>}
            </SidebarItem>
          </nav>

          {/* Logout fixed at bottom */}
          <div className="p-4 border-t border-white/20">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2 rounded-lg w-full text-white/80 hover:bg-white/10 hover:text-white transition"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 11-4 0v-1" />
              </svg>
              {sidebarOpen && <span>Logout</span>}
            </button>
          </div>
        </aside>

        {/* Dashboard content */}
        <main className="flex-1 p-6 bg-gray-50">{children}</main>
      </div>
    </div>
  );
}

/**
 * SidebarItem - supports:
 *  - `to` (string): link destination when not disabled
 *  - `disabled` (boolean): when true, renders a non-clickable item
 *  - `active`, `collapsed`
 */
function SidebarItem({ to, active, children, collapsed, disabled = false }) {
  const baseClass =
    `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${collapsed ? "justify-center" : ""}`;
  const activeClass = active ? "bg-white/10 text-white" : "text-white/60 hover:bg-white/5 hover:text-white";

  if (disabled) {
    // Render non-clickable visual
    return (
      <div className={`${baseClass} ${activeClass} opacity-60 cursor-not-allowed`} aria-disabled="true">
        {children}
      </div>
    );
  }

  // Render a real link
  return (
    <Link to={to} className={`${baseClass} ${activeClass}`}>
      {children}
    </Link>
  );
}
