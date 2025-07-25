import React from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import ChatBot from './ChatBot';
import { useState } from 'react';

const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();
  const [chatOpen, setChatOpen] = useState(false);

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex items-center space-x-2">
      <button
        aria-label="Open ChatBot"
        className="rounded-full p-2 bg-muted hover:bg-primary/10 text-2xl focus:outline-none focus:ring-2 focus:ring-primary"
        onClick={() => setChatOpen(true)}
        style={{ marginRight: 8 }}
      >
        💬
      </button>
      <ChatBot open={chatOpen} onClose={() => setChatOpen(false)} />
      <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg px-3 py-2">
        <Globe className="w-4 h-4 text-muted-foreground" />
        <select
          value={i18n.language}
          onChange={(e) => changeLanguage(e.target.value)}
          className="border-none bg-transparent text-sm text-foreground focus:outline-none"
          aria-label="Select language"
        >
          <option value="en">English</option>
          <option value="hi">हिंदी</option>
          <option value="ta">தமிழ்</option>
          <option value="kn">ಕನ್ನಡ</option>
          <option value="te">తెలుగు</option>
        </select>
      </div>
    </div>
  );
};

export default LanguageSelector; 