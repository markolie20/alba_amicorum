export interface Album {
  id: string;
  title: string;
  owner: string;
  year: number;
  location: {
    name: string;
    lat: number | null;
    lng: number | null;
  };
  country: string;
  description?: string;
  period?: string;
  language?: string;
  pages?: number;
  dimension?: string;
  condition?: string;
  scans?: string[];
  contributions?: Contribution[];
}

export interface Contribution {
  id: string;
  albumId: string;
  contributor: string;
  contributorTitle?: string;
  date: string;
  location: string;
  lat: number | null;
  lng: number | null;
  text?: string;
  language?: string;
  pageNumber?: number;
  scanUrls?: string[];
  name?: string;
  description?: string;
  sourceUrl?: string;
}