import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  PhotoIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  PlusIcon,
  EyeIcon,
  SparklesIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import API_URL from '../config';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export default function Dashboard() {
  const [images, setImages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const fetchImages = useCallback(async (showLoading = true) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No authentication token found');
        navigate('/signin');
        return;
      }

      if (showLoading) {
        setIsLoading(true);
      }

      console.log('Fetching images...');
      const response = await fetch(`${API_URL}/api/images`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        mode: 'cors'
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 422) {
          localStorage.removeItem('access_token');
          navigate('/signin');
          throw new Error('Authentication failed');
        }
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch images');
      }

      const data = await response.json();
      console.log('Received images:', data);
      
      if (!data.images) {
        throw new Error('No images data received from server');
      }
      
      setImages(data.images);
      setError(null);
    } catch (err) {
      console.error('Error fetching images:', err);
      setError(err.message);
    } finally {
      if (showLoading) {
        setIsLoading(false);
      }
    }
  }, [navigate]);

  // Initial fetch and polling setup
  useEffect(() => {
    console.log('Setting up dashboard polling...');
    fetchImages(); // Initial fetch

    const intervalId = setInterval(() => {
      console.log('Polling for new images...');
      fetchImages(false);
    }, 15000);

    return () => {
      console.log('Cleaning up dashboard polling...');
      clearInterval(intervalId);
    };
  }, [fetchImages]);

  // Fetch on location change
  useEffect(() => {
    console.log('Location changed, fetching images...');
    fetchImages();
  }, [location, fetchImages]);

  const handleDelete = async (imageId) => {
    if (!confirm('Are you sure you want to delete this image?')) return;
    
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No authentication token found');
        navigate('/signin');
        return;
      }

      const response = await fetch(`${API_URL}/api/images/${imageId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        mode: 'cors'
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 422) {
          localStorage.removeItem('access_token');
          navigate('/signin');
          throw new Error('Authentication failed');
        }
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete image');
      }

      setImages(images.filter(img => img.id !== imageId));
      fetchImages(false);
    } catch (err) {
      console.error('Error deleting image:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (imageUrl, filename) => {
    const link = document.createElement('a');
    link.href = `${API_URL}${imageUrl}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleView = (image) => {
    setSelectedImage(image);
  };

  const handleRemoveWatermark = (image) => {
    // Convert the image URL to a Blob and create an object URL
    fetch(`${API_URL}${image.url}`)
      .then(response => response.blob())
      .then(blob => {
        const imageUrl = URL.createObjectURL(blob);
        navigate('/remover', { 
          state: { 
            imageUrl: imageUrl,
            originalImage: {
              id: image.id,
              filename: image.original_filename,
              watermarkText: image.watermark_text,
              url: image.url,
              stored_filename: image.stored_filename
            }
          } 
        });
      })
      .catch(error => {
        console.error('Error preparing image for removal:', error);
        setError('Failed to prepare image for watermark removal');
      });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <Link
            to="/signin"
            className="text-indigo-600 hover:text-indigo-500 font-medium"
          >
            Sign in to view your images
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <motion.h1 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-3xl font-bold text-gray-900"
        >
          Your Watermarked Images
        </motion.h1>
        <Link
          to="/generator"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Create New
        </Link>
      </div>

      {images.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No images</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new watermarked image.
          </p>
          <div className="mt-6">
            <Link
              to="/generator"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Create New Image
            </Link>
          </div>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {images.map((image, index) => (
              <motion.div
                key={image.id}
                variants={fadeInUp}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg overflow-hidden"
              >
                <div className="relative aspect-w-16 aspect-h-9">
                  <img
                    src={`${API_URL}${image.url}`}
                    alt={image.original_filename}
                    className="object-cover w-full h-full"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-opacity duration-200 flex items-center justify-center">
                    <div className="opacity-0 hover:opacity-100 transition-opacity duration-200 flex gap-2">
                      <button
                        onClick={() => handleView(image)}
                        className="p-2 bg-white rounded-full text-gray-900 hover:bg-gray-100"
                        title="View Image"
                      >
                        <EyeIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDownload(image.url, image.original_filename)}
                        className="p-2 bg-white rounded-full text-gray-900 hover:bg-gray-100"
                        title="Download Image"
                      >
                        <ArrowDownTrayIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleRemoveWatermark(image)}
                        className="p-2 bg-white rounded-full text-gray-900 hover:bg-gray-100"
                        title="Remove Watermark"
                      >
                        <SparklesIcon className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(image.id)}
                        className="p-2 bg-white rounded-full text-red-600 hover:bg-gray-100"
                        title="Delete Image"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {image.original_filename}
                  </h3>
                  {image.watermark_text && (
                    <p className="mt-1 text-sm text-gray-500">
                      Watermark: {image.watermark_text}
                    </p>
                  )}
                  <p className="mt-1 text-xs text-gray-400">
                    {new Date(image.created_at).toLocaleDateString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Image Preview Modal */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.95 }}
              className="relative max-w-4xl w-full bg-white rounded-xl overflow-hidden"
              onClick={e => e.stopPropagation()}
            >
              <img
                src={`${API_URL}${selectedImage.url}`}
                alt={selectedImage.original_filename}
                className="w-full h-auto"
              />
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute top-4 right-4 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100"
              >
                <XMarkIcon className="h-6 w-6 text-gray-600" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 