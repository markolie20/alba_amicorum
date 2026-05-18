import { Calendar, MapPin, Book } from 'lucide-react';
import { useNavigate, useParams } from 'react-router';
import { Contribution } from '../types';

interface ContributionsListProps {
  contributions: Contribution[];
  albumId: string;
  albumTitle: string;
  albumYear: number;
  albumLocation: string;
  albumImage?: string;
}

export function ContributionsList({
  contributions,
  albumId,
  albumTitle,
  albumYear,
  albumLocation,
  albumImage
}: ContributionsListProps) {
  const navigate = useNavigate();
  const { contributionId } = useParams();
  const isMainPage = !contributionId;

  // Extract year from date string and sort by year
  const sortedContributions = [...contributions].sort((a, b) => {
    const yearA = parseInt(a.date.match(/\d{4}/)?.[0] || '0');
    const yearB = parseInt(b.date.match(/\d{4}/)?.[0] || '0');
    return yearA - yearB;
  });

  return (
    <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-border bg-accent/30">
        <h3 className="text-foreground">Album & Contributions ({contributions.length + 1})</h3>
      </div>

      <div className="p-4 space-y-3">
        {/* Album Overview Card */}
        <button
          onClick={() => navigate(`/album/${albumId}`)}
          className={`w-full flex items-center gap-4 p-4 border border-border rounded-lg transition-all text-left ${
            isMainPage
              ? 'bg-secondary/20 border-secondary'
              : 'bg-background hover:bg-accent/30'
          }`}
        >
          {/* Image */}
          {albumImage && (
            <div className="flex-shrink-0 w-24 h-24 rounded-lg overflow-hidden border border-border">
              <img
                src={albumImage}
                alt={albumTitle}
                className="w-full h-full object-cover"
              />
            </div>
          )}
          {!albumImage && (
            <div className="flex-shrink-0 w-24 h-24 rounded-lg bg-gradient-to-br from-secondary/30 to-secondary/10 border border-secondary/40 flex items-center justify-center">
              <Book className="w-12 h-12 text-secondary" />
            </div>
          )}

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h4 className="text-foreground truncate mb-2 font-medium">Album Overview</h4>
            <p className="text-sm text-muted-foreground mb-2 truncate">
              {albumTitle}
            </p>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-secondary" />
                <span className="truncate">{albumLocation}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="w-3.5 h-3.5 flex-shrink-0 text-secondary" />
                <span>{albumYear}</span>
              </div>
            </div>
          </div>
        </button>

        {/* Contributions */}
        {sortedContributions.map((contribution) => {
          const year = contribution.date.match(/\d{4}/)?.[0] || '';

          return (
            <button
              key={contribution.id}
              onClick={() => navigate(`/album/${albumId}/contribution/${contribution.id}`)}
              className={`w-full flex items-center gap-4 p-4 border border-border rounded-lg transition-all text-left ${
                contributionId === contribution.id
                  ? 'bg-secondary/20 border-secondary'
                  : 'bg-background hover:bg-accent/30'
              }`}
            >
              {/* Image */}
              {contribution.scanUrl && (
                <div className="flex-shrink-0 w-24 h-24 rounded-lg overflow-hidden border border-border">
                  <img
                    src={contribution.scanUrl}
                    alt={`Contribution by ${contribution.contributor}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Content */}
              <div className="flex-1 min-w-0">
                <h4 className="text-foreground truncate mb-2">{contribution.contributor}</h4>
                {contribution.contributorTitle && (
                  <p className="text-sm text-muted-foreground mb-2 truncate">
                    {contribution.contributorTitle}
                  </p>
                )}
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="w-3.5 h-3.5 flex-shrink-0 text-secondary" />
                    <span className="truncate">{contribution.location}</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="w-3.5 h-3.5 flex-shrink-0 text-secondary" />
                    <span>{year}</span>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
