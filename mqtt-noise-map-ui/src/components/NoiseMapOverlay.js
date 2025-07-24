import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

const NoiseMapOverlay = ({ map, interpolatedData, opacity = 0.6 }) => {
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!map || !interpolatedData || !interpolatedData.interpolated_grid) {
      return;
    }

    // Remove existing overlay
    if (overlayRef.current) {
      map.removeLayer(overlayRef.current);
    }

    const { bounds, grid_size, values, min_db, max_db } = interpolatedData.interpolated_grid;
    
    // Create canvas for heat map
    const canvas = document.createElement('canvas');
    canvas.width = grid_size[0];
    canvas.height = grid_size[1];
    const ctx = canvas.getContext('2d');
    
    // Create image data
    const imageData = ctx.createImageData(grid_size[0], grid_size[1]);
    const data = imageData.data;
    
    // Color mapping function
    const getColor = (value) => {
      const normalized = (value - min_db) / (max_db - min_db);
      
      if (normalized <= 0.33) {
        // Green to Yellow
        const r = Math.floor(normalized * 3 * 255);
        const g = 255;
        const b = 0;
        return [r, g, b, Math.floor(opacity * 255)];
      } else if (normalized <= 0.66) {
        // Yellow to Red
        const r = 255;
        const g = Math.floor((1 - (normalized - 0.33) * 3) * 255);
        const b = 0;
        return [r, g, b, Math.floor(opacity * 255)];
      } else {
        // Red to Dark Red
        const r = Math.floor((1 - (normalized - 0.66) * 1.5) * 255 + 128);
        const g = 0;
        const b = 0;
        return [r, g, b, Math.floor(opacity * 255)];
      }
    };
    
    // Fill image data
    for (let i = 0; i < values.length; i++) {
      const color = getColor(values[i]);
      const pixelIndex = i * 4;
      data[pixelIndex] = color[0];     // Red
      data[pixelIndex + 1] = color[1]; // Green
      data[pixelIndex + 2] = color[2]; // Blue
      data[pixelIndex + 3] = color[3]; // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
    
    // Create Leaflet image overlay
    const imageOverlay = L.imageOverlay(canvas.toDataURL(), bounds, {
      opacity: opacity
    });
    
    imageOverlay.addTo(map);
    overlayRef.current = imageOverlay;

  }, [map, interpolatedData, opacity]);

  useEffect(() => {
    return () => {
      if (overlayRef.current && map) {
        map.removeLayer(overlayRef.current);
      }
    };
  }, [map]);

  return null;
};

export default NoiseMapOverlay;
