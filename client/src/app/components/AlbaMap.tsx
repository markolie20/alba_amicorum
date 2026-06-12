import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Album, Contribution } from '../types';

interface AlbaMapProps {
  albums: Album[];
  selectedAlbumId?: string | null;
  /** Full album detail including contributions — fetched on demand when an album is selected. */
  selectedAlbumDetail?: Album | null;
  /** Shows a loading overlay on the map while the detail is being fetched. */
  detailLoading?: boolean;
}

function hasCoords(obj: { lat: number | null; lng: number | null }): obj is { lat: number; lng: number } {
  return obj.lat !== null && obj.lng !== null;
}

export function AlbaMap({ albums, selectedAlbumId, selectedAlbumDetail, detailLoading }: AlbaMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [noLocations, setNoLocations] = useState(false);
  const [numbersVisible, setNumbersVisible] = useState(false);

  useEffect(() => {
    const numbersPane = mapInstanceRef.current?.getPane('numbersPane');
    const linesPane = mapInstanceRef.current?.getPane('linesPane');
    if (numbersPane) numbersPane.style.display = numbersVisible ? '' : 'none';
    if (linesPane) linesPane.style.display = numbersVisible ? '' : 'none';
  }, [numbersVisible]);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    const map = L.map(mapRef.current).setView([50.8503, 4.3517], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    map.createPane('linesPane');
    const linesPane = map.getPane('linesPane');
    if (linesPane) linesPane.style.zIndex = '590';

    map.createPane('albumMarkerPane');
    const albumMarkerPane = map.getPane('albumMarkerPane');
    if (albumMarkerPane) albumMarkerPane.style.zIndex = '615';

    map.createPane('contributionMarkerPane');
    const contributionMarkerPane = map.getPane('contributionMarkerPane');
    if (contributionMarkerPane) contributionMarkerPane.style.zIndex = '612';

    map.createPane('numbersPane');
    const numbersPane = map.getPane('numbersPane');
    if (numbersPane) numbersPane.style.zIndex = '610';

    mapInstanceRef.current = map;

    const timeoutId = setTimeout(() => {
      mapInstanceRef.current?.invalidateSize();
    }, 100);

    return () => {
      clearTimeout(timeoutId);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    mapInstanceRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        mapInstanceRef.current?.removeLayer(layer);
      }
    });

    // Hide journey (lines + numbers) on every redraw and reset the React state to match
    const numbersPaneEl = mapInstanceRef.current.getPane('numbersPane');
    const linesPaneEl = mapInstanceRef.current.getPane('linesPane');
    if (numbersPaneEl) numbersPaneEl.style.display = 'none';
    if (linesPaneEl) linesPaneEl.style.display = 'none';
    setNumbersVisible(false);

    const displayAlbums = selectedAlbumId
      ? albums.filter((album) => album.id === selectedAlbumId)
      : albums;

    // Only plot albums that have coordinates
    const plottableAlbums = displayAlbums.filter((album) => hasCoords(album.location));

    // Group plottable albums by location
    const locationGroups = plottableAlbums.reduce((acc, album) => {
      const key = `${album.location.lat},${album.location.lng}`;
      if (!acc[key]) {
        acc[key] = {
          location: album.location as { lat: number; lng: number; name: string },
          count: 0,
          albums: [],
        };
      }
      acc[key].count++;
      acc[key].albums.push(album);
      return acc;
    }, {} as Record<string, { location: { lat: number; lng: number; name: string }; count: number; albums: Album[] }>);

    const PIN_PATH = 'M12 0 C5.373 0 0 5.373 0 12 C0 25 8 34 12 34 C16 34 24 25 24 12 C24 5.373 18.627 0 12 0 Z';

    Object.values(locationGroups).forEach((group) => {
      const displayText = selectedAlbumId ? '' : group.count;
      const pinHtml = `
        <div style="position:relative;width:24px;height:34px">
          <svg width="24" height="34" viewBox="0 0 24 34" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 2px 4px rgba(80,110,160,0.25))">
            <path d="${PIN_PATH}" style="fill:var(--primary)" stroke="black" stroke-width="1"/>
          </svg>
          ${displayText !== '' ? `<div style="position:absolute;top:4px;left:0;width:24px;text-align:center;color:white;font-size:10px;font-weight:700;line-height:1;pointer-events:none">${displayText}</div>` : ''}
        </div>`;
      const icon = L.divIcon({
        html: pinHtml,
        className: '',
        iconSize: [24, 34],
        iconAnchor: [12, 34],
      });

      const markerOptions = selectedAlbumId ? { icon, pane: 'albumMarkerPane' } : { icon };
      const marker = L.marker([group.location.lat, group.location.lng], markerOptions);

      let popupContent = `
        <div class="p-2">
          <div class="font-medium text-sm mb-2">${group.location.name}</div>
          <div class="text-xs text-muted-foreground mb-2">
            ${group.count} ${group.count === 1 ? 'album' : 'albums'}
          </div>
          <div class="space-y-1">
      `;
      group.albums.slice(0, 3).forEach((album) => {
        popupContent += `<div class="text-xs">• ${album.title}</div>`;
      });
      if (group.albums.length > 3) {
        popupContent += `<div class="text-xs text-muted-foreground">+${group.albums.length - 3} more</div>`;
      }
      popupContent += `</div></div>`;

      marker.bindPopup(popupContent);
      marker.addTo(mapInstanceRef.current!);
    });

    if (selectedAlbumId && displayAlbums.length === 1) {
      const selectedAlbum = displayAlbums[0];
      // Prefer the fully-fetched detail (has contributions); fall back to the list item (mock data).
      const albumWithContributions = selectedAlbumDetail ?? selectedAlbum;

      if (albumWithContributions.contributions) {
        const sortedContributions = [...albumWithContributions.contributions].sort((a, b) => {
          const yearA = parseInt(a.date.match(/\d{4}/)?.[0] || '0');
          const yearB = parseInt(b.date.match(/\d{4}/)?.[0] || '0');
          return yearA - yearB;
        });

        // Build polyline only from points that have coordinates
        const pathCoordinates: [number, number][] = [];
        if (hasCoords(selectedAlbum.location)) {
          pathCoordinates.push([selectedAlbum.location.lat, selectedAlbum.location.lng]);
        }
        sortedContributions.forEach((c) => {
          if (hasCoords(c)) pathCoordinates.push([c.lat, c.lng]);
        });

        // Show overlay when there is nothing at all to plot
        setNoLocations(pathCoordinates.length === 0);

        if (pathCoordinates.length > 1) {
          L.polyline(pathCoordinates, {
            color: '#ffffff',
            weight: 5,
            opacity: 0.8,
            pane: 'linesPane',
          }).addTo(mapInstanceRef.current!);

          L.polyline(pathCoordinates, {
            color: '#000000',
            weight: 3,
            opacity: 0.9,
            pane: 'linesPane',
          }).addTo(mapInstanceRef.current!);
        }

        // Group contributions that have coordinates by location
        const plottableContributions = albumWithContributions.contributions.filter(
          (c): c is Contribution & { lat: number; lng: number } => hasCoords(c)
        );

        const contributionGroups = plottableContributions.reduce((acc, contribution) => {
          const key = `${contribution.lat},${contribution.lng}`;
          if (!acc[key]) {
            acc[key] = {
              lat: contribution.lat,
              lng: contribution.lng,
              location: contribution.location,
              count: 0,
              contributions: [] as (Contribution & { lat: number; lng: number })[],
            };
          }
          acc[key].count++;
          acc[key].contributions.push(contribution);
          return acc;
        }, {} as Record<string, { lat: number; lng: number; location: string; count: number; contributions: (Contribution & { lat: number; lng: number })[] }>);

        Object.values(contributionGroups).forEach((group) => {
          const icon = L.divIcon({
            html: `<svg width="24" height="34" viewBox="0 0 24 34" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 2px 4px rgba(80,110,160,0.25))"><path d="${PIN_PATH}" style="fill:var(--secondary)" stroke="black" stroke-width="1"/></svg>`,
            className: '',
            iconSize: [24, 34],
            iconAnchor: [12, 34],
          });

          const marker = L.marker([group.lat, group.lng], { icon, pane: 'contributionMarkerPane' });

          let popupContent = `
            <div class="p-2">
              <div class="font-medium text-sm mb-2">${group.location}</div>
              <div class="text-xs text-muted-foreground mb-2">
                ${group.count} ${group.count === 1 ? 'contribution' : 'contributions'}
              </div>
              <div class="space-y-1">
          `;
          group.contributions.slice(0, 3).forEach((contribution) => {
            popupContent += `<div class="text-xs">• ${contribution.contributor}</div>`;
          });
          if (group.contributions.length > 3) {
            popupContent += `<div class="text-xs text-muted-foreground">+${group.contributions.length - 3} more</div>`;
          }
          popupContent += `</div></div>`;

          marker.bindPopup(popupContent);
          marker.addTo(mapInstanceRef.current!);
        });

        // Number labels placed on each segment, split by direction.
        // For a segment A↔B with labels [1,5,7,14] going A→B and [2,11] going B→A,
        // the layout is: A--1--5--7--14----11--2--B
        // (one empty slot separates the two directions; each side sorted ascending from its origin)
        if (pathCoordinates.length >= 2) {
          type SegEntry = { ab: number[]; ba: number[]; aLat: number; aLng: number; bLat: number; bLng: number };
          const segmentMap = new Map<string, SegEntry>();
          let segLabel = 1;

          // Pass 1: collect every journey step into its undirected segment bucket.
          // Same-location steps (contribution didn't travel) are skipped without
          // advancing the counter, so displayed numbers stay consecutive.
          for (let i = 0; i < pathCoordinates.length - 1; i++) {
            const [lat1, lng1] = pathCoordinates[i];
            const [lat2, lng2] = pathCoordinates[i + 1];
            if (lat1 === lat2 && lng1 === lng2) continue;

            // Canonical key: lexicographically smaller endpoint is "A".
            const k1 = `${lat1},${lng1}`;
            const k2 = `${lat2},${lng2}`;
            const isForward = k1 < k2;
            const segKey = isForward ? `${k1}|${k2}` : `${k2}|${k1}`;

            if (!segmentMap.has(segKey)) {
              segmentMap.set(segKey, {
                ab: [], ba: [],
                aLat: isForward ? lat1 : lat2, aLng: isForward ? lng1 : lng2,
                bLat: isForward ? lat2 : lat1, bLng: isForward ? lng2 : lng1,
              });
            }
            const entry = segmentMap.get(segKey)!;
            if (isForward) entry.ab.push(segLabel);
            else           entry.ba.push(segLabel);
            segLabel++;
          }

          // Pass 2: place labels and directional arrows on each segment.
          const makeLabelIcon = (lbl: number) => L.divIcon({
            html: `<div style="background:#000;color:#fff;border-radius:999px;min-width:20px;height:20px;padding:0 5px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;box-shadow:0 1px 3px rgba(0,0,0,0.5);white-space:nowrap;">${lbl}</div>`,
            className: '',
            iconSize: [20, 20],
            iconAnchor: [10, 10],
          });

          for (const { ab, ba, aLat, aLng, bLat, bLng } of segmentMap.values()) {
            if (ab.length === 0 && ba.length === 0) continue;

            const abSorted = [...ab].sort((x, y) => x - y);
            const baSorted = [...ba].sort((x, y) => x - y);
            const totalDivisions = abSorted.length + baSorted.length + 2;

            const interp = (f: number): [number, number] => [
              aLat + (bLat - aLat) * f,
              aLng + (bLng - aLng) * f,
            ];

            // Screen-space angle of A→B, used to rotate arrowheads.
            const pA = mapInstanceRef.current!.latLngToContainerPoint([aLat, aLng]);
            const pB = mapInstanceRef.current!.latLngToContainerPoint([bLat, bLng]);
            const angleAB = Math.atan2(pB.y - pA.y, pB.x - pA.x) * 180 / Math.PI;

            const makeArrow = (f: number, angle: number) =>
              L.marker(interp(f), {
                icon: L.divIcon({
                  html: `<div style="transform:rotate(${angle}deg);display:flex;align-items:center;justify-content:center;width:10px;height:10px;"><svg width="10" height="10" viewBox="0 0 10 10"><polygon points="0,0 10,5 0,10" fill="#333"/></svg></div>`,
                  className: '',
                  iconSize: [10, 10],
                  iconAnchor: [5, 5],
                }),
                pane: 'numbersPane',
              }).addTo(mapInstanceRef.current!);

            // Number labels.
            abSorted.forEach((lbl, idx) =>
              L.marker(interp((idx + 1) / totalDivisions), { icon: makeLabelIcon(lbl), pane: 'numbersPane' }).addTo(mapInstanceRef.current!)
            );
            baSorted.forEach((lbl, idx) =>
              L.marker(interp((totalDivisions - 1 - idx) / totalDivisions), { icon: makeLabelIcon(lbl), pane: 'numbersPane' }).addTo(mapInstanceRef.current!)
            );

            // A→B arrows: one before each A→B label, starting from A.
            // Layout: A ->- l1 ->- l2 ->- ... ->- ln  [gap]
            abSorted.forEach((_, idx) => {
              const fPrev = idx === 0 ? 0 : idx / totalDivisions;
              const fCurr = (idx + 1) / totalDivisions;
              makeArrow((fPrev + fCurr) / 2, angleAB);
            });

            // B→A arrows: one between each consecutive B→A pair, then one to B.
            // Layout: [gap]  lm -<- ... -<- l1 -<- B
            for (let j = baSorted.length - 1; j >= 0; j--) {
              const fThis = (totalDivisions - 1 - j) / totalDivisions;
              const fNext = j === 0 ? 1 : (totalDivisions - j) / totalDivisions;
              makeArrow((fThis + fNext) / 2, angleAB + 180);
            }
          }
        }
      }

      // Zoom to album location if it has coords, otherwise keep default view
      if (hasCoords(selectedAlbum.location)) {
        mapInstanceRef.current.setView([selectedAlbum.location.lat, selectedAlbum.location.lng], 7);
      }
    } else {
      setNoLocations(false);
      if (!selectedAlbumId && albums.length > 0) {
        mapInstanceRef.current.setView([50.8503, 4.3517], 5);
      }
    }
  }, [albums, selectedAlbumId, selectedAlbumDetail]);

  return (
    <div className="relative h-full rounded-lg overflow-hidden border border-border shadow-sm bg-card">
      <div ref={mapRef} className="h-full w-full" />
      {selectedAlbumId && (
        <button
          onClick={() => setNumbersVisible(v => !v)}
          className="absolute top-2 right-2 z-[1000] px-3 py-1.5 text-xs font-medium rounded-md bg-card border border-border shadow-sm hover:bg-accent transition-colors"
        >
          {numbersVisible ? 'Hide journey' : 'Show journey'}
        </button>
      )}
      {detailLoading && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[1000]">
          <div className="bg-card/90 border border-border rounded-lg px-5 py-3 shadow-lg text-sm text-muted-foreground">
            Loading locations…
          </div>
        </div>
      )}
      {!detailLoading && noLocations && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-[1000]">
          <div className="bg-card/90 border border-border rounded-lg px-5 py-3 shadow-lg text-sm text-muted-foreground">
            No locations found for this album
          </div>
        </div>
      )}
    </div>
  );
}
