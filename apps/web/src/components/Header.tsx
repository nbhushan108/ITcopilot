function Header(): JSX.Element {
  return (
    <header className="bg-primary-700 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center font-bold text-lg">
            IT
          </div>
          <div>
            <h1 className="text-xl font-bold">ITcopilot</h1>
            <p className="text-xs text-primary-100">Income Tax Copilot for India</p>
          </div>
        </div>
        <nav className="flex gap-6 text-sm">
          <a href="/" className="hover:text-primary-100 transition-colors">
            Dashboard
          </a>
          <a href="/docs" className="hover:text-primary-100 transition-colors">
            API Docs
          </a>
        </nav>
      </div>
    </header>
  );
}

export default Header;
