import { Album } from '../types';

export const mockAlbums: Album[] = [
  {
    id: '1',
    title: 'Album Amicorum of Johannes Wtenbogaert',
    owner: 'Johannes Wtenbogaert',
    year: 1584,
    location: { name: 'Amsterdam, Netherlands', lat: 52.3676, lng: 4.9041 },
    country: 'Netherlands',
    contributions: [
      {
        id: 'c1-1',
        albumId: '1',
        contributor: 'Hugo Grotius',
        date: '1583',
        location: 'Delft, Netherlands',
        lat: 52.0116,
        lng: 4.3571,
      },
      {
        id: 'c1-2',
        albumId: '1',
        contributor: 'Justus Lipsius',
        date: '1584',
        location: 'Leiden, Netherlands',
        lat: 52.1601,
        lng: 4.4970,
      },
      {
        id: 'c1-3',
        albumId: '1',
        contributor: 'Daniel Heinsius',
        date: '1584',
        location: 'The Hague, Netherlands',
        lat: 52.0705,
        lng: 4.3007,
      },
    ]
  },
  {
    id: '2',
    title: 'Album of Philipp Hainhofer',
    owner: 'Philipp Hainhofer',
    year: 1596,
    location: { name: 'Augsburg, Germany', lat: 48.3705, lng: 10.8978 },
    country: 'Germany',
    contributions: [
      {
        id: 'c2-1',
        albumId: '2',
        contributor: 'Michael Maier',
        date: '1595',
        location: 'Prague, Czech Republic',
        lat: 50.0755,
        lng: 14.4378,
      },
      {
        id: 'c2-2',
        albumId: '2',
        contributor: 'Johannes Kepler',
        date: '1596',
        location: 'Graz, Austria',
        lat: 47.0707,
        lng: 15.4395,
      },
      {
        id: 'c2-3',
        albumId: '2',
        contributor: 'Georg Flegel',
        date: '1596',
        location: 'Frankfurt, Germany',
        lat: 50.1109,
        lng: 8.6821,
      },
    ]
  },
  {
    id: '3',
    title: 'Friendship Album of Marie de Gournay',
    owner: 'Marie de Gournay',
    year: 1607,
    location: { name: 'Paris, France', lat: 48.8566, lng: 2.3522 },
    country: 'France'
  },
  {
    id: '4',
    title: 'Album Amicorum of Jacob Heyblocq',
    owner: 'Jacob Heyblocq',
    year: 1645,
    location: { name: 'Leiden, Netherlands', lat: 52.1601, lng: 4.4970 },
    country: 'Netherlands'
  },
  {
    id: '5',
    title: 'Album of Constantijn Huygens',
    owner: 'Constantijn Huygens',
    year: 1623,
    location: { name: 'The Hague, Netherlands', lat: 52.0705, lng: 4.3007 },
    country: 'Netherlands',
    contributions: [
      {
        id: 'c5-1',
        albumId: '5',
        contributor: 'René Descartes',
        date: '1622',
        location: 'Paris, France',
        lat: 48.8566,
        lng: 2.3522,
      },
      {
        id: 'c5-2',
        albumId: '5',
        contributor: 'John Donne',
        date: '1623',
        location: 'London, England',
        lat: 51.5074,
        lng: -0.1278,
      },
      {
        id: 'c5-3',
        albumId: '5',
        contributor: 'Peter Paul Rubens',
        date: '1623',
        location: 'Antwerp, Belgium',
        lat: 51.2194,
        lng: 4.4025,
      },
      {
        id: 'c5-4',
        albumId: '5',
        contributor: 'Anna Maria van Schurman',
        date: '1623',
        location: 'Utrecht, Netherlands',
        lat: 52.0907,
        lng: 5.1214,
      },
    ]
  },
  {
    id: '6',
    title: 'Album of Daniel Heinsius',
    owner: 'Daniel Heinsius',
    year: 1603,
    location: { name: 'Leiden, Netherlands', lat: 52.1601, lng: 4.4970 },
    country: 'Netherlands'
  },
  {
    id: '7',
    title: 'Album Amicorum of Georg Flegel',
    owner: 'Georg Flegel',
    year: 1615,
    location: { name: 'Frankfurt, Germany', lat: 50.1109, lng: 8.6821 },
    country: 'Germany'
  },
  {
    id: '8',
    title: 'Friendship Album of Erasmus',
    owner: 'Desiderius Erasmus',
    year: 1520,
    location: { name: 'Rotterdam, Netherlands', lat: 51.9225, lng: 4.4792 },
    country: 'Netherlands'
  },
  {
    id: '9',
    title: 'Album of Michel de Montaigne',
    owner: 'Michel de Montaigne',
    year: 1580,
    location: { name: 'Bordeaux, France', lat: 44.8378, lng: -0.5792 },
    country: 'France'
  },
  {
    id: '10',
    title: 'Album Amicorum of Justus Lipsius',
    owner: 'Justus Lipsius',
    year: 1592,
    location: { name: 'Leuven, Belgium', lat: 50.8798, lng: 4.7005 },
    country: 'Belgium'
  },
  {
    id: '11',
    title: 'Album of John Donne',
    owner: 'John Donne',
    year: 1611,
    location: { name: 'London, England', lat: 51.5074, lng: -0.1278 },
    country: 'England'
  },
  {
    id: '12',
    title: 'Album Amicorum of Andreas Vesalius',
    owner: 'Andreas Vesalius',
    year: 1543,
    location: { name: 'Brussels, Belgium', lat: 50.8503, lng: 4.3517 },
    country: 'Belgium'
  },
  {
    id: '13',
    title: 'Album of Christoph Scheiner',
    owner: 'Christoph Scheiner',
    year: 1626,
    location: { name: 'Ingolstadt, Germany', lat: 48.7665, lng: 11.4257 },
    country: 'Germany'
  },
  {
    id: '14',
    title: 'Friendship Album of Galileo Galilei',
    owner: 'Galileo Galilei',
    year: 1609,
    location: { name: 'Padua, Italy', lat: 45.4064, lng: 11.8768 },
    country: 'Italy',
    contributions: [
      {
        id: 'c14-1',
        albumId: '14',
        contributor: 'Johannes Kepler',
        date: '1608',
        location: 'Prague, Czech Republic',
        lat: 50.0755,
        lng: 14.4378,
      },
      {
        id: 'c14-2',
        albumId: '14',
        contributor: 'Christoph Clavius',
        date: '1609',
        location: 'Rome, Italy',
        lat: 41.9028,
        lng: 12.4964,
      },
      {
        id: 'c14-3',
        albumId: '14',
        contributor: 'Paolo Sarpi',
        date: '1609',
        location: 'Venice, Italy',
        lat: 45.4408,
        lng: 12.3155,
      },
    ]
  },
  {
    id: '15',
    title: 'Album Amicorum of Hugo Grotius',
    owner: 'Hugo Grotius',
    year: 1618,
    location: { name: 'Delft, Netherlands', lat: 52.0116, lng: 4.3571 },
    country: 'Netherlands'
  },
  {
    id: '16',
    title: 'Album of René Descartes',
    owner: 'René Descartes',
    year: 1637,
    location: { name: 'Leiden, Netherlands', lat: 52.1601, lng: 4.4970 },
    country: 'Netherlands'
  },
  {
    id: '17',
    title: 'Album Amicorum of Anna Maria van Schurman',
    owner: 'Anna Maria van Schurman',
    year: 1641,
    location: { name: 'Utrecht, Netherlands', lat: 52.0907, lng: 5.1214 },
    country: 'Netherlands'
  },
  {
    id: '18',
    title: 'Album of Robert Boyle',
    owner: 'Robert Boyle',
    year: 1654,
    location: { name: 'Oxford, England', lat: 51.7520, lng: -1.2577 },
    country: 'England'
  },
  {
    id: '19',
    title: 'Friendship Album of Baruch Spinoza',
    owner: 'Baruch Spinoza',
    year: 1661,
    location: { name: 'Amsterdam, Netherlands', lat: 52.3676, lng: 4.9041 },
    country: 'Netherlands'
  },
  {
    id: '20',
    title: 'Album Amicorum of Gottfried Wilhelm Leibniz',
    owner: 'Gottfried Wilhelm Leibniz',
    year: 1676,
    location: { name: 'Hanover, Germany', lat: 52.3759, lng: 9.7320 },
    country: 'Germany'
  },
  {
    id: '21',
    title: 'Album of Isaac Newton',
    owner: 'Isaac Newton',
    year: 1687,
    location: { name: 'Cambridge, England', lat: 52.2053, lng: 0.1218 },
    country: 'England'
  },
  {
    id: '22',
    title: 'Album Amicorum of Maria Sibylla Merian',
    owner: 'Maria Sibylla Merian',
    year: 1699,
    location: { name: 'Amsterdam, Netherlands', lat: 52.3676, lng: 4.9041 },
    country: 'Netherlands'
  },
  {
    id: '23',
    title: 'Friendship Album of Voltaire',
    owner: 'Voltaire',
    year: 1734,
    location: { name: 'Paris, France', lat: 48.8566, lng: 2.3522 },
    country: 'France'
  },
  {
    id: '24',
    title: 'Album of Carl Linnaeus',
    owner: 'Carl Linnaeus',
    year: 1735,
    location: { name: 'Leiden, Netherlands', lat: 52.1601, lng: 4.4970 },
    country: 'Netherlands'
  },
  {
    id: '25',
    title: 'Album Amicorum of Immanuel Kant',
    owner: 'Immanuel Kant',
    year: 1781,
    location: { name: 'Königsberg, Germany', lat: 54.7104, lng: 20.4522 },
    country: 'Germany'
  },
  {
    id: '26',
    title: 'Album of Wolfgang Amadeus Mozart',
    owner: 'Wolfgang Amadeus Mozart',
    year: 1784,
    location: { name: 'Vienna, Austria', lat: 48.2082, lng: 16.3738 },
    country: 'Germany'
  },
  {
    id: '27',
    title: 'Friendship Album of Mary Wollstonecraft',
    owner: 'Mary Wollstonecraft',
    year: 1792,
    location: { name: 'London, England', lat: 51.5074, lng: -0.1278 },
    country: 'England'
  },
  {
    id: '28',
    title: 'Album Amicorum of Johann Wolfgang von Goethe',
    owner: 'Johann Wolfgang von Goethe',
    year: 1808,
    location: { name: 'Weimar, Germany', lat: 50.9795, lng: 11.3235 },
    country: 'Germany'
  },
  {
    id: '29',
    title: 'Album of Alexander von Humboldt',
    owner: 'Alexander von Humboldt',
    year: 1829,
    location: { name: 'Berlin, Germany', lat: 52.5200, lng: 13.4050 },
    country: 'Germany'
  },
  {
    id: '30',
    title: 'Friendship Album of Ada Lovelace',
    owner: 'Ada Lovelace',
    year: 1842,
    location: { name: 'London, England', lat: 51.5074, lng: -0.1278 },
    country: 'England'
  }
];
