import { notFound } from 'next/navigation';
import { getSauna, saunad } from '@/data/saunad';
import ProductCard from '@/components/ProductCard';
import SaunaViewerWrapper from '@/components/SaunaViewerWrapper';

export async function generateStaticParams() {
  return saunad.map((s) => ({ slug: s.slug }));
}

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const sauna = getSauna(slug);
  if (!sauna) return {};
  return {
    title: `${sauna.name} (${sauna.size}) — Tesler Sauna`,
    description: sauna.description,
  };
}

export default async function SaunaPage({ params }) {
  const { slug } = await params;
  const sauna = getSauna(slug);
  if (!sauna) notFound();

  return (
    <>
      <SaunaViewerWrapper modelPath={sauna.model} bakedMaterials={sauna.bakedMaterials} />
      <ProductCard sauna={sauna} />
    </>
  );
}
