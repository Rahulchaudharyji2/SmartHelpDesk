import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import TicketPage from "./pages/TicketPage";

// PrivateRoute ensures only logged-in users can access dashboard
function PrivateRoute({ children }) {
  const { user } = useAuth();
  if (user === undefined) return null; // or loading spinner
  return user ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/tickets"
            element={
              <PrivateRoute>
                  <TicketPage />
              </PrivateRoute>
            }
          />
          <Route path="/*" element={<Home />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
