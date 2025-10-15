// // Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// // TODO: Add SDKs for Firebase products that you want to use
// // https://firebase.google.com/docs/web/setup#available-libraries

// // Your web app's Firebase configuration
// // For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: "AIzaSyDrTIHcCpcUlCqqTVixyc_UVMmBw1zS8uk",
//   authDomain: "smart-help-desk-88a76.firebaseapp.com",
//   projectId: "smart-help-desk-88a76",
//   storageBucket: "smart-help-desk-88a76.firebasestorage.app",
//   messagingSenderId: "414409571847",
//   appId: "1:414409571847:web:dea305b685f9f4e9f874a2",
//   measurementId: "G-FQ6BPMLMLD"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional

// apiKey: "AIzaSyDrTIHcCpcUlCqqTVixyc_UVMmBw1zS8uk",
//   authDomain: "smart-help-desk-88a76.firebaseapp.com",
//   projectId: "smart-help-desk-88a76",
//   storageBucket: "smart-help-desk-88a76.firebasestorage.app",
//   messagingSenderId: "414409571847",
//   appId: "1:414409571847:web:dea305b685f9f4e9f874a2",
//   measurementId: "G-FQ6BPMLMLD"
const firebaseConfig = {
  apiKey: "AIzaSyDrTIHcCpcUlCqqTVixyc_UVMmBw1zS8uk",
  authDomain: "smart-help-desk-88a76.firebaseapp.com",
  projectId: "smart-help-desk-88a76",
  storageBucket: "smart-help-desk-88a76.firebasestorage.app",
  messagingSenderId: "414409571847",
  appId: "1:414409571847:web:dea305b685f9f4e9f874a2",
  measurementId: "G-FQ6BPMLMLD"
};  

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app)