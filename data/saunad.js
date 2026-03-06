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
    model: '/models/sauna_model.glb',
    specs: [
      { label: 'Välisdiameeter', value: '2.4 m' },
      { label: 'Siseruumi kõrgus', value: '1.9 m' },
      { label: 'Pikkus', value: '3.0 – 6.0 m (valik)' },
      { label: 'Seina paksus', value: '44 mm' },
      { label: 'Puit', value: 'Kuusk' },
      { label: 'Katus', value: 'Asfalt katusekivid' },
    ],
  },
];

export function getSauna(slug) {
  return saunad.find((s) => s.slug === slug) ?? null;
}
