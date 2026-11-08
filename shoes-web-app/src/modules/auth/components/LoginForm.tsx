import { useState } from 'react';
import { useAuthStore } from '../store/useAuthStore';

export const LoginForm = () => {
  // Estado para controlar qué pestaña está activa
  const [isLoginMode, setIsLoginMode] = useState(true);
  // Estados locales para los inputs
  const [formData, setFormData] = useState({
    email: '', password: '', first_name: '', last_name: '', 
    birth_date: '', street: '', city: '', country: '', zip_code: ''
  });
  
  // Extraemos las acciones y estados de nuestro store
  const { login, register, isLoading, error } = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isLoginMode) {
      await login({ email: formData.email, password: formData.password });
    } else {
      // Mapeamos el estado plano a la estructura anidada que espera FastAPI
      await register({
        first_name: formData.first_name,
        last_name: formData.last_name,
        birth_date: formData.birth_date,
        email: formData.email,
        password: formData.password,
        shipping_address: {
          street: formData.street,
          city: formData.city,
          country: formData.country,
          zip_code: formData.zip_code
        }
      });
    }
    
    if (useAuthStore.getState().isAuthenticated) {
      window.location.href = '/';
    }
  };

  return (
    <div className="flex flex-col gap-10 w-full animate-fade-in">
      
      {/* Tabs Controlados por React (más fieles a la imagen) */}
      <div className="bg-[#F3F4F6] p-1.5 rounded-full flex gap-1.5 border border-neutral-200 shadow-inner">
        <button 
          type="button"
          onClick={() => setIsLoginMode(true)}
          className={`flex-1 text-sm py-3 rounded-full transition-all duration-300 ${isLoginMode ? 'bg-white text-neutral-950 font-semibold shadow-sm' : 'text-neutral-500 font-medium hover:text-neutral-800'}`}
        >
          Iniciar sesión
        </button>
        <button 
          type="button"
          onClick={() => setIsLoginMode(false)}
          className={`flex-1 text-sm py-3 rounded-full transition-all duration-300 ${!isLoginMode ? 'bg-white text-neutral-950 font-semibold shadow-sm' : 'text-neutral-500 font-medium hover:text-neutral-800'}`}
        >
          Registrarme
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-7">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm font-medium">
            {error}
          </div>
        )}

        {/* CAMPOS DE REGISTRO (visibles si isLoginMode es false) */}
        {!isLoginMode && (
          <div className="flex flex-col gap-6 animate-fade-in">
            
            <div className="flex flex-col gap-2.5">
              <label className="text-sm font-semibold text-neutral-800">Nombre completo</label>
              <div className="grid grid-cols-2 gap-4">
                <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} placeholder="Nombre" required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
                <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} placeholder="Apellido" required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
              </div>
            </div>

            <div className="flex flex-col gap-2.5">
              <label className="text-sm font-semibold text-neutral-800">Fecha de Nacimiento</label>
              <input type="date" name="birth_date" value={formData.birth_date} onChange={handleChange} required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
            </div>

            {/* Separador sutil */}
            <div className="pt-6 border-t border-neutral-200 animate-fade-in">
              <h3 className="text-sm font-bold text-neutral-800 mb-5 tracking-tight">Dirección de Envío</h3>
              
              <div className="flex flex-col gap-5">
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-neutral-600">Calle / Carrera / Avenida</label>
                  <input type="text" name="street" value={formData.street} onChange={handleChange} placeholder="Ej: Calle 45 # 23-12" required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-neutral-600">Ciudad</label>
                    <input type="text" name="city" value={formData.city} onChange={handleChange} placeholder="Medellín" required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-neutral-600">Código Postal (opcional)</label>
                    <input type="text" name="zip_code" value={formData.zip_code} onChange={handleChange} placeholder="050010" className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
                  </div>
                </div>
                
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-neutral-600">País</label>
                  <input type="text" name="country" value={formData.country} onChange={handleChange} placeholder="Colombia" required={!isLoginMode} className="w-full bg-[#F9FAFB] border border-neutral-200 px-5 py-3.5 rounded-xl text-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-300 outline-none transition shadow-inner" />
                </div>
              </div>
            </div>
            {/* Separador final antes de email/pass */}
            <div className="border-t border-neutral-200 mt-2"></div>
          </div>
        )}

        {/* CAMPOS COMUNES (Email y Password, más fieles a la imagen) */}
        <div className="flex flex-col gap-2.5">
          <label className="text-sm font-semibold text-neutral-800">Correo electrónico</label>
          <div className="relative">
            <span className="absolute left-5 top-1/2 -translate-y-1/2 text-neutral-400">
              ✉️ </span>
            <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="tu@correo.com" required className="w-full bg-[#F9FAFB] border border-neutral-200 pl-14 pr-5 py-4.5 rounded-2xl text-base focus:ring-2 focus:ring-orange-300 focus:border-orange-400 outline-none transition shadow-inner" />
          </div>
        </div>
        
        <div className="flex flex-col gap-2.5">
          <label className="text-sm font-semibold text-neutral-800">Contraseña</label>
          <div className="relative">
            <span className="absolute left-5 top-1/2 -translate-y-1/2 text-neutral-400">
              🔒 </span>
            <input type="password" name="password" value={formData.password} onChange={handleChange} placeholder="Tu contraseña" required className="w-full bg-[#F9FAFB] border border-neutral-200 pl-14 pr-14 py-4.5 rounded-2xl text-base focus:ring-2 focus:ring-orange-300 focus:border-orange-400 outline-none transition shadow-inner" />
            <button type="button" className="absolute right-5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600">
              👁️ </button>
          </div>
        </div>
        
        {/* Botón de Acción (más grande y con estilo fiel) */}
        <button 
          type="submit" 
          disabled={isLoading} 
          className="w-full flex justify-center items-center gap-3 bg-gradient-to-r from-[#DB6F32] to-[#EE6239] text-white font-serif-nova font-black uppercase text-base tracking-widest py-6 rounded-2xl mt-5 hover:from-[#DD6D31] hover:to-[#E3663C] transition-all duration-300 shadow-button-orange active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              Procesando...
            </>
          ) : (
            <>
              {isLoginMode ? 'Iniciar sesión' : 'Crear mi cuenta'}
              <span className="text-xl leading-none">→</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};