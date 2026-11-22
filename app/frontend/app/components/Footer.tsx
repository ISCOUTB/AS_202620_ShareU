import Link from "next/link";

export default function Footer() {
  return (
    <footer className="site-footer">
      <Link className="footer-brand" href="/">
        shareU<span>.</span>
      </Link>
      <span>Un espacio para aprender juntos.</span>
      <span>Hecho con ✿ para la comunidad estudiantil</span>
    </footer>
  );
}
