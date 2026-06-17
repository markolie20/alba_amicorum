import { useParams, useNavigate } from 'react-router';
import { useEffect, useState } from 'react';
import { ArrowLeft, Calendar, MapPin, Globe, FileText, Ruler, BookOpen, Languages, ChevronLeft, ChevronRight } from 'lucide-react';
import { Header } from '../components/Header';
import { ImageCarousel } from '../components/ImageCarousel';
import { ContributionsList } from '../components/ContributionsList';
import { fetchAlbumDetail } from '../api';
import { Album } from '../types';

export default function AlbumDetailPage() {
  const { albumId, contributionId } = useParams();
  const navigate = useNavigate();

  const [album, setAlbum] = useState<Album | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!albumId) return;
    setLoading(true);
    setError(null);
    fetchAlbumDetail(albumId)
      .then((data) => { setAlbum(data); setLoading(false); })
      .catch(() => { setError('Could not load album.'); setLoading(false); });
  }, [albumId]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [albumId, contributionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
          Loading album…
        </div>
      </div>
    );
  }

  if (error || !album) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="px-6 py-4 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive">
            {error ?? 'Album not found.'}
          </div>
        </div>
      </div>
    );
  }

  const contribution = contributionId
    ? album.contributions?.find((c) => c.id === contributionId)
    : null;

  const isMainPage = !contributionId;

  const sortedContributions = [...(album.contributions || [])].sort((a, b) =>
    (a.pageNumber ?? Infinity) - (b.pageNumber ?? Infinity)
  );

  const currentIndex = contributionId
    ? sortedContributions.findIndex((c) => c.id === contributionId)
    : -1; // -1 represents album overview

  const goToPrevious = () => {
    if (currentIndex === -1) {
      // Currently on album overview, go to last contribution
      const lastContribution = sortedContributions[sortedContributions.length - 1];
      if (lastContribution) {
        navigate(`/album/${albumId}/contribution/${lastContribution.id}`);
      }
    } else if (currentIndex === 0) {
      // First contribution, go to album overview
      navigate(`/album/${albumId}`);
    } else {
      // Go to previous contribution
      navigate(`/album/${albumId}/contribution/${sortedContributions[currentIndex - 1].id}`);
    }
  };

  const goToNext = () => {
    if (currentIndex === -1) {
      // Currently on album overview, go to first contribution
      const firstContribution = sortedContributions[0];
      if (firstContribution) {
        navigate(`/album/${albumId}/contribution/${firstContribution.id}`);
      }
    } else if (currentIndex === sortedContributions.length - 1) {
      // Last contribution, go to album overview
      navigate(`/album/${albumId}`);
    } else {
      // Go to next contribution
      navigate(`/album/${albumId}/contribution/${sortedContributions[currentIndex + 1].id}`);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <Header />

      {/* Back Button */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to search</span>
          </button>
        </div>
      </div>

      {/* Floating Navigation Buttons */}
      <button
        onClick={goToPrevious}
        className="fixed left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-secondary hover:bg-secondary/90 text-white rounded-full shadow-lg flex items-center justify-center transition-all z-10"
        aria-label="Previous"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>

      <button
        onClick={goToNext}
        className="fixed right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-secondary hover:bg-secondary/90 text-white rounded-full shadow-lg flex items-center justify-center transition-all z-10"
        aria-label="Next"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-6 py-6 space-y-6">
        <div className="flex gap-6 items-start">
          {/* Left Side - Image Carousel or Single Image (60%) */}
          <div className="flex-[1.5] min-w-0">
            {isMainPage ? (
              <div className="h-[600px]">
                <ImageCarousel images={album.scans || []} />
              </div>
            ) : contribution?.scanUrls && contribution.scanUrls.length > 0 ? (
              <div className="h-[600px]">
                <ImageCarousel images={contribution.scanUrls} />
              </div>
            ) : (
              <div className="w-full h-[600px] bg-card border border-border rounded-lg flex items-center justify-center shadow-sm">
                <p className="text-muted-foreground">No image available</p>
              </div>
            )}
          </div>

          {/* Right Side - Metadata (40%) */}
          <div className="flex-1 min-w-0">
            {/* Metadata Panel */}
            <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-border bg-accent/30">
                <h2 className="text-foreground">
                  {isMainPage ? album.title : contribution?.contributor}
                </h2>
                {!isMainPage && contribution?.contributorTitle && (
                  <p className="text-sm text-muted-foreground mt-1">{contribution.contributorTitle}</p>
                )}
                {!isMainPage && contribution?.name && (
                  <p className="text-sm text-muted-foreground mt-1">{contribution.name}</p>
                )}
              </div>

              <div className="p-6 space-y-4">
                {isMainPage ? (
                  <>
                    {/* Album Overview Metadata */}
                    {album.description && (
                      <div>
                        <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
                          {album.description}
                        </p>
                      </div>
                    )}

                    <div className="grid grid-cols-1 gap-3 pt-2">
                      <div className="flex items-start gap-3">
                        <BookOpen className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-muted-foreground">Owner</div>
                          <div className="text-sm text-foreground">{album.owner}</div>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <Calendar className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-muted-foreground">Period</div>
                          <div className="text-sm text-foreground">
                            {album.period || album.year}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <MapPin className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-muted-foreground">Location</div>
                          <div className="text-sm text-foreground">{album.location.name}</div>
                        </div>
                      </div>

                      {album.language && (
                        <div className="flex items-start gap-3">
                          <Languages className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Languages</div>
                            <div className="text-sm text-foreground">{album.language}</div>
                          </div>
                        </div>
                      )}

                      {album.pages && (
                        <div className="flex items-start gap-3">
                          <FileText className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Pages</div>
                            <div className="text-sm text-foreground">{album.pages} pages</div>
                          </div>
                        </div>
                      )}

                      {album.dimension && (
                        <div className="flex items-start gap-3">
                          <Ruler className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Dimensions</div>
                            <div className="text-sm text-foreground">{album.dimension}</div>
                          </div>
                        </div>
                      )}

                      {album.condition && (
                        <div className="flex items-start gap-3">
                          <Globe className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Condition</div>
                            <div className="text-sm text-foreground">{album.condition}</div>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    {/* Contribution Metadata */}
                    {contribution?.description && (
                      <div className="p-4 bg-accent/20 rounded-lg border border-border">
                        <p className="text-sm text-foreground leading-relaxed whitespace-pre-line">{contribution.description}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-1 gap-3">
                      <div className="flex items-start gap-3">
                        <Calendar className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-muted-foreground">Date</div>
                          <div className="text-sm text-foreground">{contribution.date}</div>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <MapPin className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-muted-foreground">Location</div>
                          <div className="text-sm text-foreground">{contribution.location}</div>
                        </div>
                      </div>

                      {contribution.language && (
                        <div className="flex items-start gap-3">
                          <Languages className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Language</div>
                            <div className="text-sm text-foreground">{contribution.language}</div>
                          </div>
                        </div>
                      )}

                      {contribution.pageNumber && (
                        <div className="flex items-start gap-3">
                          <FileText className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Page Number</div>
                            <div className="text-sm text-foreground">Page {contribution.pageNumber}</div>
                          </div>
                        </div>
                      )}

                      {contribution.sourceUrl && (
                        <div className="flex items-start gap-3">
                          <Globe className="w-4 h-4 text-secondary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs text-muted-foreground">Source</div>
                            <a
                              href={contribution.sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-secondary hover:underline break-all"
                            >
                              View on data.bibliotheken.nl
                            </a>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Contributions List - Full Width Below */}
        {album.contributions && album.contributions.length > 0 && (
          <ContributionsList
            contributions={album.contributions}
            albumId={albumId!}
            albumTitle={album.title}
            albumYear={album.year}
            albumLocation={album.location.name}
            albumImage={album.scans?.[0]}
          />
        )}
      </div>
    </div>
  );
}