import { useState } from 'react';

interface Props {
  images: string[];
  productName: string;
}

export const ImageGallery = ({ images, productName }: Props) => {
  // Aseguramos tener al menos la imagen por defecto
  const safeImages = images.length > 0 ? images : ['/placeholder-shoe.png'];
  
  // Estado para la imagen principal (por defecto la primera, índice 0)
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  return (
    <div className="flex flex-col gap-4">
      {/* Imagen Principal (Estado-dependiente) */}
      <div className="bg-[#1a1a1a] rounded-2xl overflow-hidden aspect-square border border-neutral-800">
        <img 
          src={safeImages[selectedImageIndex]} 
          alt={productName} 
          className="w-full h-full object-cover transition-opacity duration-300"
        />
      </div>
      
      {/* Miniaturas (4 como máximo, excluyendo la principal si prefieres, 
          o las 5 incluyendo la principal. Aquí usaremos todas). */}
      {safeImages.length > 1 && (
        <div className="grid grid-cols-5 gap-4">
          {safeImages.slice(0, 5).map((img, index) => (
            <div 
              key={index}
              onClick={() => setSelectedImageIndex(index)} // <-- ¡Aquí está la magia!
              className={`bg-[#1a1a1a] rounded-xl overflow-hidden aspect-square border-2 cursor-pointer transition-all ${
                index === selectedImageIndex 
                  ? 'border-orange-500 scale-105' 
                  : 'border-neutral-800 hover:border-neutral-600'
              }`}
            >
              <img src={img} alt={`Vista de ${productName}`} className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};