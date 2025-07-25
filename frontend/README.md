# GramSetu - Rural Finance Platform Frontend

## 🌾 About GramSetu

GramSetu is a comprehensive rural finance platform designed to connect farmers and rural communities with microfinance institutions. The platform facilitates loan applications, credit scoring, and financial inclusion for agricultural and rural development purposes.

## 💰 Currency Support

This application is fully localized for the Indian market with:
- **Currency**: All amounts displayed in Indian Rupees (₹)
- **Context**: Agricultural and rural loan purposes
- **Language Support**: English, Hindi, Kannada, Tamil, and Telugu

## 🚀 Quick Start

### Option 1: Using the Shell Script (Recommended)
```bash
# Make sure you're in the frontend directory
cd frontend

# Run the startup script
./start-server.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env file to add your Gemini API key

# Start development server
npm run dev
```

## 🌐 Project Info

**Repository**: GramSetu - Rural Finance Platform  
**Type**: SAP Hackfest Submission  
**Focus**: Rural Financial Inclusion for India

## ✨ Features

- **Multi-language Support**: Available in English, Hindi, Kannada, Tamil, and Telugu
- **Dark/Light Mode**: Full theme support with proper contrast and accessibility
- **Loan Management**: Application submission, tracking, and history
- **Credit Scoring**: AI-powered credit assessment with Gemini integration
- **Chat Assistant**: AI chatbot "Vrishabh" for customer support
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live status updates for loan applications
- **Indian Context**: Tailored for rural and agricultural financing needs

## 🛠️ Technologies Used

This project is built with:

- **Frontend Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: Redux Toolkit
- **Routing**: React Router v6
- **Internationalization**: react-i18next
- **AI Integration**: Google Gemini API
- **Icons**: Lucide React (including IndianRupee icon)
- **Animations**: Framer Motion
- **Form Handling**: React Hook Form
- **Charts**: Recharts
- **Notifications**: Sonner

## 📱 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:dev` - Build for development
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build
- `./start-server.sh` - Automated startup script (recommended)
- `./build.sh` - Automated production build script

## 🔧 Environment Setup

Create a `.env` file in the frontend directory:

```env
VITE_GEMINI_API_KEY=your_gemini_api_key_here
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── common/      # Common components (Layout, ChatBot, etc.)
│   │   ├── forms/       # Form components (LoanApplicationForm)
│   │   └── ui/          # shadcn/ui components (button, card, dialog, etc.)
│   ├── pages/           # Page components (Dashboard, Login, Register, Profile)
│   ├── services/        # API services and external integrations
│   ├── store/           # Redux store and slices
│   │   └── slices/      # Redux slices for state management
│   ├── types/           # TypeScript type definitions
│   ├── i18n/            # Internationalization setup
│   │   ├── index.ts     # i18n configuration
│   │   └── locales/     # Translation files (en.json, hi.json, kn.json, ta.json, te.json)
│   ├── hooks/           # Custom React hooks (use-mobile, use-toast)
│   ├── lib/             # Utility functions (utils.ts)
│   ├── App.tsx          # Main App component
│   ├── main.tsx         # Application entry point
│   ├── App.css          # Global styles
│   ├── index.css        # Tailwind CSS imports
│   └── vite-env.d.ts    # Vite environment types
├── public/              # Static assets
│   ├── Chatbot.jpeg     # Chatbot avatar image
│   ├── favicon.ico      # Website favicon
│   └── robots.txt       # SEO robots file
├── dist/                # Built files (generated after build)
├── node_modules/        # Dependencies (generated after npm install)
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── start-server.sh      # Development server startup script
├── build.sh             # Production build script
├── package.json         # Project dependencies and scripts
├── package-lock.json    # Locked dependency versions
├── vite.config.ts       # Vite configuration
├── tailwind.config.ts   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
├── eslint.config.js     # ESLint configuration
├── tsconfig.json        # TypeScript configuration
├── tsconfig.app.json    # TypeScript app-specific config
├── tsconfig.node.json   # TypeScript Node.js config
├── components.json      # shadcn/ui configuration
├── index.html           # HTML template
└── README.md           # This file
```

## 🌍 Internationalization

The app supports 5 languages with complete translations:
- **English** (en)
- **Hindi** (hi) - हिंदी
- **Kannada** (kn) - ಕನ್ನಡ
- **Tamil** (ta) - தமிழ்
- **Telugu** (te) - తెలుగు

All UI text, including dashboard subtitles, form labels, and button text, is fully translated.

## 🎨 Theming

- **Light Mode**: Clean, bright interface for daylight usage
- **Dark Mode**: Eye-friendly dark theme with proper contrast
- **Automatic Detection**: Respects system preference
- **Manual Toggle**: Users can override system settings

## 📈 Recent Updates

### Currency Localization
- ✅ All amounts displayed in Indian Rupees (₹)
- ✅ Replaced DollarSign icon with IndianRupee icon
- ✅ Updated loan purposes for agricultural context
- ✅ Indian names and document types in dummy data

### UI/UX Improvements
- ✅ Fixed dark mode support in loan application form
- ✅ Internationalized all dashboard subtitle text
- ✅ Improved chat modal positioning and visibility
- ✅ Enhanced credit score card dark mode styling

### Developer Experience
- ✅ Added automated startup script (`start-server.sh`)
- ✅ Comprehensive README documentation
- ✅ Build error fixes and optimizations

## 🚀 Development Workflow

### Local Development

For local development, clone this repository and set up the development environment:

Requirements: Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

```bash
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to the frontend directory
cd GramSetu/frontend

# Use the automated startup script
./start-server.sh

# OR manually install and run
npm install
cp .env.example .env
npm run dev
```

### Development Options

**Local IDE Development**
- Clone the repository to your local machine
- Use your preferred IDE (VS Code, WebStorm, etc.)
- Follow the setup instructions above

**Edit directly in GitHub**
- Navigate to desired files
- Click "Edit" button (pencil icon)
- Make changes and commit

**Use GitHub Codespaces**
- Navigate to repository main page
- Click "Code" button → "Codespaces" tab
- Click "New codespace"
- Edit files and commit changes

## 🌐 Deployment

### Production Build
```bash
# Build for production
npm run build

# Or use the automated build script
./build.sh
```

### Static Hosting
The built files in the `dist/` directory can be deployed to any static hosting service:
- **Vercel**: Connect your GitHub repository for automatic deployments
- **Netlify**: Drag and drop the `dist/` folder or connect via Git
- **GitHub Pages**: Use GitHub Actions for automated deployment
- **AWS S3 + CloudFront**: For scalable cloud hosting

### Server Deployment
For server-based deployments:
- **Docker**: Containerize the application using the provided Dockerfile
- **Node.js Server**: Serve the built files using Express or similar
- **CDN**: Use a Content Delivery Network for global distribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Update translations if UI text is modified
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is part of the SAP Hackfest submission for rural finance solutions.

## 📞 Support

For technical support or questions:
- Create an issue in this repository
- Contact the development team
- Check the project documentation and README files

## 📚 Documentation

Additional documentation can be found in:
- `/docs/` directory - API documentation and guides
- `/backend/` directory - Backend services documentation  
- `/infrastructure/` directory - Deployment and infrastructure guides
---

**Made with ❤️ for rural India's financial inclusion**
