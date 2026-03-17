import './globals.css';

export const metadata = {
  title: 'Conversational Dashboard',
  description: 'Ask questions about your data in natural language',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
