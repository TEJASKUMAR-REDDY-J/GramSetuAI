import { GoogleGenerativeAI } from '@google/generative-ai';

// Note: In production, this should be stored in environment variables
// For development, you can replace this with your actual API key
const API_KEY = import.meta.env.VITE_GEMINI_API_KEY ?? 'your-gemini-api-key-here';

const genAI = new GoogleGenerativeAI(API_KEY);

export interface ChatMessage {
  from: 'user' | 'bot';
  text: string;
}

export class GeminiChatService {
  private readonly model: any;
  private chat: any;

  constructor() {
    this.model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    this.initializeChat();
  }

  private initializeChat() {
    const context = `You are Vrishabh, a helpful AI assistant for a microfinance platform called GramSetu. 
    You help users with:
    - Understanding loan processes and requirements
    - Credit score information and improvement tips
    - Financial literacy and advice
    - Platform navigation and features
    - General banking and financial questions
    
    Your name is Vrishabh (which means "bull" in Sanskrit), representing strength and reliability in finance.
    Keep responses helpful, concise, and focused on financial services and microfinance topics.
    Be empathetic and understanding of users who may be new to formal banking.`;

    this.chat = this.model.startChat({
      history: [
        {
          role: 'user',
          parts: [{ text: context }]
        },
        {
          role: 'model',
          parts: [{ text: 'Hello! I\'m Vrishabh, your GramSetu assistant. I\'m here to help you with all your microfinance and banking questions. How can I assist you today?' }]
        }
      ],
      generationConfig: {
        maxOutputTokens: 1000,
        temperature: 0.7,
      },
    });
  }

  async sendMessage(message: string): Promise<string> {
    try {
      if (!API_KEY || API_KEY === 'your-gemini-api-key-here') {
        return `I'm currently in demo mode. To enable AI responses, please add your Gemini API key to the environment variables as VITE_GEMINI_API_KEY.

For your question: "${message}"

Here's a helpful response: I'm here to help with microfinance, loans, credit scores, and financial guidance. Feel free to ask about loan applications, eligibility criteria, or any financial advice you need!`;
      }

      console.log('Sending message to Gemini:', message);
      const result = await this.chat.sendMessage(message);
      const response = await result.response;
      const text = response.text();
      console.log('Gemini response:', text);
      return text;
    } catch (error) {
      console.error('Detailed Gemini API error:', error);
      
      // Check if it's an API key issue
      if (error instanceof Error) {
        if (error.message.includes('API_KEY_INVALID') || error.message.includes('403')) {
          return 'It looks like there\'s an issue with the API key. Please check that your Gemini API key is valid and has the necessary permissions.';
        }
        if (error.message.includes('quota') || error.message.includes('limit')) {
          return 'The API quota has been exceeded. Please try again later or check your Google Cloud billing settings.';
        }
        if (error.message.includes('network') || error.message.includes('fetch')) {
          return 'There\'s a network connectivity issue. Please check your internet connection and try again.';
        }
      }
      
      return 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment, or contact our support team for assistance.';
    }
  }

  resetChat() {
    this.initializeChat();
  }
}

export const geminiChatService = new GeminiChatService();
