export default function Footer() {
  return (
    <footer className="bg-white border-t">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">About</h3>
            <p className="mt-4 text-base text-gray-500">
              Professional watermark tools for protecting and cleaning your images.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">Features</h3>
            <ul className="mt-4 space-y-4">
              <li>
                <a href="/generator" className="text-base text-gray-500 hover:text-gray-900">
                  Add Watermarks
                </a>
              </li>
              <li>
                <a href="/remover" className="text-base text-gray-500 hover:text-gray-900">
                  Remove Watermarks
                </a>
              </li>
              <li>
                <a href="/" className="text-base text-gray-500 hover:text-gray-900">
                  Home
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-400 tracking-wider uppercase">Connect</h3>
            <ul className="mt-4 space-y-4">
              <li>
                <a
                  href="https://github.com/yourusername/watermark-tool"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-base text-gray-500 hover:text-gray-900"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@watermarktool.com"
                  className="text-base text-gray-500 hover:text-gray-900"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-200 pt-8">
          <p className="text-base text-gray-400 text-center">
            &copy; {new Date().getFullYear()} Watermark Tool. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
} 