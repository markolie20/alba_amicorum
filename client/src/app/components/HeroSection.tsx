import { useEffect, useState } from 'react';
import { fetchStats, Stats } from '../api';

export function HeroSection() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  return (
    <section className="bg-gradient-to-br from-secondary/20 via-secondary/10 to-background border-b border-border">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-7xl mx-auto">
          <div className="space-y-6">
            <div className="inline-block px-4 py-2 bg-secondary/30 rounded-full border border-secondary/40">
              <span className="text-sm text-secondary-foreground">16e - 19e Eeuwse Europese Collecties</span>
            </div>
            <h2 className="text-4xl lg:text-5xl text-foreground leading-tight">
              Ontdek Historische Alba Amicorum
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Verken een samengestelde collectie vriendenboeken uit Renaissance- en Verlichtingstijdperk Europa.
              Deze bijzondere manuscripten bieden intieme inkijkjes in de sociale netwerken, artistieke smaak
              en intellectuele uitwisselingen van hun tijd.
            </p>
            <div className="flex gap-4 pt-4">
              <div className="text-center">
                <div className="text-3xl text-secondary">
                  {stats ? stats.albums : '—'}
                </div>
                <div className="text-sm text-muted-foreground">Albums</div>
              </div>
              <div className="w-px bg-border"></div>
              <div className="text-center">
                <div className="text-3xl text-secondary">
                  {stats ? stats.countries : '—'}
                </div>
                <div className="text-sm text-muted-foreground">Landen</div>
              </div>
              <div className="w-px bg-border"></div>
              <div className="text-center">
                <div className="text-3xl text-secondary">
                  {stats ? `${stats.years}+` : '—'}
                </div>
                <div className="text-sm text-muted-foreground">Jaar</div>
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary/30 to-transparent rounded-2xl blur-2xl"></div>
            <img
              src="/images/b2334151-d00d-43b7-832e-691876d9cb58/page_050.jpg"
              alt="Historisch Alba Amicorum"
              className="relative rounded-2xl shadow-2xl w-full object-cover aspect-[4/3] border border-border/50"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
