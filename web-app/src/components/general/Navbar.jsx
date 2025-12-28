import { LoginButton } from "./LoginButton";

function Navbar() {
  return (
    <nav className="w-full py-3 px-3 flex items-center">
      <img src="/image.png" className="h-14 me-auto"></img>
      <div className="gap-6 px-3 hidden sm:flex font-medium outfit-regular text-xl">
        <a href="/playground">Playground</a>
      </div>
      <LoginButton/>  
    </nav>
  );
}

export { Navbar };
