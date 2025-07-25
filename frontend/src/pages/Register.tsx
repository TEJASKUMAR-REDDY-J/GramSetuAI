import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import { UserRole } from '../types';
import { Building2, User, Mail, Lock, UserPlus, Phone, MapPin, Calendar, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../components/common/ThemeToggle';
import LanguageSelector from '../components/common/LanguageSelector';

const Register: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState<UserRole | null>(null);
  const [formData, setFormData] = useState({
    userId: '',
    name: '',
    password: '',
    confirmPassword: '',
    phone: '',
    age: '',
    gender: '',
    location: '',
    education: '',
    familyType: '',
    familySize: '',
    occupation: '',
    specificWork: '',
    monthlyIncome: '',
    incomeSeasonality: '',
    houseType: '',
    landHolding: '',
    hasMobile: '',
    hasTwoWheeler: '',
    hasBankAccount: '',
    isSHGMember: '',
    loanHistory: '',
    govtScheme: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleRoleSelect = (role: UserRole) => {
    setSelectedRole(role);
    // Clear any existing data
    setFormData({
      userId: '',
      name: '',
      password: '',
      confirmPassword: '',
      phone: '',
      age: '',
      gender: '',
      location: '',
      education: '',
      familyType: '',
      familySize: '',
      occupation: '',
      specificWork: '',
      monthlyIncome: '',
      incomeSeasonality: '',
      houseType: '',
      landHolding: '',
      hasMobile: '',
      hasTwoWheeler: '',
      hasBankAccount: '',
      isSHGMember: '',
      loanHistory: '',
      govtScheme: ''
    });
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleClearAll = () => {
    setFormData({
      userId: '',
      name: '',
      password: '',
      confirmPassword: '',
      phone: '',
      age: '',
      gender: '',
      location: '',
      education: '',
      familyType: '',
      familySize: '',
      occupation: '',
      specificWork: '',
      monthlyIncome: '',
      incomeSeasonality: '',
      houseType: '',
      landHolding: '',
      hasMobile: '',
      hasTwoWheeler: '',
      hasBankAccount: '',
      isSHGMember: '',
      loanHistory: '',
      govtScheme: ''
    });
    toast.success('Form cleared successfully');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRole) return;

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      await authService.register({
        userId: formData.userId,
        name: formData.name,
        password: formData.password,
        role: selectedRole,
        phone: formData.phone,
        age: formData.age,
        gender: formData.gender,
        location: formData.location,
        education: formData.education,
        familyType: formData.familyType,
        familySize: formData.familySize,
        occupation: formData.occupation,
        specificWork: formData.specificWork,
        monthlyIncome: formData.monthlyIncome,
        incomeSeasonality: formData.incomeSeasonality,
        houseType: formData.houseType,
        landHolding: formData.landHolding,
        hasMobile: formData.hasMobile,
        hasTwoWheeler: formData.hasTwoWheeler,
        hasBankAccount: formData.hasBankAccount,
        isSHGMember: formData.isSHGMember,
        loanHistory: formData.loanHistory,
        govtScheme: formData.govtScheme
      });
      
      toast.success(`Registration successful! Welcome to GramSetu, ${formData.name}!`);
      
      // Redirect to login page
      setTimeout(() => {
        navigate('/login');
      }, 1000);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Registration failed. Please try again.');
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

      {/* Back Button - Top Left */}
      <div className="absolute top-4 left-4 z-50">
        <button
          onClick={() => navigate('/login')}
          className="flex items-center space-x-2 glass-tab rounded-lg px-3 py-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{t('auth.backToLogin')}</span>
        </button>
      </div>

      {/* Main Registration Section */}
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass rounded-2xl p-8 w-full max-w-lg relative overflow-hidden"
        >
          <div className="relative z-10">
            <div className="text-center mb-8">
              <div className="flex flex-col items-center justify-center mb-4">
                <img src="/Logo.png" alt="GramSetu Logo" className="w-12 h-12 mb-2" />
                <h1 className="text-3xl font-bold text-foreground">{t('auth.joinTitle')}</h1>
              </div>
              <p className="text-muted-foreground">{t('auth.joinSubtitle')}</p>
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
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center space-x-2 glass-tab border border-border px-4 py-2 rounded-full">
                    {selectedRole === 'lender' ? <Building2 className="w-5 h-5 text-foreground" /> : <User className="w-5 h-5 text-foreground" />}
                    <span className="text-sm font-medium capitalize text-foreground">{selectedRole && t(`auth.${selectedRole}`)}</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.userId')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.userId}
                      onChange={(e) => handleInputChange('userId', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('form.userIdPlaceholder')}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.fullName')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <UserPlus className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                        placeholder={t('form.fullNamePlaceholder')}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.phone')}
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                        placeholder={t('form.phonePlaceholder')}
                      />
                    </div>
                  </div>

                  {selectedRole === 'borrower' && (
                    <>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.age')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.age}
                      onChange={(e) => handleInputChange('age', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      placeholder={t('form.agePlaceholder')}
                      min="18"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.gender')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.gender}
                      onChange={(e) => handleInputChange('gender', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.gender')}
                    >
                      <option value="">{t('form.genderPlaceholder')}</option>
                      <option value="male">{t('form.male')}</option>
                      <option value="female">{t('form.female')}</option>
                      <option value="otherGender">{t('form.otherGender')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.location')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('form.locationPlaceholder')}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.educationLevel')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.education}
                      onChange={(e) => handleInputChange('education', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.educationLevel')}
                    >
                      <option value="">{t('form.educationLevelPlaceholder')}</option>
                      <option value="illiterate">{t('form.illiterate')}</option>
                      <option value="primary">{t('form.primary')}</option>
                      <option value="secondary">{t('form.secondary')}</option>
                      <option value="higherSecondary">{t('form.higherSecondary')}</option>
                      <option value="graduate">{t('form.graduate')}</option>
                      <option value="postGraduate">{t('form.postGraduate')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.familyType')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.familyType}
                      onChange={(e) => handleInputChange('familyType', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.familyType')}
                    >
                      <option value="">{t('form.familyTypePlaceholder')}</option>
                      <option value="joint">{t('form.joint')}</option>
                      <option value="nuclear">{t('form.nuclear')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.totalFamilySize')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.familySize}
                      onChange={(e) => handleInputChange('familySize', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      placeholder={t('form.totalFamilySizePlaceholder')}
                      min="0"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.occupation')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.occupation}
                      onChange={(e) => handleInputChange('occupation', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.occupation')}
                    >
                      <option value="">{t('form.occupationPlaceholder')}</option>
                      <option value="farmer">{t('form.farmer')}</option>
                      <option value="artisan">{t('form.artisan')}</option>
                      <option value="contractLaborer">{t('form.contractLaborer')}</option>
                      <option value="smallBusiness">{t('form.smallBusiness')}</option>
                      <option value="dailyWageWorker">{t('form.dailyWageWorker')}</option>
                      <option value="other">{t('form.other')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.specificWork')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.specificWork}
                      onChange={(e) => handleInputChange('specificWork', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('form.specificWorkPlaceholder')}
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.monthlyIncome')} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.monthlyIncome}
                      onChange={(e) => handleInputChange('monthlyIncome', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      placeholder={t('form.monthlyIncomePlaceholder')}
                      min="0"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.incomeSeasonality')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.incomeSeasonality}
                      onChange={(e) => handleInputChange('incomeSeasonality', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.incomeSeasonality')}
                    >
                      <option value="">{t('form.incomeSeasonalityPlaceholder')}</option>
                      <option value="Regular">{t('form.regular')}</option>
                      <option value="Seasonal">{t('form.seasonal')}</option>
                      <option value="Irregular">{t('form.irregular')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.houseType')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.houseType}
                      onChange={(e) => handleInputChange('houseType', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.houseType')}
                    >
                      <option value="">{t('form.houseTypePlaceholder')}</option>
                      <option value="Kutcha">{t('form.kutcha')}</option>
                      <option value="Semi-pucca">{t('form.semiPucca')}</option>
                      <option value="Pucca">{t('form.pucca')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.landHolding')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.landHolding}
                      onChange={(e) => handleInputChange('landHolding', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.landHolding')}
                    >
                      <option value="">{t('form.landHoldingPlaceholder')}</option>
                      <option value="Landless">{t('form.landless')}</option>
                      <option value="<1 acre">{t('form.lt1acre')}</option>
                      <option value="1-2 acres">{t('form.1to2acres')}</option>
                      <option value="2-5 acres">{t('form.2to5acres')}</option>
                      <option value=">5 acres">{t('form.gt5acres')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.hasMobile')} <span className="text-red-500">*</span>
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasMobile"
                          value="Yes"
                          checked={formData.hasMobile === 'Yes'}
                              onChange={(e) => handleInputChange('hasMobile', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.yes')}</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasMobile"
                          value="No"
                          checked={formData.hasMobile === 'No'}
                              onChange={(e) => handleInputChange('hasMobile', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.no')}</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.hasTwoWheeler')} <span className="text-red-500">*</span>
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasTwoWheeler"
                          value="Yes"
                          checked={formData.hasTwoWheeler === 'Yes'}
                              onChange={(e) => handleInputChange('hasTwoWheeler', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.yes')}</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasTwoWheeler"
                          value="No"
                          checked={formData.hasTwoWheeler === 'No'}
                              onChange={(e) => handleInputChange('hasTwoWheeler', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.no')}</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.hasBankAccount')} <span className="text-red-500">*</span>
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasBankAccount"
                          value="Yes"
                          checked={formData.hasBankAccount === 'Yes'}
                              onChange={(e) => handleInputChange('hasBankAccount', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.yes')}</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="hasBankAccount"
                          value="No"
                          checked={formData.hasBankAccount === 'No'}
                              onChange={(e) => handleInputChange('hasBankAccount', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.no')}</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.isSHGMember')} <span className="text-red-500">*</span>
                    </label>
                        <div className="flex space-x-4 mb-3">
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="isSHGMember"
                          value="Yes"
                              checked={formData.isSHGMember === 'Yes' || (formData.isSHGMember !== 'No' && formData.isSHGMember !== '')}
                              onChange={(e) => handleInputChange('isSHGMember', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.yes')}</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="isSHGMember"
                          value="No"
                          checked={formData.isSHGMember === 'No'}
                              onChange={(e) => handleInputChange('isSHGMember', e.target.value)}
                          className="text-primary focus:ring-primary"
                          required
                        />
                        <span className="text-foreground">{t('form.no')}</span>
                      </label>
                    </div>
                        {(formData.isSHGMember === 'Yes' || (formData.isSHGMember !== 'No' && formData.isSHGMember !== '')) && (
                          <div className="mt-2">
                            <input
                              type="text"
                              value={formData.isSHGMember === 'Yes' ? '' : formData.isSHGMember}
                              onChange={(e) => handleInputChange('isSHGMember', e.target.value)}
                              className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                              placeholder={t('form.shgMemberPlaceholder')}
                            />
                          </div>
                        )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.loanHistory')} <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.loanHistory}
                      onChange={(e) => handleInputChange('loanHistory', e.target.value)}
                      className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                      required
                      aria-label={t('form.loanHistory')}
                    >
                      <option value="">{t('form.loanHistoryPlaceholder')}</option>
                      <option value="None">{t('form.none')}</option>
                      <option value="Informal">{t('form.informal')}</option>
                      <option value="SHG">{t('form.shg')}</option>
                      <option value="Bank">{t('form.bank')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                          {t('form.govtSchemeEnrollment')} <span className="text-red-500">*</span>
                    </label>
                    <div className="flex space-x-4 mb-3" aria-label={t('form.govtSchemeEnrollment')}>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="govtScheme"
                          value="Yes"
                          checked={formData.govtScheme === 'Yes' || (formData.govtScheme !== 'No' && formData.govtScheme !== '')}
                          onChange={(e) => handleInputChange('govtScheme', e.target.value)}
                          className="text-primary focus:ring-primary"
                        />
                        <span className="text-foreground">{t('form.yes')}</span>
                      </label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="radio"
                          name="govtScheme"
                          value="No"
                          checked={formData.govtScheme === 'No'}
                          onChange={(e) => handleInputChange('govtScheme', e.target.value)}
                          className="text-primary focus:ring-primary"
                        />
                        <span className="text-foreground">{t('form.no')}</span>
                      </label>
                    </div>
                    {(formData.govtScheme === 'Yes' || (formData.govtScheme !== 'No' && formData.govtScheme !== '')) && (
                      <div className="mt-2">
                        <input
                          type="text"
                          value={formData.govtScheme === 'Yes' ? '' : formData.govtScheme}
                          onChange={(e) => handleInputChange('govtScheme', e.target.value)}
                          className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                          placeholder={t('form.govtSchemePlaceholder')}
                        />
                      </div>
                    )}
                  </div>
                    </>
                  )}

                  {selectedRole === 'lender' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                          {t('form.institutionName')} <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.name}
                          onChange={(e) => handleInputChange('name', e.target.value)}
                          className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                          placeholder={t('form.institutionNamePlaceholder')}
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                          {t('form.institutionType')} <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={formData.occupation}
                          onChange={(e) => handleInputChange('occupation', e.target.value)}
                          className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground bg-background/50"
                          required
                          aria-label={t('form.institutionType')}
                        >
                          <option value="">{t('form.institutionTypePlaceholder')}</option>
                          <option value="National Bank">{t('form.nationalBank')}</option>
                          <option value="Regional Rural Bank">{t('form.regionalRuralBank')}</option>
                          <option value="Cooperative Bank">{t('form.cooperativeBank')}</option>
                          <option value="Microfinance Institution">{t('form.microfinanceInstitution')}</option>
                          <option value="Non-Banking Financial Company">{t('form.nbfc')}</option>
                          <option value="Other">{t('form.other')}</option>
                        </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                          {t('form.location')} <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.location}
                          onChange={(e) => handleInputChange('location', e.target.value)}
                          className="w-full px-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                          placeholder={t('form.locationPlaceholder')}
                          required
                        />
                      </div>
                    </>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.password')} <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('form.passwordPlaceholder')}
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                      {t('form.confirmPassword')} <span className="text-red-500">*</span>
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <input
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                      className="w-full pl-10 pr-4 py-2 glass-tab rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground bg-background/50"
                      placeholder={t('form.confirmPasswordPlaceholder')}
                      required
                    />
                  </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-border/50 mb-4">
                  <button
                    type="button"
                    onClick={handleClearAll}
                    className="w-full py-2 glass-tab rounded-lg text-red-500 font-medium glass-hover transition-colors hover:text-red-600 hover:bg-red-50/10"
                  >
                    {t('form.clearAll')}
                  </button>
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
                    {isLoading ? t('common.loading') : t('auth.createAccountBtn')}
                  </button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Register; 