import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const NoiseMapOverlay = ({ interpolatedData, opacity = 0.6 }) => {
  const map = useMap();
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!map || !interpolatedData || !interpolatedData.interpolated_grid) {
      console.log('🔍 NoiseMapOverlay: Missing data or map', { 
        hasMap: !!map, 
        hasData: !!interpolatedData, 
        hasGrid: !!(interpolatedData && interpolatedData.interpolated_grid)
      });
      return;
    }

    // Remove existing overlay
    if (overlayRef.current) {
      try {
        map.removeLayer(overlayRef.current);
        console.log('🗑️ Removed previous overlay');
      } catch (error) {
        console.warn('Error removing overlay:', error);
      }
    }

    const { bounds, grid_size, values, min_db, max_db } = interpolatedData.interpolated_grid;
    
    console.log(`🎨 Creating overlay: ${grid_size[0]}x${grid_size[1]} grid, dB range: ${min_db.toFixed(1)}-${max_db.toFixed(1)}`);
    console.log('📍 Overlay bounds:', bounds);
    console.log(`📐 Bounds details: SW(${bounds[0][0].toFixed(3)}, ${bounds[0][1].toFixed(3)}) to NE(${bounds[1][0].toFixed(3)}, ${bounds[1][1].toFixed(3)})`);
    
    // Verify bounds orientation for Leaflet
    const [[south, west], [north, east]] = bounds;
    if (south > north) {
      console.warn('⚠️ Latitude bounds may be reversed! South > North');
    }
    if (west > east) {
      console.warn('⚠️ Longitude bounds may be reversed! West > East');
    }
    
    // Create canvas for heat map
    const canvas = document.createElement('canvas');
    canvas.width = grid_size[0];
    canvas.height = grid_size[1];
    const ctx = canvas.getContext('2d');
    
    // Create image data
    const imageData = ctx.createImageData(grid_size[0], grid_size[1]);
    const data = imageData.data;
    
    // Enhanced color mapping function with better gradient transitions
    const getColor = (value) => {
      // Handle edge cases
      if (min_db === max_db) {
        // All sensors have the same value, use a neutral color
        return [100, 150, 100, Math.floor(opacity * 180)];
      }
      
      const normalized = Math.max(0, Math.min(1, (value - min_db) / (max_db - min_db)));
      
      let r, g, b;
      
      if (normalized <= 0.2) {
        // Very quiet - Green to Light Green
        const t = normalized / 0.2;
        r = Math.floor(76 + (139 - 76) * t);
        g = Math.floor(175 + (195 - 175) * t);
        b = Math.floor(80 + (57 - 80) * t);
      } else if (normalized <= 0.4) {
        // Quiet to Moderate - Light Green to Yellow-Green
        const t = (normalized - 0.2) / 0.2;
        r = Math.floor(139 + (205 - 139) * t);
        g = Math.floor(195 + (220 - 195) * t);
        b = Math.floor(57 + (57 - 57) * t);
      } else if (normalized <= 0.6) {
        // Moderate to Noticeable - Yellow-Green to Yellow
        const t = (normalized - 0.4) / 0.2;
        r = Math.floor(205 + (255 - 205) * t);
        g = Math.floor(220 + (235 - 220) * t);
        b = Math.floor(57 + (59 - 57) * t);
      } else if (normalized <= 0.8) {
        // Noticeable to Loud - Yellow to Orange
        const t = (normalized - 0.6) / 0.2;
        r = Math.floor(255 + (255 - 255) * t);
        g = Math.floor(235 + (152 - 235) * t);
        b = Math.floor(59 + (0 - 59) * t);
      } else {
        // Loud to Very Loud - Orange to Red
        const t = (normalized - 0.8) / 0.2;
        r = Math.floor(255 + (244 - 255) * t);
        g = Math.floor(152 + (67 - 152) * t);
        b = Math.floor(0 + (54 - 0) * t);
      }
      
      // Apply transparency based on opacity setting - more opaque for better visibility
      const alpha = Math.floor(opacity * 220);
      
      return [r, g, b, alpha];
    };
    
    // Fill image data with smoother interpolation
    for (let i = 0; i < values.length; i++) {
      const color = getColor(values[i]);
      const pixelIndex = i * 4;
      data[pixelIndex] = color[0];     // Red
      data[pixelIndex + 1] = color[1]; // Green
      data[pixelIndex + 2] = color[2]; // Blue
      data[pixelIndex + 3] = color[3]; // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
    
    // Apply smoothing filter for better visualization
    ctx.filter = 'blur(3px)';
    ctx.drawImage(canvas, 0, 0);
    
    // Create Leaflet image overlay with enhanced options
    const imageOverlay = L.imageOverlay(canvas.toDataURL(), bounds, {
      opacity: opacity,
      interactive: false,
      crossOrigin: 'anonymous',
      className: 'noise-heatmap-overlay'
    });
    
    imageOverlay.addTo(map);
    overlayRef.current = imageOverlay;
    
    console.log('✅ Heat map overlay added to map');

  }, [map, interpolatedData, opacity]);

  useEffect(() => {
    return () => {
      if (overlayRef.current && map && map.removeLayer) {
        try {
          map.removeLayer(overlayRef.current);
        } catch (error) {
          console.warn('Error removing overlay on cleanup:', error);
        }
      }
    };
  }, [map]);

  return null;
};

export default NoiseMapOverlay;
