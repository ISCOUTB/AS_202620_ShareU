import { initializeApp } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged, updateProfile } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";
import { getFirestore, doc, setDoc, getDoc, collection, addDoc, getDocs, query, where, serverTimestamp, limit, updateDoc } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-firestore.js";
import { firebaseConfig, isFirebaseConfigured } from "./firebase-config.js";

let app, auth, db;
if (isFirebaseConfigured) {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
  db = getFirestore(app);
}
export { auth, db, isFirebaseConfigured, onAuthStateChanged, signOut };

export async function registerUser({ name, email, password, university = "", career = "" }) {
  const credential = await createUserWithEmailAndPassword(auth, email, password);
  await updateProfile(credential.user, { displayName: name });
  await setDoc(doc(db, "users", credential.user.uid), {
    uid: credential.user.uid, name, email, university, career,
    role: "user", createdAt: serverTimestamp()
  });
  return credential.user;
}
export async function loginUser(email, password) {
  return (await signInWithEmailAndPassword(auth, email, password)).user;
}
export async function getUserProfile(uid) {
  const snapshot = await getDoc(doc(db, "users", uid));
  return snapshot.exists() ? snapshot.data() : null;
}
const mapDocs = snapshot => snapshot.docs.map(item => ({ id: item.id, ...item.data() }));
function newestFirst(items) {
  return items.sort((a, b) => {
    const time = value => value?.toMillis ? value.toMillis() : (value instanceof Date ? value.getTime() : 0);
    return time(b.createdAt) - time(a.createdAt);
  });
}

// ShareU stores academic contributions as text and metadata only; no file uploads or Storage dependency.
export async function publishPost({ title, subject, university, career, type, content, description = "", user }) {
  const record = {
    title: title.trim(), subject: subject.trim(), university: university.trim(),
    career: career.trim(), type, content: content.trim(), description: description.trim(),
    ownerUid: user.uid, ownerName: user.displayName || user.email,
    status: "pending", createdAt: serverTimestamp()
  };
  const created = await addDoc(collection(db, "documents"), record);
  return { id: created.id, ...record };
}
export async function listApprovedDocuments() {
  const snapshot = await getDocs(query(collection(db, "documents"), where("status", "==", "approved"), limit(200)));
  return newestFirst(mapDocs(snapshot));
}
export async function listOwnDocuments(uid) {
  const snapshot = await getDocs(query(collection(db, "documents"), where("ownerUid", "==", uid), limit(200)));
  return newestFirst(mapDocs(snapshot));
}
export async function listPendingDocuments() {
  // Sort in the browser to avoid requiring a composite Firestore index for status + createdAt.
  const snapshot = await getDocs(query(collection(db, "documents"), where("status", "==", "pending"), limit(200)));
  return newestFirst(mapDocs(snapshot));
}
export async function moderateDocument(id, status) {
  if (!["approved", "rejected"].includes(status)) throw new Error("Invalid moderation status");
  await updateDoc(doc(db, "documents", id), { status, moderatedAt: serverTimestamp() });
}
