import { createBrowserRouter } from 'react-router';
import HomePage from './pages/HomePage';
import AlbumDetailPage from './pages/AlbumDetailPage';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: HomePage,
  },
  {
    path: '/album/:albumId',
    Component: AlbumDetailPage,
  },
  {
    path: '/album/:albumId/contribution/:contributionId',
    Component: AlbumDetailPage,
  },
]);
