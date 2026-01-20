import { useState } from "react";
import { LoginButton } from "./LoginButton";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="w-full py-3 px-3 flex items-center relative bg-gray-50">

      <a href="/" className="me-auto">
        <img src="/image.png" className="h-12" alt="Logo" />
      </a>

      <div className="hidden sm:flex gap-6 px-3 font-medium outfit-regular text-xl">
        <a href="/playground">Playground</a>
        <a href="/profile">Profile</a>
      </div>

      <div className="ms-3">
        <LoginButton />
      </div>
      <button
        className="sm:hidden px-2 text-2xl"
        onClick={() => setMenuOpen(prev => !prev)}
        aria-label="Toggle menu"
      >
        ☰
      </button>

      {menuOpen && (
        <div className="absolute top-full left-0 w-full bg-gray-50 sm:hidden">
          <div className="flex flex-col gap-4 px-4 py-2 font-medium outfit-regular text-lg">
            <a href="/playground" onClick={() => setMenuOpen(false)}>
              Playground
            </a>
            <a href="/profile" onClick={() => setMenuOpen(false)}>
              Profile
            </a>
          </div>
        </div>
      )}
    </nav>
  );
}

export { Navbar };
