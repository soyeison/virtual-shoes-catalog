import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';

export const AuthWidget = () => {
  const [isMounted, setIsMounted] = useState(false);
  
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useAuthStore((state) => state.logout);

  // useEffect solo corre en el navegador, nunca en el servidor de Astro
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleLogout = () => {
    logout();
    window.location.href = '/'; // Redirige al inicio y recarga la aplicación
  };

  if (!isMounted) {
    return <div className="w-[45px] h-[20px]"></div>; 
  }

  // Si el usuario tiene un token válido en localStorage
  if (isAuthenticated) {
    return (
      <button 
        onClick={handleLogout}
        className="text-sm font-bold uppercase tracking-widest text-neutral-400 hover:text-red-500 transition-colors"
      >
        Salir
      </button>
    );
  }

  // Si es un visitante
  return (
    <a 
      href="/login"
      className="text-sm font-bold uppercase tracking-widest hover:text-orange-500 transition-colors"
    >
      Login
    </a>
  );
};