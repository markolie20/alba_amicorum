import { useNavigate, useParams } from 'react-router';
import { Book, User } from 'lucide-react';
import { Contribution } from '../types';

interface ContributionsSidebarProps {
  albumId: string;
  albumTitle: string;
  contributions: Contribution[];
}

export function ContributionsSidebar({
  albumId,
  albumTitle,
  contributions,
}: ContributionsSidebarProps) {
  const navigate = useNavigate();
  const { contributionId } = useParams();

  const isMainPage = !contributionId;

  return (
    <div className="h-full flex flex-col bg-card border border-border rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border bg-accent/30">
        <h3 className="text-foreground">Navigation</h3>
      </div>

      {/* Main Album Link - Pinned at Top */}
      <div className="border-b border-border">
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            navigate(`/album/${albumId}`);
          }}
          className={`w-full text-left px-4 py-3 transition-all flex items-center gap-3 cursor-pointer ${
            isMainPage
              ? 'bg-secondary/20 border-l-4 border-secondary'
              : 'hover:bg-accent/50 border-l-4 border-transparent'
          }`}
        >
          <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-secondary/30 to-secondary/10 rounded-lg flex items-center justify-center border border-secondary/40">
            <Book className="w-5 h-5 text-secondary" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-foreground truncate">Album Overview</div>
            <div className="text-xs text-muted-foreground truncate">{albumTitle}</div>
          </div>
        </button>
      </div>

      {/* Contributions List */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-2">
          <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
            Contributions ({contributions.length})
          </div>
        </div>

        <div className="space-y-1 px-2 pb-4">
          {contributions.map((contribution) => (
            <button
              key={contribution.id}
              type="button"
              onClick={(e) => {
                e.preventDefault();
                navigate(`/album/${albumId}/contribution/${contribution.id}`);
              }}
              className={`w-full text-left px-3 py-2.5 rounded-lg transition-all flex items-start gap-3 cursor-pointer ${
                contributionId === contribution.id
                  ? 'bg-secondary/20 border-l-4 border-secondary'
                  : 'hover:bg-accent/50 border-l-4 border-transparent'
              }`}
            >
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-secondary/40 to-secondary/20 rounded-full flex items-center justify-center border border-secondary/40 mt-0.5">
                <User className="w-4 h-4 text-secondary-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-foreground truncate">{contribution.contributor}</div>
                <div className="text-xs text-muted-foreground truncate">{contribution.date}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}