export const saunad = [
  {
    slug: 'vaike-delux',
    name: 'Väike Delux',
    size: '2.4m',
    label: 'Väike Delux 2.4m',
    description:
      'Luksus loodi nautimiseks, nagu ka hea kuum leil ja külmad karastusjoogid. Delux saunas saad nautida mõlemat ja tunda end nagu vana roomlane legendaarsetes Caracalla termides.',
    price: '4,030.00€',
    priceIncVat: '780.00€',
    priceExVat: '3,250.00€',
    model: '/models/VäikeDelux2.4m.glb',
    bakedMaterials: true,
    specs: [
      { label: 'Välisdiameeter', value: '2.4 m' },
      { label: 'Siseruumi kõrgus', value: '1.9 m' },
      { label: 'Pikkus', value: '3.0 – 6.0 m (valik)' },
      { label: 'Seina paksus', value: '44 mm' },
      { label: 'Puit', value: 'Kuusk' },
      { label: 'Katus', value: 'Asfalt katusekivid' },
    ],
  },
  {
    slug: 'barrel-klassik',
    name: 'Barrel Klassik',
    size: '3.3m',
    label: 'Barrel Klassik 3.3m',
    description:
      'Klassikaline tünnisaun, mis sobib ideaalselt nii pere- kui ka sõprade koosviibimisteks. Tugev ja vastupidav konstruktsioon tagab soojapidavuse ja pikaajalise kasutuse.',
    price: '3,500.00€',
    priceIncVat: '677.50€',
    priceExVat: '2,822.50€',
    model: '/models/sauna_model.glb',
    bakedMaterials: false,
    specs: [
      { label: 'Välisdiameeter', value: '2.05 m' },
      { label: 'Siseruumi kõrgus', value: '1.65 m' },
      { label: 'Pikkus', value: '3.3 m' },
      { label: 'Seina paksus', value: '44 mm' },
      { label: 'Puit', value: 'Kuusk' },
      { label: 'Katus', value: 'Asfalt katusekivid' },
    ],
  },
];

export function getSauna(slug) {
  return saunad.find((s) => s.slug === slug) ?? null;
}
