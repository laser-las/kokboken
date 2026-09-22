export type Recipe = {
  slug: string
  title: string
  time: string
  category: string
  image: string
}

export const recipes: Recipe[] = [
  { slug: 'kottbullar-med-potatismos', title: 'Köttbullar med potatismos', time: '45 min', category: 'Klassiker', image: 'https://images.unsplash.com/photo-1529042410759-befb1204b468?auto=format&fit=crop&w=900&q=85' },
  { slug: 'pasta-frutti-di-mare', title: 'Pasta frutti di mare', time: '30 min', category: 'Fisk & Skaldjur', image: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=900&q=85' },
  { slug: 'pasta-carbonara', title: 'Pasta carbonara', time: '25 min', category: 'Maträtter', image: 'https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=900&q=85' },
  { slug: 'ortfile-med-rostad-potatis', title: 'Örtfilé med rostad potatis', time: '1 h 15 min', category: 'Maträtter', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=85' },
]
