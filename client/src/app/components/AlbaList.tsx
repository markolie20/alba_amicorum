import { Book, MapPin, Calendar, ChevronLeft, ChevronRight, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router';
import { Album } from '../types';

interface AlbaListProps {
  albums: Album[];
  currentPage: number;
  setCurrentPage: (page: number) => void;
  itemsPerPage: number;
  selectedAlbumId: string | null;
  setSelectedAlbumId: (id: string | null) => void;
}

export function AlbaList({ albums, currentPage, setCurrentPage, itemsPerPage, selectedAlbumId, setSelectedAlbumId }: AlbaListProps) {
  const navigate = useNavigate();
  const totalPages = Math.ceil(albums.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentAlbums = albums.slice(startIndex, endIndex);

  return (
    <div className="flex flex-col h-full bg-card border border-border rounded-lg shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-accent/30">
        <div className="flex items-center justify-between">
          <h3 className="text-foreground">Albums ({albums.length})</h3>
          <div className="flex items-center gap-3">
            {selectedAlbumId && (
              <button
                onClick={() => setSelectedAlbumId(null)}
                className="text-sm text-secondary hover:text-secondary/80 transition-colors"
              >
                Clear selection
              </button>
            )}
            <div className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </div>
          </div>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {currentAlbums.map((album) => (
          <div
            key={album.id}
            onClick={() => setSelectedAlbumId(selectedAlbumId === album.id ? null : album.id)}
            className={`flex items-center gap-4 p-4 border rounded-lg transition-all cursor-pointer group ${
              selectedAlbumId === album.id
                ? 'bg-secondary/20 border-secondary'
                : 'bg-background hover:bg-accent/50 border-border'
            }`}
          >
            {/* Icon */}
            <div className="flex-shrink-0 w-16 h-16 bg-gradient-to-br from-secondary/30 to-secondary/10 rounded-lg flex items-center justify-center border border-secondary/40 group-hover:scale-105 transition-transform">
              <Book className="w-8 h-8 text-secondary" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h4 className="text-foreground truncate mb-1">{album.title}</h4>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{album.location.name}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>{album.year}</span>
                  <span className="text-xs">•</span>
                  <span className="truncate">{album.owner}</span>
                </div>
              </div>
            </div>

            {/* Go to Album Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/album/${album.id}`);
              }}
              className="flex-shrink-0 px-3 py-2 bg-secondary hover:bg-secondary/90 text-white rounded-lg transition-all flex items-center gap-2"
            >
              <span className="text-sm">View</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="px-4 py-4 border-t border-border bg-accent/30">
        <div className="flex items-center justify-between gap-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="w-9 h-9 bg-background hover:bg-accent border border-border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0 flex items-center justify-center"
            aria-label="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-1.5 flex-1 justify-center min-w-0">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }

              return (
                <button
                  key={i}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`w-9 h-9 flex-shrink-0 rounded-lg transition-all text-sm ${
                    currentPage === pageNum
                      ? 'bg-secondary text-white'
                      : 'bg-background hover:bg-accent border border-border'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="w-9 h-9 bg-background hover:bg-accent border border-border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0 flex items-center justify-center"
            aria-label="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}