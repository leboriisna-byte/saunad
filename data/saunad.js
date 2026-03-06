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
  },
];

export function getSauna(slug) {
  return saunad.find((s) => s.slug === slug) ?? null;
}
