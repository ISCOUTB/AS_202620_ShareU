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
  return (
    <html lang="es">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
