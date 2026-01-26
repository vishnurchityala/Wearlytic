import { faUser, faRightFromBracket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuth } from "../../auth/AuthProvider";

function LoginButton() {
  const { user, loginWithGoogle, logout, loading } = useAuth();

  const handleClick = () => {
    if (user) {
      logout();
    } else {
      loginWithGoogle();
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={loading}
      className="px-3.5 py-1.5 text-sm sm:text-base text-white bg-black rounded-lg outfit-regular font-medium flex items-center gap-2 cursor-pointer hover:bg-gray-900 transition-colors"
    >
      <FontAwesomeIcon icon={user ? faRightFromBracket : faUser} className="w-5 h-5" />
      {loading
        ? "Please wait..."
        : user
        ? "Logout"
        : "Login"}
    </button>
  );
}

export { LoginButton };
