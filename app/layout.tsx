import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'PlasticProspector B2B | Prospecção IA de Indústrias de Embalagens Plásticas',
  description: 'Plataforma SaaS para prospecção inteligente de fabricantes de frascos, bisnagas, potes e tampas plásticas com Gemini 2.5 Flash.',
  keywords: 'prospecção b2b, embalagens plásticas, fabricantes pead pet, prospecção de indústrias, gemini ai b2b',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="bg-[#090d16] text-slate-100 min-h-screen selection:bg-cyan-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
