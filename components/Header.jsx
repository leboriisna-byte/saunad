'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

export default function Header({ saunad }) {
  const pathname = usePathname();

  return (
    <header className="top-bar">
      <div className="logo">
        <Link href="/">
          <Image src="/Group.svg" alt="Tesler Grupp" width={120} height={40} style={{ filter: 'brightness(0) invert(1)' }} />
        </Link>
      </div>
      <nav className="nav-links">
        {saunad.map((s) => (
          <Link
            key={s.slug}
            href={`/saunad/${s.slug}`}
            className={`nav-link${pathname === `/saunad/${s.slug}` ? ' active' : ''}`}
          >
            {s.label}
          </Link>
        ))}
      </nav>
      <div className="header-actions">
        <a href="#" className="contact-link">Kontakt</a>
      </div>
    </header>
  );
}
