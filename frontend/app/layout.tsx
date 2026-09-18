import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Bryle — grounded answers",
  description: "Ask questions and get answers grounded in an indexed website.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
