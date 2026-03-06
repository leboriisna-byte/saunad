import { Outfit } from 'next/font/google';
import Header from '@/components/Header';
import { saunad } from '@/data/saunad';
import '@/styles/globals.css';

const outfit = Outfit({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-outfit',
});

export const metadata = {
  title: 'Tesler Sauna',
  description: 'Tesleri saunamajad — kvaliteet ja luksus.',
  icons: {
    icon: '/Group-100x100.webp',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="et" className={outfit.variable}>
      <body>
        <div id="app">
          <Header saunad={saunad} />
          {children}
        </div>
      </body>
    </html>
  );
}
