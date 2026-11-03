// Configuración web de Firebase para ShareU.
// No se utiliza Firebase Storage. Mantén las reglas de Firestore y Authentication seguras.
export const firebaseConfig = {
  apiKey: "AIzaSyCqW1eltZJ_Xo0ks3_eF9tpJsfCny0oUGg",
  authDomain: "shareu-96e84.firebaseapp.com",
  projectId: "shareu-96e84",
  storageBucket: "shareu-96e84.firebasestorage.app",
  messagingSenderId: "552313986658",
  appId: "1:552313986658:web:b337efb3028b33371bfb3b",
  measurementId: "G-X6J37P0WDH"
};

export const isFirebaseConfigured =
  Boolean(firebaseConfig.apiKey) &&
  !firebaseConfig.apiKey.includes("REEMPLAZAR") &&
  Boolean(firebaseConfig.authDomain) &&
  Boolean(firebaseConfig.projectId) &&
  Boolean(firebaseConfig.appId);
