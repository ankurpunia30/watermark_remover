import { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bars3Icon,
  XMarkIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  HomeIcon,
  PhotoIcon,
  DocumentDuplicateIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import API_URL from '../config';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      console.log('Token being sent:', token); // Debug token

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          credentials: 'include'
        });

        if (response.ok) {
          const userData = await response.json();
          console.log('User data received:', userData); // Debug user data
          setUser(userData);
        } else if (response.status === 422 || response.status === 401) {
          // Token is invalid or expired
          console.log('Token validation failed, clearing token');
          localStorage.removeItem('access_token');
          setUser(null);
        } else {
          console.log('Other error:', response.status);
          localStorage.removeItem('access_token');
        }
      } catch (error) {
        console.error('Error fetching user:', error);
        localStorage.removeItem('access_token');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, [location.pathname]);

  const handleSignOut = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    navigate('/');
  };

  const NavLink = ({ to, children, className = '' }) => {
    const isActive = location.pathname === to;
    return (
      <Link
        to={to}
        className={`${className} ${
          isActive
            ? 'text-indigo-600 font-semibold'
            : 'text-gray-600 hover:text-indigo-600'
        }`}
      >
        {children}
      </Link>
    );
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                WatermarkPro
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-8">
            {!isLoading && (
              <>
                {user ? (
                  <>
                    <NavLink to="/dashboard" className="flex items-center gap-2">
                      <HomeIcon className="h-5 w-5" />
                      Dashboard
                    </NavLink>
                    <NavLink to="/generator" className="flex items-center gap-2">
                      <PhotoIcon className="h-5 w-5" />
                      Add Watermark
                    </NavLink>
                    <NavLink to="/remover" className="flex items-center gap-2">
                      <DocumentDuplicateIcon className="h-5 w-5" />
                      Remove Watermark
                    </NavLink>
                    <div className="relative">
                      <button
                        onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                        className="flex items-center gap-2 text-gray-600 hover:text-indigo-600 transition-colors"
                      >
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center text-white font-semibold">
                          {user?.email ? user.email[0].toUpperCase() : '?'}
                        </div>
                        <span>{user?.email}</span>
                        <ChevronDownIcon className="h-4 w-4" />
                      </button>

                      <AnimatePresence>
                        {isUserMenuOpen && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-50"
                          >
                            <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                              Signed in as<br />
                              <span className="font-medium">{user?.email}</span>
                            </div>
                            <button
                              onClick={handleSignOut}
                              className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                            >
                              <ArrowRightOnRectangleIcon className="h-5 w-5" />
                              Sign Out
                            </button>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </>
                ) : (
                  <>
                    <NavLink to="/signin" className="flex items-center gap-2">
                      <UserIcon className="h-5 w-5" />
                      Sign In
                    </NavLink>
                    <NavLink
                      to="/signup"
                      className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-indigo-500 hover:to-purple-500 transition-all"
                    >
                      Sign Up
                    </NavLink>
                  </>
                )}
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            >
              <span className="sr-only">Open main menu</span>
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="sm:hidden"
          >
            <div className="pt-2 pb-3 space-y-1">
              {!isLoading && (
                <>
                  {user ? (
                    <>
                      <NavLink
                        to="/dashboard"
                        className="block pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-indigo-500"
                      >
                        Dashboard
                      </NavLink>
                      <NavLink
                        to="/generator"
                        className="block pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-indigo-500"
                      >
                        Add Watermark
                      </NavLink>
                      <NavLink
                        to="/remover"
                        className="block pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-indigo-500"
                      >
                        Remove Watermark
                      </NavLink>
                      <div className="pt-4 pb-3 border-t border-gray-200">
                        <div className="flex items-center px-4">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center justify-center text-white font-semibold">
                              {user?.email ? user.email[0].toUpperCase() : '?'}
                            </div>
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-700">{user?.email}</div>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={handleSignOut}
                        className="block w-full text-left pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-red-500 text-gray-600 hover:text-red-600"
                      >
                        Sign Out
                      </button>
                    </>
                  ) : (
                    <>
                      <NavLink
                        to="/signin"
                        className="block pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-indigo-500"
                      >
                        Sign In
                      </NavLink>
                      <NavLink
                        to="/signup"
                        className="block pl-3 pr-4 py-2 border-l-4 border-transparent hover:border-indigo-500"
                      >
                        Sign Up
                      </NavLink>
                    </>
                  )}
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
} 