
import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { LogOut } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import LanguageSelector from './LanguageSelector';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card/50 backdrop-blur-sm shadow-sm border-b border-border/50">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img src="/Logo.png" alt="GramSetu Logo" className="w-8 h-8 mr-3" />
              <h1 className="text-2xl font-bold text-sapBlue-600">GramSetu</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <LanguageSelector />
              
              <ThemeToggle />
              
              {user && (
                <div className="flex items-center space-x-3">
                  <button 
                    onClick={handleProfileClick}
                    className="text-right hover:bg-white/5 rounded-lg p-2 transition-colors"
                    title="View Profile"
                  >
                    <p className="text-sm font-medium text-foreground hover:text-primary transition-colors">{user.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
                  </button>
                  <button
                    onClick={handleLogout}
                    className="p-2 text-muted-foreground hover:text-foreground transition-colors rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10"
                    title={t('auth.logout')}
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
};

export default Layout;
