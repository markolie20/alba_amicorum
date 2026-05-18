import { useState, useMemo } from 'react';
import { Header } from '../components/Header';
import { HeroSection } from '../components/HeroSection';
import { FilterBar } from '../components/FilterBar';
import { AlbaMap } from '../components/AlbaMap';
import { AlbaList } from '../components/AlbaList';
import { mockAlbums } from '../data/mockAlbums';

export default function HomePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [yearRange, setYearRange] = useState<[number, number]>([1500, 1900]);
  const [selectedCountry, setSelectedCountry] = useState('All');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAlbumId, setSelectedAlbumId] = useState<string | null>(null);
  const itemsPerPage = 8;

  // Filter albums based on search and filters
  const filteredAlbums = useMemo(() => {
    return mockAlbums.filter((album) => {
      const matchesSearch =
        searchTerm === '' ||
        album.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        album.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
        album.location.name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesYear = album.year >= yearRange[0] && album.year <= yearRange[1];

      const matchesCountry = selectedCountry === 'All' || album.country === selectedCountry;

      return matchesSearch && matchesYear && matchesCountry;
    });
  }, [searchTerm, yearRange, selectedCountry]);

  // Reset to page 1 when filters change
  useMemo(() => {
    setCurrentPage(1);
  }, [searchTerm, yearRange, selectedCountry]);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* 1. Top Title Bar */}
      <Header />

      {/* 2. Hero Section with Text and Image */}
      <HeroSection />

      {/* 3. Filter and Map/List Section */}
      <div className="flex-1 flex flex-col">
        {/* Filter Bar */}
        <FilterBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          yearRange={yearRange}
          setYearRange={setYearRange}
          selectedCountry={selectedCountry}
          setSelectedCountry={setSelectedCountry}
        />

        {/* Map and List Section */}
        <div className="flex-1 container mx-auto px-6 py-6">
          <div className="flex gap-6 h-[700px]">
            {/* Interactive Map (60-70% width) */}
            <div className="flex-[1.75] min-w-0">
              <AlbaMap albums={filteredAlbums} selectedAlbumId={selectedAlbumId} />
            </div>

            {/* List View (30-40% width) */}
            <div className="flex-1 min-w-0">
              <AlbaList
                albums={filteredAlbums}
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                itemsPerPage={itemsPerPage}
                selectedAlbumId={selectedAlbumId}
                setSelectedAlbumId={setSelectedAlbumId}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
