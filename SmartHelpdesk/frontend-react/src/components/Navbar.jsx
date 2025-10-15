import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import Chatbot from "../components/Chatbot";
import TicketForm from "../components/TicketForm";

export default function Navbar() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [ticketOpen, setTicketOpen] = useState(false);
  const dropdownRef = useRef();
  const ticketRef = useRef();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const username = user?.email ? user.email.split("@")[0] : "Guest";
  const displayName = user?.displayName || username;
  const email = user?.email || "";

  // Close dropdowns if clicked outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
      if (ticketRef.current && !ticketRef.current.contains(e.target)) {
        setTicketOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav className="sticky top-0 z-30 bg-gradient-to-r from-[#023e8a] via-[#03045e] to-[#03045e] shadow text-white">
      <div className="max-w-6xl mx-auto flex flex-wrap md:flex-nowrap items-center justify-between px-4 py-4 gap-2 md:gap-0">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-xl md:text-2xl font-bold tracking-tight">
            Smart Help Desk
          </span>
        </Link>

        <div className="flex flex-wrap md:flex-nowrap gap-2 md:gap-4 items-center">
          <NavLink to="/" active={pathname === "/"}>
            Home
          </NavLink>
          <NavLink to="/dashboard" active={pathname === "/dashboard"}>
            Dashboard
          </NavLink>
          {user && (
            <NavLink to="/ticket" active={pathname === "/ticket"}>
              Tickets
            </NavLink>
          )}

          {user ? (
            <div className="relative ml-0 md:ml-4" ref={dropdownRef}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex flex-col items-end text-right focus:outline-none"
              >
                <div className="font-medium truncate max-w-[100px]">
                  {username}
                </div>
                <div className="text-xs text-white/70 truncate max-w-[100px]">
                  {displayName}
                </div>
                <div className="text-xs text-white/50 truncate max-w-[100px]">
                  {email}
                </div>
              </button>
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg text-gray-900 border border-gray-200 overflow-hidden z-50">
                  <div className="px-4 py-3 border-b border-gray-200">
                    <div className="font-medium">{username}</div>
                    <div className="text-sm text-gray-600">{displayName}</div>
                    <div className="text-sm text-gray-500">{email}</div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={() => navigate("/login")}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-white font-medium transition"
            >
              Login
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

function NavLink({ to, active, children }) {
  return (
    <Link
      to={to}
      className={`px-3 py-1 rounded-lg font-medium transition ${
        active
          ? "bg-white/20 shadow text-white"
          : "hover:bg-white/10 hover:text-gray-100"
      }`}
    >
      {children}
    </Link>
  );
}
