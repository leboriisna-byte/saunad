'use client';

import { useState } from 'react';

export default function ProductCard({ sauna }) {
  const [specsOpen, setSpecsOpen] = useState(false);

  function handleShare() {
    if (navigator.share) {
      navigator.share({ title: `${sauna.name} (${sauna.size})`, url: window.location.href });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Link kopeeritud!');
    }
  }

  function handleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  return (
    <>
      {/* Specs panel — centered above the model */}
      {specsOpen && (
        <div className="specs-panel">
          <div className="specs-header">
            <span>Mõõdud ja spetsifikatsioonid</span>
            <button className="specs-close" onClick={() => setSpecsOpen(false)}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <div className="specs-grid">
            {sauna.specs.map((s) => (
              <div key={s.label} className="specs-row">
                <span className="specs-label">{s.label}</span>
                <span className="specs-value">{s.value}</span>
              </div>
            ))}
          </div>
          <div className="specs-arrow" />
        </div>
      )}

      <div className="bottom-ui">
        <div className="product-info">
          <h1>{sauna.name} ({sauna.size})</h1>
          <p className="product-desc">{sauna.description}</p>
          <div className="price-container">
            <span className="price-label">Alates:</span>
            <span className="price">{sauna.price}</span>
            <span className="vat">
              (sis. KM {sauna.priceIncVat} | ilma KM-ita {sauna.priceExVat})
            </span>
          </div>
        </div>

        <div className="action-buttons">
          {/* Dimensions */}
          <button className={`icon-btn${specsOpen ? ' active' : ''}`} title="Mõõdud" onClick={() => setSpecsOpen((o) => !o)}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 6h18M3 12h18M3 18h18" />
              <path d="M6 3v3M12 3v3M18 3v3" />
            </svg>
          </button>

          {/* Share */}
          <button className="icon-btn" title="Jaga" onClick={handleShare}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
          </button>

          {/* Fullscreen */}
          <button className="icon-btn" title="Täisekraan" onClick={handleFullscreen}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 3 21 3 21 9" />
              <polyline points="9 21 3 21 3 15" />
              <line x1="21" y1="3" x2="14" y2="10" />
              <line x1="3" y1="21" x2="10" y2="14" />
            </svg>
          </button>
        </div>
      </div>
    </>
  );
}
