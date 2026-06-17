import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface ImageCarouselProps {
  images: string[];
}

export function ImageCarousel({ images }: ImageCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    setCurrentIndex(0);
  }, [images]);

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) => (prevIndex === 0 ? images.length - 1 : prevIndex - 1));
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex === images.length - 1 ? 0 : prevIndex + 1));
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  return (
    <div className="relative w-full h-full bg-card border border-border rounded-lg overflow-hidden shadow-sm">
      {/* Main Image */}
      <div className="relative w-full h-full">
        <img
          src={images[currentIndex]}
          alt={`Scan ${currentIndex + 1}`}
          className="w-full h-full object-contain bg-accent/20"
        />

        {/* Navigation Arrows */}
        {images.length > 1 && (
          <>
            <button
              onClick={goToPrevious}
              className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-background/90 hover:bg-background border border-border rounded-full flex items-center justify-center shadow-lg transition-all"
              aria-label="Previous image"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={goToNext}
              className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-background/90 hover:bg-background border border-border rounded-full flex items-center justify-center shadow-lg transition-all"
              aria-label="Next image"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </>
        )}

        {/* Image Counter */}
        <div className="absolute top-4 right-4 px-3 py-1.5 bg-background/90 border border-border rounded-full text-sm">
          {currentIndex + 1} / {images.length}
        </div>
      </div>

      {/* Thumbnail Navigation */}
      {images.length > 1 && (
        <div className="absolute bottom-0 left-0 right-0 bg-background/95 border-t border-border p-4">
          <div className="flex gap-2 overflow-x-auto pb-2">
            {images.map((image, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`flex-shrink-0 w-16 h-16 rounded border-2 transition-all overflow-hidden ${
                  index === currentIndex
                    ? 'border-secondary shadow-md'
                    : 'border-border hover:border-secondary/50'
                }`}
              >
                <img
                  src={image}
                  alt={`Thumbnail ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
