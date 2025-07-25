import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import '@ui5/webcomponents/dist/Assets.js';
import '@ui5/webcomponents-fiori/dist/Assets.js';
import '@ui5/webcomponents-icons/dist/Assets.js';

createRoot(document.getElementById("root")!).render(<App />);
