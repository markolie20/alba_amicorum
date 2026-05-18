export function Header() {
  return (
    <header className="bg-primary border-b border-primary/30">
      <div className="container mx-auto px-6 py-4">
        <button
          onClick={() => window.location.href = '/'}
          className="hover:opacity-90 transition-opacity"
        >
          <h1 className="text-2xl text-white tracking-wide">
            De Koninklijke Bibliotheek
          </h1>
        </button>
      </div>
    </header>
  );
}
