import "./globals.css";
import type { ReactNode } from "react";
import { AuthProvider } from "@/lib/auth";

export const metadata = {
  title: "ShareU — material académico compartido",
  description: "Apuntes, talleres y parciales por universidad, carrera y materia.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  const apiUrl =
    process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  return (
    <html lang="es">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__SHAREU_API_URL = ${JSON.stringify(apiUrl)};`,
          }}
        />
      </head>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
