import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactCrop, { centerCrop, makeAspectCrop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import DragDropUploader from './DragDropUploader';
import { 
  ArrowUpTrayIcon,
  DocumentTextIcon,
  AdjustmentsHorizontalIcon,
  ArrowPathIcon,
  XMarkIcon,
  PhotoIcon,
  ArrowDownTrayIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { Link, useNavigate } from 'react-router-dom';
import API_URL from '../config';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const slideIn = {
  initial: { x: -20, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  exit: { x: 20, opacity: 0 }
};

export default function WatermarkGenerator() {
  const [image, setImage] = useState(null);
  const [watermarkType, setWatermarkType] = useState('text');
  const [watermarkText, setWatermarkText] = useState('');
  const [fontSize, setFontSize] = useState(24);
  const [opacity, setOpacity] = useState(0.5);
  const [position, setPosition] = useState('center');
  const [pattern, setPattern] = useState('single');
  const [spacing, setSpacing] = useState(100);
  const [angle, setAngle] = useState(0);
  const [previewCanvas, setPreviewCanvas] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImage, setProcessedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []);

  const updatePreview = useCallback(() => {
    if (!image || !watermarkText) return;

    const img = new Image();
    img.src = image;
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;

      // Draw original image
      ctx.drawImage(img, 0, 0);

      // Add watermark text
      ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
      ctx.font = `${fontSize}px Arial`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      let x = canvas.width / 2;
      let y = canvas.height / 2;

      switch (position) {
        case 'top':
          y = fontSize * 2;
          break;
        case 'bottom':
          y = canvas.height - fontSize * 2;
          break;
        case 'left':
          x = fontSize * 2;
          ctx.textAlign = 'left';
          break;
        case 'right':
          x = canvas.width - fontSize * 2;
          ctx.textAlign = 'right';
          break;
      }

      ctx.fillText(watermarkText, x, y);
      setPreviewCanvas(canvas);
    };
  }, [image, watermarkText, fontSize, opacity, position]);

  useEffect(() => {
    updatePreview();
  }, [updatePreview]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
      setProcessedImage(null);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError('Please select an image');
      return;
    }

    if (!watermarkText) {
      setError('Please enter watermark text');
      return;
    }

    if (!isAuthenticated) {
      setError('Please sign in to add watermarks');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      const formData = new FormData();
      
      const response = await fetch(image);
      const blob = await response.blob();
      formData.append('image', blob, 'image.png');
      formData.append('text', watermarkText);
      formData.append('fontSize', fontSize.toString());
      formData.append('opacity', opacity.toString());
      formData.append('position', position);
      formData.append('pattern', pattern);
      formData.append('spacing', spacing.toString());
      formData.append('angle', angle.toString());

      const apiResponse = await fetch(`${API_URL}/api/watermark/add`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        credentials: 'include',
        body: formData
      });

      if (!apiResponse.ok) {
        const errorData = await apiResponse.json();
        throw new Error(errorData.error || 'Failed to add watermark');
      }

      const data = await apiResponse.json();
      if (data.image && data.image.url) {
        setProcessedImage(`${API_URL}${data.image.url}`);
        setSuccess(true);
        // Wait for 1.5 seconds to show success message then redirect
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        throw new Error('No processed image URL received');
      }
    } catch (error) {
      console.error('Error adding watermark:', error);
      setError(error.message || 'Failed to add watermark');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null);
    setWatermarkText('');
    setFontSize(24);
    setOpacity(0.5);
    setPosition('center');
    setProcessedImage(null);
    setError('');
  };

  const handleDownload = () => {
    if (processedImage) {
      const link = document.createElement('a');
      link.href = processedImage;
      link.download = 'watermarked-image.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-white py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Add Watermark to Your Images
          </h1>
          <p className="text-lg text-gray-600">
            Protect your images with professional watermarks and patterns
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Image Upload and Settings */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <div className="space-y-6">
              {/* Image Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Image
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-500 transition-colors">
                  <div className="space-y-1 text-center">
                    {image ? (
                      <div className="relative">
                        <img
                          src={image}
                          alt="Preview"
                          className="max-h-64 mx-auto rounded-lg"
                        />
                        <button
                          onClick={handleReset}
                          className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                        >
                          <ArrowPathIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <div className="flex text-sm text-gray-600">
                          <label
                            htmlFor="file-upload"
                            className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                          >
                            <span>Upload a file</span>
                            <input
                              id="file-upload"
                              name="file-upload"
                              type="file"
                              accept="image/*"
                              className="sr-only"
                              onChange={handleFileSelect}
                            />
                          </label>
                          <p className="pl-1">or drag and drop</p>
                        </div>
                        <p className="text-xs text-gray-500">
                          PNG, JPG, GIF up to 10MB
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Watermark Settings */}
              <div className="space-y-4">
                <div>
                  <label htmlFor="watermarkType" className="block text-sm font-medium text-gray-700">
                    Watermark Type
                  </label>
                  <select
                    id="watermarkType"
                    value={pattern}
                    onChange={(e) => setPattern(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md"
                  >
                    <option value="single">Single Text</option>
                    <option value="repeat">Repeated Pattern</option>
                    <option value="diagonal">Diagonal Pattern</option>
                    <option value="grid">Grid Pattern</option>
                    <option value="radial">Radial Pattern</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="watermarkText" className="block text-sm font-medium text-gray-700">
                    Watermark Text
                  </label>
                  <input
                    type="text"
                    id="watermarkText"
                    value={watermarkText}
                    onChange={(e) => setWatermarkText(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Enter your watermark text"
                  />
                </div>

                <div>
                  <label htmlFor="fontSize" className="block text-sm font-medium text-gray-700">
                    Font Size
                  </label>
                  <input
                    type="range"
                    id="fontSize"
                    min="12"
                    max="72"
                    value={fontSize}
                    onChange={(e) => setFontSize(parseInt(e.target.value))}
                    className="mt-1 block w-full"
                  />
                  <div className="text-sm text-gray-500 mt-1">{fontSize}px</div>
                </div>

                <div>
                  <label htmlFor="opacity" className="block text-sm font-medium text-gray-700">
                    Opacity
                  </label>
                  <input
                    type="range"
                    id="opacity"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={opacity}
                    onChange={(e) => setOpacity(parseFloat(e.target.value))}
                    className="mt-1 block w-full"
                  />
                  <div className="text-sm text-gray-500 mt-1">{Math.round(opacity * 100)}%</div>
                </div>

                {pattern !== 'single' && (
                  <>
                    <div>
                      <label htmlFor="spacing" className="block text-sm font-medium text-gray-700">
                        Pattern Spacing
                      </label>
                      <input
                        type="range"
                        id="spacing"
                        min="50"
                        max="300"
                        value={spacing}
                        onChange={(e) => setSpacing(parseInt(e.target.value))}
                        className="mt-1 block w-full"
                      />
                      <div className="text-sm text-gray-500 mt-1">{spacing}px</div>
                    </div>

                    <div>
                      <label htmlFor="angle" className="block text-sm font-medium text-gray-700">
                        Pattern Angle
                      </label>
                      <input
                        type="range"
                        id="angle"
                        min="0"
                        max="360"
                        value={angle}
                        onChange={(e) => setAngle(parseInt(e.target.value))}
                        className="mt-1 block w-full"
                      />
                      <div className="text-sm text-gray-500 mt-1">{angle}°</div>
                    </div>
                  </>
                )}

                {pattern === 'single' && (
                  <div>
                    <label htmlFor="position" className="block text-sm font-medium text-gray-700">
                      Position
                    </label>
                    <select
                      id="position"
                      value={position}
                      onChange={(e) => setPosition(e.target.value)}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md"
                    >
                      <option value="center">Center</option>
                      <option value="top">Top</option>
                      <option value="bottom">Bottom</option>
                      <option value="left">Left</option>
                      <option value="right">Right</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleSubmit}
                  disabled={isLoading || !image || !watermarkText}
                  className="flex-1 flex justify-center items-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    'Add Watermark'
                  )}
                </button>
              </div>
            </div>
          </motion.div>

          {/* Right Column: Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">Preview</h2>
            <div className="aspect-w-16 aspect-h-9 bg-gray-100 rounded-lg overflow-hidden">
              <AnimatePresence>
                {image && watermarkText ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="relative w-full h-full"
                  >
                    <canvas
                      ref={canvasRef}
                      className="w-full h-full object-contain"
                      style={{ display: 'none' }}
                    />
                    {previewCanvas && (
                      <img
                        src={previewCanvas.toDataURL()}
                        alt="Preview"
                        className="w-full h-full object-contain"
                      />
                    )}
                  </motion.div>
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    <DocumentTextIcon className="h-12 w-12" />
                    <span className="ml-2">Preview will appear here</span>
                  </div>
                )}
              </AnimatePresence>
            </div>

            {processedImage && (
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500"
                >
                  <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                  Download
                </button>
              </div>
            )}
          </motion.div>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 bg-red-50 text-red-700 p-4 rounded-lg text-sm text-center"
          >
            {error}
          </motion.div>
        )}

        {success && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 bg-green-50 text-green-700 p-4 rounded-lg text-sm text-center"
          >
            Watermark added successfully! Redirecting to dashboard...
          </motion.div>
        )}
      </div>
    </div>
  );
} 