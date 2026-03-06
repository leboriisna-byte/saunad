'use client';

import dynamic from 'next/dynamic';

// ssr: false must live inside a client component
const SaunaViewer = dynamic(() => import('./SaunaViewer'), { ssr: false });

export default function SaunaViewerWrapper({ modelPath, bakedMaterials }) {
  return <SaunaViewer modelPath={modelPath} bakedMaterials={bakedMaterials} />;
}
