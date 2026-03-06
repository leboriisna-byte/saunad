export default function ProductCard({ sauna }) {
  return (
    <div className="bottom-ui">
      <div className="product-info">
        <h1>
          {sauna.name} ({sauna.size})
        </h1>
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
        <button className="icon-btn" title="Mõõdud">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </button>
        <button className="icon-btn" title="Jaga">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
          </svg>
        </button>
        <button className="icon-btn" title="Täisekraan" id="fullscreen-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
          </svg>
        </button>
      </div>
    </div>
  );
}
