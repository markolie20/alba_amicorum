import { Search, Calendar, Filter } from 'lucide-react';

interface FilterBarProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  yearRange: [number, number];
  setYearRange: (range: [number, number]) => void;
  selectedCountry: string;
  setSelectedCountry: (country: string) => void;
  countries: string[];
}

export function FilterBar({
  searchTerm,
  setSearchTerm,
  yearRange,
  setYearRange,
  selectedCountry,
  setSelectedCountry,
  countries,
}: FilterBarProps) {
  const countryOptions = ['Alle', ...countries];

  return (
    <div className="bg-card border-b border-border shadow-sm">
      <div className="container mx-auto px-6 py-6">
        <div className="flex flex-col lg:flex-row gap-4 items-center">
          {/* Search */}
          <div className="flex-1 w-full lg:w-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="Zoek albums op naam, eigenaar of locatie..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-input-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ring transition-all"
              />
            </div>
          </div>

          {/* Year Range Filter */}
          <div className="flex items-center gap-3 bg-input-background border border-border rounded-lg px-4 py-3 w-full lg:w-auto">
            <Calendar className="w-5 h-5 text-muted-foreground flex-shrink-0" />
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1500"
                max="1900"
                value={yearRange[0]}
                onChange={(e) => setYearRange([parseInt(e.target.value), yearRange[1]])}
                className="w-20 bg-transparent border-b border-border focus:outline-none focus:border-ring"
              />
              <span className="text-muted-foreground">-</span>
              <input
                type="number"
                min="1500"
                max="1900"
                value={yearRange[1]}
                onChange={(e) => setYearRange([yearRange[0], parseInt(e.target.value)])}
                className="w-20 bg-transparent border-b border-border focus:outline-none focus:border-ring"
              />
            </div>
          </div>

          {/* Country Filter */}
          <div className="flex items-center gap-3 bg-input-background border border-border rounded-lg px-4 py-3 w-full lg:w-auto">
            <Filter className="w-5 h-5 text-muted-foreground flex-shrink-0" />
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="bg-transparent focus:outline-none focus:ring-0 cursor-pointer"
            >
              {countryOptions.map((country) => (
                <option key={country} value={country}>
                  {country}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
