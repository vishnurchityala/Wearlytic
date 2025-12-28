import { faUser } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

function LoginButton(){
    return (
    <button
        type="submit"
        className="px-4 py-2 text-base sm:text-lg text-white bg-black rounded-2xl outfit-regular font-medium"
      >
        <FontAwesomeIcon icon={faUser} className="w-7 h-7 md:mr-2" />Vishnu 
      </button>
    );
}

export {LoginButton}