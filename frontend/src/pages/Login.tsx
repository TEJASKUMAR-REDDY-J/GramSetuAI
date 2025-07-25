
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { loginStart, loginSuccess, loginFailure } from '../store/slices/authSlice';
import { authService } from '../services/api';
import { UserRole } from '../types';
import { Building2, User, Mail, Lock, Shield, Zap, Globe, Users, UserPlus } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../components/common/ThemeToggle';
import LanguageSelector from '../components/common/LanguageSelector';

const Login: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    setUserId('');
    setPassword('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole) return;

    setIsLoading(true);
    dispatch(loginStart());

    try {
      const user = await authService.login(userId, password, selectedRole);
      dispatch(loginSuccess(user));
      toast.success(`Welcome back, ${user.name}!`);
      
      // Redirect based on role
      if (user.role === 'lender') {
        navigate('/lenders/dashboard');
      } else {
        navigate('/borrowers/dashboard');
      }
    } catch (error) {
      dispatch(loginFailure());
      toast.error('Invalid credentials. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background/90 to-muted/20">
      {/* Theme Toggle - Top Right */}
      <div className="absolute top-4 right-4 z-50 flex items-center space-x-3">
        <LanguageSelector />
        <ThemeToggle />
      </div>

      {/* Main Login Section */}
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass rounded-2xl p-8 w-full max-w-md relative overflow-hidden"
        >
          <div className="relative z-10">
            <div className="text-center mb-8">
              <div className="flex flex-col items-center justify-center mb-4">
                <img src="/Logo.png" alt="GramSetu Logo" className="w-12 h-12 mb-2" />
                <h1 className="text-3xl font-bold text-foreground">GramSetu</h1>
              </div>
              <p className="text-muted-foreground">{t('auth.welcomeBack')}</p>
            </div>

            {!selectedRole ? (
              <div className="space-y-4">
                <p className="text-center text-muted-foreground mb-6">{t('auth.selectRole')}</p>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleRoleSelect('lender')}
                  className="w-full p-4 glass-tab rounded-lg glass-hover group"
                >
                  <div className="flex items-center space-x-3">
                    <Building2 className="w-8 h-8 text-primary" />
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">{t('auth.lender')}</h3>
                      <p className="text-sm text-muted-foreground">{t('auth.lenderDesc')}</p>
                    </div>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleRoleSelect('borrower')}
                  className="w-full p-4 glass-tab rounded-lg glass-hover group"
                >
                  <div className="flex items-center space-x-3">
                    <User className="w-8 h-8 text-primary" />
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">{t('auth.borrower')}</h3>
                      <p className="text-sm text-muted-foreground">{t('auth.borrowerDesc')}</p>
                    </div>
                  </div>
                </motion.button>

                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">{t('auth.or')}</span>
                  </div>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => navigate('/register')}
                  className="w-full p-4 glass-tab rounded-lg glass-hover group border-2 border-dashed border-primary/30"
                >
                  <div className="flex items-center justify-center space-x-3">
                    <UserPlus className="w-6 h-6 text-primary" />
                    <div className="text-center">
                      <h3 className="font-semibold text-foreground">{t('auth.createAccount')}</h3>
                      <p className="text-sm text-muted-foreground">{t('auth.registerAs')}</p>
                    </div>
                  </div>
                </motion.button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center space-x-2 glass-tab border border-border px-4 py-2 rounded-full">
                    {selectedRole === 'lender' ? <Building2 className="w-5 h-5 text-foreground" /> : <User className="w-5 h-5 text-foreground" />}
                    <span className="text-sm font-medium text-foreground">{t(`auth.${selectedRole}`)}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    {t('auth.userId')}
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <input
                      type="text"
                      value={userId}
                      onChange={(e) => setUserId(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('auth.userIdLoginPlaceholder')}
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    {t('auth.password')}
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('auth.passwordLoginPlaceholder')}
                      required
                    />
                  </div>
                </div>

                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => setSelectedRole(null)}
                    className="flex-1 py-2 glass-tab rounded-lg text-muted-foreground glass-hover transition-colors"
                  >
                    {t('auth.back')}
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-1 py-2 bg-primary/80 backdrop-blur-sm border border-primary/50 text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
                  >
                    {isLoading ? t('common.loading') : t('auth.login')}
                  </button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>

      {/* About Section - Appears on Scroll */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true, margin: "-100px" }}
        className="min-h-screen flex items-center justify-center p-4"
      >
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-foreground mb-4">{t('about.title')}</h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {t('about.intro')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="glass rounded-xl p-6 text-center"
            >
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">{t('about.secureTitle')}</h3>
              <p className="text-muted-foreground">{t('about.secureDesc')}</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="glass rounded-xl p-6 text-center"
            >
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">{t('about.userCentricTitle')}</h3>
              <p className="text-muted-foreground">{t('about.userCentricDesc')}</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="glass rounded-xl p-6 text-center"
            >
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">{t('about.multilingualTitle')}</h3>
              <p className="text-muted-foreground">{t('about.multilingualDesc')}</p>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-12 glass rounded-xl p-8"
          >
            <div className="text-center">
              <h3 className="text-2xl font-bold text-foreground mb-4">{t('about.futureTitle')}</h3>
              <p className="text-muted-foreground mb-4">{t('about.futureDesc')}</p>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
