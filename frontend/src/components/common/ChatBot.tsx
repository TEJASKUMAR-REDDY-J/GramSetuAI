import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { geminiChatService, ChatMessage } from '../../services/geminiService';

const ChatBot: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { from: 'bot', text: 'Hi! I am Vrishabh, your GramSetu assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, open]);

  if (!open) return null;

  const chatWidget = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all">
      <div className="relative w-full max-w-2xl max-h-[85vh] h-[70vh] min-w-[400px] min-h-[500px] flex flex-col rounded-3xl shadow-2xl border border-white/10 bg-gradient-to-br from-white/30 via-background/80 to-muted/40 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 rounded-t-3xl border-b border-white/10 bg-gradient-to-r from-primary/80 to-primary/60 text-primary-foreground shadow-sm">
          <span className="font-bold text-lg tracking-wide flex items-center gap-3">
            <img 
              src="/Chatbot.jpeg" 
              alt="Vrishabh" 
              className="w-12 h-12 rounded-full object-cover border-2 border-white/30"
            />{' '}
            Chat with Vrishabh
          </span>
          <button
            onClick={onClose}
            className="text-2xl font-bold text-white/80 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary rounded-full px-2 transition-colors"
            aria-label="Close chat"
          >
            ×
          </button>
        </div>
        {/* Chat area */}
        <div
          ref={chatRef}
          className="flex-1 overflow-y-auto p-6 space-y-4 bg-background min-h-0"
        >
        {messages.map((msg, idx) => (
          <div key={`${msg.from}-${idx}`} className={`flex ${msg.from === 'bot' ? 'justify-start' : 'justify-end'}`}>
            {msg.from === 'bot' && (
              <div className="flex-shrink-0 mr-3 mt-1">
                <img 
                  src="/Chatbot.jpeg" 
                  alt="Vrishabh" 
                  className="w-12 h-12 rounded-full object-cover border-2 border-white/50"
                />
              </div>
            )}
            <div
              className={`px-5 py-3 max-w-[70%] rounded-2xl shadow-md transition-all text-base whitespace-pre-line ${
                msg.from === 'bot'
                  ? 'bg-white/95 text-gray-800 border border-gray-200 rounded-bl-2'
                  : 'bg-blue-600 text-white border border-blue-500 rounded-br-2'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex-shrink-0 mr-3 mt-1">
              <img 
                src="/Chatbot.jpeg" 
                alt="Vrishabh" 
                className="w-12 h-12 rounded-full object-cover border-2 border-white/50"
              />
            </div>
            <div className="px-5 py-3 max-w-[70%] rounded-2xl shadow-md bg-white/95 text-gray-800 border border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:100ms]"></div>
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:200ms]"></div>
                </div>
                <span className="text-sm text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        </div>
        {/* Input area */}
        <form
          className="flex items-center gap-3 p-4 border-t border-white/10 bg-white/60 rounded-b-3xl backdrop-blur-md"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!input.trim() || isLoading) return;
            
            const userMessage = input.trim();
            setInput('');
            setIsLoading(true);
            
            // Add user message
            setMessages(prev => [...prev, { from: 'user', text: userMessage }]);
            
            try {
              // Get AI response
              const botResponse = await geminiChatService.sendMessage(userMessage);
              setMessages(prev => [...prev, { from: 'bot', text: botResponse }]);
            } catch (error) {
              console.error('Error getting AI response:', error);
              setMessages(prev => [...prev, { 
                from: 'bot', 
                text: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.' 
              }]);
            } finally {
              setIsLoading(false);
            }
          }}
        >
          <input
            className="flex-1 px-4 py-2 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-primary bg-white/90 text-gray-800 placeholder:text-gray-500 shadow-sm transition-all"
            placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={isLoading}
            autoFocus
            aria-label="Type your message"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-5 py-2 rounded-xl bg-primary text-primary-foreground font-semibold shadow-md hover:bg-primary/80 transition-colors focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Send message"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );

  return createPortal(chatWidget, document.body);
};

export default ChatBot; 