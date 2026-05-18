export interface Album {
  id: string;
  title: string;
  owner: string;
  year: number;
  location: {
    name: string;
    lat: number;
    lng: number;
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
  lat: number;
  lng: number;
  text?: string;
  language?: string;
  pageNumber?: number;
  scanUrl?: string;
}