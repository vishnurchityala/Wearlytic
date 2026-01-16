import { LoginButton } from "./LoginButton";

function Navbar() {
  return (
    <nav className="w-full py-3 px-3 flex items-center">
      <a href="/" className="me-auto p-0"><img src="/image.png" className="h-12"></img></a>
      <div className="gap-6 px-3 hidden sm:flex font-medium outfit-regular text-xl">
        <a href="/playground">Playground</a>
      </div>
      <LoginButton/>  
    </nav>
  );
}

export { Navbar };
