import { Navigate } from 'react-router-dom';

export function HomeScreen() {
  return <Navigate to="/conversation" replace />;
}
