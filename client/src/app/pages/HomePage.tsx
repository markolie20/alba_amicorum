import { useState, useMemo, useEffect } from 'react';
import { Header } from '../components/Header';
import { HeroSection } from '../components/HeroSection';
import { FilterBar } from '../components/FilterBar';
import { AlbaMap } from '../components/AlbaMap';
import { AlbaList } from '../components/AlbaList';
import { fetchAlbums, fetchAlbumDetail, fetchCountries } from '../api';
import { Album } from '../types';

export default function HomePage() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [albumsLoading, setAlbumsLoading] = useState(true);
  const [albumsError, setAlbumsError] = useState<string | null>(null);

  useEffect(() => {
    fetchAlbums()
      .then((data) => { setAlbums(data); setAlbumsLoading(false); })
      .catch(() => { setAlbumsError('Kon albums niet laden.'); setAlbumsLoading(false); });
  }, []);

  const [searchTerm, setSearchTerm] = useState('');
  const [yearRange, setYearRange] = useState<[number, number]>([1550, 1900]);
  const [selectedCountry, setSelectedCountry] = useState('Alle');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedAlbumId, setSelectedAlbumId] = useState<string | null>(null);
  const itemsPerPage = 8;

  // Countries come from the API so they match the real data, not the mock
  const [availableCountries, setAvailableCountries] = useState<string[]>([]);
  useEffect(() => {
    fetchCountries()
      .then(setAvailableCountries)
      .catch(() => {
        // Fallback: derive from whatever albums are loaded
        const countries = [...new Set(albums.map((a) => a.country).filter((c) => c !== 'Unknown'))].sort();
        setAvailableCountries(countries);
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch full album detail (with contributions) when an album is selected
  const [selectedAlbumDetail, setSelectedAlbumDetail] = useState<Album | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedAlbumId) {
      setSelectedAlbumDetail(null);
      setDetailError(null);
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    fetchAlbumDetail(selectedAlbumId)
      .then((data) => {
        setSelectedAlbumDetail(data);
        setDetailLoading(false);
      })
      .catch(() => {
        setDetailError('Kon albumdetails niet laden.');
        setDetailLoading(false);
      });
  }, [selectedAlbumId]);

  const filteredAlbums = useMemo(() => {
    return albums.filter((album) => {
      const matchesSearch =
        searchTerm === '' ||
        album.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        album.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
        album.location.name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesYear = album.year >= yearRange[0] && album.year <= yearRange[1];

      const matchesCountry = selectedCountry === 'Alle' || album.country === selectedCountry;

      return matchesSearch && matchesYear && matchesCountry;
    });
  }, [albums, searchTerm, yearRange, selectedCountry]);

  // Reset to page 1 when filters change
  useMemo(() => {
    setCurrentPage(1);
  }, [searchTerm, yearRange, selectedCountry]);

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Header />
      <HeroSection />

      <div className="flex-1 flex flex-col min-h-0">
        <FilterBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          yearRange={yearRange}
          setYearRange={setYearRange}
          selectedCountry={selectedCountry}
          setSelectedCountry={setSelectedCountry}
          countries={availableCountries}
        />

        <div className="flex-1 container mx-auto px-6 py-6 min-h-0">
          <div className="flex gap-6 h-full">
            <div className="flex-[1.75] min-w-0">
              {detailError && (
                <div className="mb-2 px-4 py-2 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive">
                  {detailError}
                </div>
              )}
              <AlbaMap
                albums={filteredAlbums}
                selectedAlbumId={selectedAlbumId}
                selectedAlbumDetail={selectedAlbumDetail}
                detailLoading={detailLoading}
              />
            </div>

            <div className="flex-1 min-w-0 flex flex-col">
              {albumsError && (
                <div className="mb-2 px-4 py-2 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive">
                  {albumsError}
                </div>
              )}
              {albumsLoading ? (
                <div className="flex-1 flex items-center justify-center bg-card border border-border rounded-lg text-sm text-muted-foreground">
                  Albums laden…
                </div>
              ) : (
                <AlbaList
                  albums={filteredAlbums}
                  currentPage={currentPage}
                  setCurrentPage={setCurrentPage}
                  itemsPerPage={itemsPerPage}
                  selectedAlbumId={selectedAlbumId}
                  setSelectedAlbumId={setSelectedAlbumId}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
