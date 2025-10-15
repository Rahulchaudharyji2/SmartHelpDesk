import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center min-h-[80vh] gap-10 bg-gradient-to-b   text-600 py-12">
      {/* Hero Content */}
      <div className="text-center px-6 md:px-0">
        <h1 className="text-4xl md:text-6xl font-extrabold mb-4 drop-shadow-lg">
          Welcome to{" "}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-2xl shadow-lg">
            Smart Help Desk
          </span>
        </h1>
        <p className="text-lg md:text-2xl text-blue-600 mt-4 max-w-3xl mx-auto leading-relaxed">
          Your <span className="text-blue-300 font-semibold">AI-powered</span> helpdesk for IT support, password resets, and more.
          <br />
          Chat, create, and track support tickets effortlessly.
        </p>

        <Link
          to="/dashboard"
          className="inline-block mt-8 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-3 rounded-full font-semibold text-lg shadow-lg hover:scale-105 hover:brightness-110 transition-transform duration-300"
        >
          Go to Dashboard
        </Link>
      </div>

      {/* Image Card */}
      <div className="w-full max-w-4xl mx-auto mt-8 relative">
        <div className="rounded-3xl overflow-hidden shadow-2xl border-4 border-blue-700 hover:scale-105 transition-transform duration-300">
          <img
            src="https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=900&q=80"
            alt="Helpdesk illustration"
            className="w-full h-auto object-cover"
          />
        </div>

        {/* Optional overlay */}
        <div className="absolute inset-0 rounded-3xl bg-gradient-to-t from-[#03045e]/70 to-transparent"></div>
      </div>
    </section>
  );
}
