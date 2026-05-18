import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Album } from '../types';

interface AlbaMapProps {
  albums: Album[];
  selectedAlbumId?: string | null;
}

export function AlbaMap({ albums, selectedAlbumId }: AlbaMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current).setView([50.8503, 4.3517], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Create custom panes for proper layering
    // Default markerPane is at z-index 600

    // Lines pane above markers
    map.createPane('linesPane');
    const linesPane = map.getPane('linesPane');
    if (linesPane) {
      linesPane.style.zIndex = '610'; // Above markers (600)
    }

    // Numbers pane above lines
    map.createPane('numbersPane');
    const numbersPane = map.getPane('numbersPane');
    if (numbersPane) {
      numbersPane.style.zIndex = '620'; // Above lines (610)
    }

    mapInstanceRef.current = map;

    // Force map to resize after initialization
    const timeoutId = setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
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

    // Clear existing markers and polylines
    mapInstanceRef.current.eachLayer((layer) => {
      if (layer instanceof L.Marker || layer instanceof L.Polyline) {
        mapInstanceRef.current?.removeLayer(layer);
      }
    });

    // Filter albums if one is selected
    const displayAlbums = selectedAlbumId
      ? albums.filter((album) => album.id === selectedAlbumId)
      : albums;

    // Group albums by location to show counts
    const locationGroups = displayAlbums.reduce((acc, album) => {
      const key = `${album.location.lat},${album.location.lng}`;
      if (!acc[key]) {
        acc[key] = {
          location: album.location,
          count: 0,
          albums: []
        };
      }
      acc[key].count++;
      acc[key].albums.push(album);
      return acc;
    }, {} as Record<string, { location: { lat: number; lng: number; name: string }; count: number; albums: Album[] }>);

    // Add album markers (blue) - empty when selected, count when not
    Object.values(locationGroups).forEach((group) => {
      const displayText = selectedAlbumId ? '' : group.count;
      const icon = L.divIcon({
        html: `<div class="flex items-center justify-center w-10 h-10 bg-secondary text-white rounded-full border-2 border-white shadow-lg font-medium">${displayText}</div>`,
        className: 'custom-marker',
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      });

      const marker = L.marker([group.location.lat, group.location.lng], { icon });

      // Create popup content
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

    // If an album is selected, show contribution markers (gold/amber)
    if (selectedAlbumId && displayAlbums.length === 1) {
      const selectedAlbum = displayAlbums[0];

      if (selectedAlbum.contributions) {
        // Sort contributions chronologically
        const sortedContributions = [...selectedAlbum.contributions].sort((a, b) => {
          const yearA = parseInt(a.date.match(/\d{4}/)?.[0] || '0');
          const yearB = parseInt(b.date.match(/\d{4}/)?.[0] || '0');
          return yearA - yearB;
        });

        // Create path coordinates: album -> contribution1 -> contribution2 -> ...
        const pathCoordinates: [number, number][] = [
          [selectedAlbum.location.lat, selectedAlbum.location.lng],
          ...sortedContributions.map(c => [c.lat, c.lng] as [number, number])
        ];

        // Draw white outline for better visibility
        const polylineShadow = L.polyline(pathCoordinates, {
          color: '#ffffff',
          weight: 5,
          opacity: 0.8,
          pane: 'linesPane'
        });
        polylineShadow.addTo(mapInstanceRef.current!);

        // Draw black solid line connecting all points (on top)
        const polyline = L.polyline(pathCoordinates, {
          color: '#000000',
          weight: 3,
          opacity: 0.9,
          pane: 'linesPane'
        });
        polyline.addTo(mapInstanceRef.current!);

        // Group contributions by location
        const contributionGroups = selectedAlbum.contributions.reduce((acc, contribution) => {
          const key = `${contribution.lat},${contribution.lng}`;
          if (!acc[key]) {
            acc[key] = {
              lat: contribution.lat,
              lng: contribution.lng,
              location: contribution.location,
              count: 0,
              contributions: []
            };
          }
          acc[key].count++;
          acc[key].contributions.push(contribution);
          return acc;
        }, {} as Record<string, { lat: number; lng: number; location: string; count: number; contributions: typeof selectedAlbum.contributions }>);

        // Add contribution markers (empty gold circles)
        Object.values(contributionGroups).forEach((group) => {
          const icon = L.divIcon({
            html: `<div class="flex items-center justify-center w-10 h-10 bg-[#cba052] text-white rounded-full border-2 border-white shadow-lg font-medium"></div>`,
            className: 'custom-marker',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
          });

          const marker = L.marker([group.lat, group.lng], { icon });

          // Create popup content for contributions
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

        // Add number 1 at the album starting point (white text overlay)
        const albumNumberIcon = L.divIcon({
          html: `<div class="flex items-center justify-center w-10 h-10 text-white font-bold text-lg" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">1</div>`,
          className: 'custom-number-marker',
          iconSize: [40, 40],
          iconAnchor: [20, 20]
        });

        const albumNumberMarker = L.marker([selectedAlbum.location.lat, selectedAlbum.location.lng], {
          icon: albumNumberIcon,
          pane: 'numbersPane'
        });
        albumNumberMarker.addTo(mapInstanceRef.current!);

        // Add numbers 2, 3, 4, etc. on contributions in chronological order
        sortedContributions.forEach((contribution, index) => {
          const number = index + 2; // Start from 2 (1 is the album)
          const numberIcon = L.divIcon({
            html: `<div class="flex items-center justify-center w-10 h-10 text-white font-bold text-lg" style="text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">${number}</div>`,
            className: 'custom-number-marker',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
          });

          const numberMarker = L.marker([contribution.lat, contribution.lng], {
            icon: numberIcon,
            pane: 'numbersPane'
          });
          numberMarker.addTo(mapInstanceRef.current!);
        });
      }

      // Zoom to show both album and all contributions
      mapInstanceRef.current.setView([selectedAlbum.location.lat, selectedAlbum.location.lng], 7);
    } else if (!selectedAlbumId && albums.length > 0) {
      // Reset to default view when no album is selected
      mapInstanceRef.current.setView([50.8503, 4.3517], 5);
    }
  }, [albums, selectedAlbumId]);

  return (
    <div className="h-full rounded-lg overflow-hidden border border-border shadow-sm bg-card">
      <div ref={mapRef} className="h-full w-full" />
    </div>
  );
}