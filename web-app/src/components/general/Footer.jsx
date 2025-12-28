import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faLinkedin, faGithub } from '@fortawesome/free-brands-svg-icons';

function Footer() {
  return (
    <footer className="w-full bg-black text-white py-8 px-6">
      <div className="max-w-6xl mx-auto flex flex-col justify-between items-start gap-8">

        <div className="flex justify-center md:justify-start w-full md:w-auto mb-4 md:mb-0">
          <div className="h-12">
            <img src="/image.png" alt="Wearlytic Logo" className="h-full invert" />
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between w-full items-start gap-8">

        <div className="hidden md:flex flex-col gap-2 text-sm text-gray-400">
            <a href="" className="hover:text-white">Playground</a>
            <a href="" className="hover:text-white">Listings</a>
            <a href="" className="hover:text-white">Creators</a>
        </div>

        <div className="flex gap-4 md:gap-2 md:flex-col items-center ms-auto me-auto md:ms-0 md:me-0 md:items-start">
            <a href="mailto:vishnurchityala@gmail.com" className="text-gray-400 hover:text-white text-sm">
            <FontAwesomeIcon icon={faEnvelope} className="w-6 h-6 md:mr-2 md:text-sm" />
            <span className="hidden md:inline">Email</span>
            </a>
            <a href="https://www.linkedin.com/in/vishnuchityala" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white text-sm">
            <FontAwesomeIcon icon={faLinkedin} className="w-6 h-6 md:mr-2 md:text-sm" />
            <span className="hidden md:inline">LinkedIn</span>
            </a>
            <a href="https://github.com/vishnurchityala" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white text-sm">
            <FontAwesomeIcon icon={faGithub} className="w-6 h-6 md:mr-2 md:text-sm" />
            <span className="hidden md:inline">GitHub</span>
            </a>
        </div>

        </div>

      </div>

      <div className="text-xs text-gray-500 mt-10 text-center font-medium">
        &copy; {new Date().getFullYear()} Wearlytic. All rights reserved.
      </div>
    </footer>
  );
}

export { Footer };
