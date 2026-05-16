import { useState } from "react";
import { LoginButton } from "./LoginButton";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="w-full py-3 px-4 sm:px-6 flex items-center relative bg-gray-50/80 backdrop-blur border-b border-gray-200/60">
      <a href="/" className="me-auto flex items-center">
        <img src="/image.png" className="h-11 sm:h-12" alt="Logo" />
      </a>

      <div className="hidden sm:flex gap-7 px-3 font-medium outfit-regular text-lg text-gray-700">
        <a href="/playground" className="hover:text-black transition-colors">Playground</a>
        <a href="/profile" className="hover:text-black transition-colors">Profile</a>
      </div>

      <div className="ms-3">
        <LoginButton />
      </div>
      <button
        className="sm:hidden px-2 text-2xl text-gray-700 hover:text-black transition-colors"
        onClick={() => setMenuOpen(prev => !prev)}
        aria-label="Toggle menu"
      >
        ☰
      </button>

      {menuOpen && (
        <div className="absolute top-full left-0 w-full bg-gray-50/95 backdrop-blur sm:hidden shadow-md rounded-b-2xl border-b border-gray-200/70">
          <div className="flex flex-col gap-4 px-5 py-4 font-medium outfit-regular text-lg text-gray-700">
            <a href="/playground" onClick={() => setMenuOpen(false)} className="hover:text-black transition-colors">
              Playground
            </a>
            <a href="/profile" onClick={() => setMenuOpen(false)} className="hover:text-black transition-colors">
              Profile
            </a>
          </div>
        </div>
      )}
    </nav>
  );
}

export { Navbar };
