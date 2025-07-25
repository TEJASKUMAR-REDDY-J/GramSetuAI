import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../store';
import Layout from '../components/common/Layout';
import { loanService } from '../services/api';
import { LoanApplication } from '../types';
import { 
  User, Phone, MapPin, Calendar, Briefcase, CreditCard, 
  Edit3, Save, X, Home, Users, Smartphone, Car, 
  Building, GraduationCap, Banknote, Upload, Lock, ArrowLeft, History
} from 'lucide-react';
import { toast } from 'sonner';

const Profile: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useSelector((state: RootState) => state.auth);
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showLoanHistoryModal, setShowLoanHistoryModal] = useState(false);
  const [loans, setLoans] = useState<LoanApplication[]>([]);
  const [loadingLoans, setLoadingLoans] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [editedData, setEditedData] = useState({
    name: user?.name ?? '',
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

  if (!user) {
    return <div>Loading...</div>;
  }

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    // Here you would typically save to backend
    setIsEditing(false);
    toast.success('Profile updated successfully!');
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset to original values
    setEditedData({
      name: user?.name ?? '',
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
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePasswordChange = () => {
    setShowPasswordModal(true);
  };

  const handlePasswordSave = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('New password and confirmation do not match');
      return;
    }
    if (passwordData.newPassword.length < 6) {
      toast.error('Password must be at least 6 characters long');
      return;
    }
    // Here you would typically send to backend
    setShowPasswordModal(false);
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    toast.success('Password changed successfully!');
  };

  const handlePasswordCancel = () => {
    setShowPasswordModal(false);
    setPasswordData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  const handlePasswordInputChange = (field: string, value: string) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleUploadDocuments = () => {
    // Create a file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.doc,.docx,.jpg,.jpeg,.png';
    input.onchange = (event) => {
      const files = (event.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        toast.success(`${files.length} document(s) selected for upload`);
        // Here you would typically upload to backend
      }
    };
    input.click();
  };

  const handleViewLoanHistory = async () => {
    setLoadingLoans(true);
    setShowLoanHistoryModal(true);
    
    try {
      const loanData = await loanService.getLoanApplications(user?.role || 'borrower', user?.id);
      setLoans(loanData);
    } catch (error) {
      toast.error('Failed to load loan history');
      console.error('Error loading loans:', error);
    } finally {
      setLoadingLoans(false);
    }
  };

  const handleCloseLoanHistory = () => {
    setShowLoanHistoryModal(false);
    setLoans([]);
  };

  const handleBackToDashboard = () => {
    // Navigate back to the appropriate dashboard based on user role
    if (user?.role === 'lender') {
      navigate('/lenders/dashboard');
    } else {
      navigate('/borrowers/dashboard');
    }
  };

  return (
    <Layout>
      <div className="w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full"
        >
          {/* Back Button */}
          <div className="mb-6">
            <button
              onClick={handleBackToDashboard}
              className="flex items-center space-x-2 px-4 py-2 bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>{t('profile.backToDashboard')}</span>
            </button>
          </div>

          {/* Profile Header */}
          <div className="bg-gradient-to-r from-primary/10 to-primary/5 rounded-2xl p-8 mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center">
                    <User className="w-12 h-12 text-primary" />
                  </div>
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                  </div>
                </div>
                <div>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="text-3xl font-bold bg-transparent border-b border-primary text-foreground mb-2"
                      placeholder="Enter your name"
                      aria-label="Name"
                    />
                  ) : (
                    <h1 className="text-3xl font-bold text-foreground mb-2">{user.name}</h1>
                  )}
                  <p className="text-lg text-muted-foreground capitalize mb-1">{t(`auth.${user.role}`)}</p>
                  <p className="text-sm text-muted-foreground">ID: {user.id}</p>
                </div>
              </div>
              
              <div className="flex space-x-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleSave}
                      className="flex items-center space-x-2 px-4 py-2 bg-green-500/20 text-green-600 rounded-lg hover:bg-green-500/30 transition-colors"
                    >
                      <Save className="w-4 h-4" />
                      <span>{t('profile.saveChanges')}</span>
                    </button>
                    <button
                      onClick={handleCancel}
                      className="flex items-center space-x-2 px-4 py-2 bg-red-500/20 text-red-600 rounded-lg hover:bg-red-500/30 transition-colors"
                    >
                      <X className="w-4 h-4" />
                      <span>{t('profile.cancelEdit')}</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleEdit}
                    className="flex items-center space-x-2 px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
                  >
                    <Edit3 className="w-4 h-4" />
                    <span>{t('profile.editProfile')}</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Personal Information */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-card rounded-2xl p-6 border border-border/50"
            >
              <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center">
                <User className="w-6 h-6 mr-3 text-primary" />
                {t('profile.personalInfo')}
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <Phone className="w-5 h-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground">{t('profile.phone')}</p>
                    {isEditing ? (
                      <input
                        type="tel"
                        value={editedData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                        placeholder={t('profile.notAvailable')}
                        aria-label="Phone number"
                      />
                    ) : (
                      <p className="text-foreground">{editedData.phone || t('profile.notAvailable')}</p>
                    )}
                  </div>
                </div>

                {user.role === 'borrower' && (
                  <>
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Calendar className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.age')}</p>
                        {isEditing ? (
                          <input
                            type="number"
                            value={editedData.age}
                            onChange={(e) => handleInputChange('age', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            placeholder={t('profile.notAvailable')}
                            aria-label="Age"
                            min="18"
                            max="100"
                          />
                        ) : (
                          <p className="text-foreground">{editedData.age || t('profile.notAvailable')}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <User className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.gender')}</p>
                        {isEditing ? (
                          <select
                            value={editedData.gender}
                            onChange={(e) => handleInputChange('gender', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            aria-label="Gender"
                          >
                            <option value="">{t('profile.notAvailable')}</option>
                            <option value="male">{t('form.male')}</option>
                            <option value="female">{t('form.female')}</option>
                            <option value="otherGender">{t('form.otherGender')}</option>
                          </select>
                        ) : (
                          <p className="text-foreground">
                            {editedData.gender ? t(`form.${editedData.gender}`) : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                  </>
                )}
                
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <MapPin className="w-5 h-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm text-muted-foreground">{t('profile.location')}</p>
                    {isEditing ? (
                      <input
                        type="text"
                        value={editedData.location}
                        onChange={(e) => handleInputChange('location', e.target.value)}
                        className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                        placeholder={t('profile.notAvailable')}
                        aria-label="Location"
                      />
                    ) : (
                      <p className="text-foreground">{editedData.location || t('profile.notAvailable')}</p>
                    )}
                  </div>
                </div>

                {user.role === 'borrower' && (
                  <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                    <GraduationCap className="w-5 h-5 text-muted-foreground" />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground">{t('profile.education')}</p>
                      {isEditing ? (
                        <select
                          value={editedData.education}
                          onChange={(e) => handleInputChange('education', e.target.value)}
                          className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                          aria-label="Education level"
                        >
                          <option value="">{t('profile.notAvailable')}</option>
                          <option value="illiterate">{t('form.illiterate')}</option>
                          <option value="primary">{t('form.primary')}</option>
                          <option value="secondary">{t('form.secondary')}</option>
                          <option value="higherSecondary">{t('form.higherSecondary')}</option>
                          <option value="graduate">{t('form.graduate')}</option>
                          <option value="postGraduate">{t('form.postGraduate')}</option>
                        </select>
                      ) : (
                        <p className="text-foreground">
                          {editedData.education ? t(`form.${editedData.education}`) : t('profile.notAvailable')}
                        </p>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <Calendar className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">{t('profile.memberSince')}</p>
                    <p className="text-foreground">{new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Account Information */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-card rounded-2xl p-6 border border-border/50"
            >
              <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center">
                <Briefcase className="w-6 h-6 mr-3 text-primary" />
                {t('profile.accountInfo')}
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <CreditCard className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">{t('profile.userId')}</p>
                    <p className="text-foreground">{user.id}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <User className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">{t('profile.accountType')}</p>
                    <p className="text-foreground capitalize">{t(`auth.${user.role}`)}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                  <div className="w-5 h-5 flex items-center justify-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">{t('profile.accountStatus')}</p>
                    <p className="text-green-600 font-medium">{t('profile.active')}</p>
                  </div>
                </div>

                {user.role === 'borrower' && (
                  <>
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Briefcase className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.occupation')}</p>
                        {isEditing ? (
                          <select
                            value={editedData.occupation}
                            onChange={(e) => handleInputChange('occupation', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            aria-label="Occupation"
                          >
                            <option value="">{t('profile.notAvailable')}</option>
                            <option value="farmer">{t('form.farmer')}</option>
                            <option value="artisan">{t('form.artisan')}</option>
                            <option value="contractLaborer">{t('form.contractLaborer')}</option>
                            <option value="smallBusiness">{t('form.smallBusiness')}</option>
                            <option value="dailyWageWorker">{t('form.dailyWageWorker')}</option>
                            <option value="other">{t('form.other')}</option>
                          </select>
                        ) : (
                          <p className="text-foreground">
                            {editedData.occupation ? t(`form.${editedData.occupation}`) : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Banknote className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.monthlyIncome')}</p>
                        {isEditing ? (
                          <input
                            type="number"
                            value={editedData.monthlyIncome}
                            onChange={(e) => handleInputChange('monthlyIncome', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            placeholder={t('profile.notAvailable')}
                            aria-label="Monthly income"
                            min="0"
                          />
                        ) : (
                          <p className="text-foreground">
                            {editedData.monthlyIncome ? `₹${editedData.monthlyIncome}` : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </motion.div>

            {/* Additional sections for borrowers */}
            {user.role === 'borrower' && (
              <>
                {/* Family Information */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                  className="bg-card rounded-2xl p-6 border border-border/50"
                >
                  <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center">
                    <Users className="w-6 h-6 mr-3 text-primary" />
                    {t('profile.familyInfo')}
                  </h2>
                  
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Home className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.familyType')}</p>
                        {isEditing ? (
                          <select
                            value={editedData.familyType}
                            onChange={(e) => handleInputChange('familyType', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            aria-label="Family type"
                          >
                            <option value="">{t('profile.notAvailable')}</option>
                            <option value="joint">{t('form.joint')}</option>
                            <option value="nuclear">{t('form.nuclear')}</option>
                          </select>
                        ) : (
                          <p className="text-foreground">
                            {editedData.familyType ? t(`form.${editedData.familyType}`) : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Users className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.familySize')}</p>
                        {isEditing ? (
                          <input
                            type="number"
                            value={editedData.familySize}
                            onChange={(e) => handleInputChange('familySize', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            placeholder={t('profile.notAvailable')}
                            aria-label="Family size"
                            min="1"
                            max="20"
                          />
                        ) : (
                          <p className="text-foreground">{editedData.familySize || t('profile.notAvailable')}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>

                {/* Assets Information */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  className="bg-card rounded-2xl p-6 border border-border/50"
                >
                  <h2 className="text-xl font-semibold text-foreground mb-6 flex items-center">
                    <Car className="w-6 h-6 mr-3 text-primary" />
                    {t('profile.assetsInfo')}
                  </h2>
                  
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Smartphone className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.hasMobile')}</p>
                        {isEditing ? (
                          <select
                            value={editedData.hasMobile}
                            onChange={(e) => handleInputChange('hasMobile', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            aria-label="Has mobile phone"
                          >
                            <option value="">{t('profile.notAvailable')}</option>
                            <option value="Yes">{t('form.yes')}</option>
                            <option value="No">{t('form.no')}</option>
                          </select>
                        ) : (
                          <p className="text-foreground">
                            {editedData.hasMobile ? t(`form.${editedData.hasMobile.toLowerCase()}`) : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 bg-background/50 rounded-lg">
                      <Building className="w-5 h-5 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm text-muted-foreground">{t('profile.hasBankAccount')}</p>
                        {isEditing ? (
                          <select
                            value={editedData.hasBankAccount}
                            onChange={(e) => handleInputChange('hasBankAccount', e.target.value)}
                            className="mt-1 w-full px-2 py-1 bg-background border border-border rounded text-foreground text-sm"
                            aria-label="Has bank account"
                          >
                            <option value="">{t('profile.notAvailable')}</option>
                            <option value="Yes">{t('form.yes')}</option>
                            <option value="No">{t('form.no')}</option>
                          </select>
                        ) : (
                          <p className="text-foreground">
                            {editedData.hasBankAccount ? t(`form.${editedData.hasBankAccount.toLowerCase()}`) : t('profile.notAvailable')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </>
            )}
          </div>

          {/* Quick Actions */}
          {!isEditing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              className="mt-8 bg-card rounded-2xl p-6 border border-border/50"
            >
              <h2 className="text-xl font-semibold text-foreground mb-6">{t('profile.quickActions')}</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button 
                  onClick={handleViewLoanHistory}
                  className="p-4 bg-purple-500/10 hover:bg-purple-500/20 rounded-xl text-left transition-colors group"
                >
                  <History className="w-8 h-8 text-purple-500 mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-medium text-foreground mb-1">{t('profile.viewLoanHistory')}</h3>
                  <p className="text-sm text-muted-foreground">{t('profile.viewLoanHistoryDesc')}</p>
                </button>
                
                <button 
                  onClick={handlePasswordChange}
                  className="p-4 bg-blue-500/10 hover:bg-blue-500/20 rounded-xl text-left transition-colors group"
                >
                  <Lock className="w-8 h-8 text-blue-500 mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-medium text-foreground mb-1">{t('profile.changePassword')}</h3>
                  <p className="text-sm text-muted-foreground">{t('profile.changePasswordDesc')}</p>
                </button>
                
                <button 
                  onClick={handleUploadDocuments}
                  className="p-4 bg-green-500/10 hover:bg-green-500/20 rounded-xl text-left transition-colors group"
                >
                  <Upload className="w-8 h-8 text-green-500 mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-medium text-foreground mb-1">{t('profile.uploadDocuments')}</h3>
                  <p className="text-sm text-muted-foreground">{t('profile.uploadDocumentsDesc')}</p>
                </button>
              </div>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-40">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-card rounded-2xl p-6 w-full max-w-md border border-border/50"
          >
            <h3 className="text-xl font-semibold text-foreground mb-6 flex items-center">
              <Lock className="w-6 h-6 mr-3 text-primary" />
              {t('profile.changePassword')}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  {t('profile.currentPassword')}
                </label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => handlePasswordInputChange('currentPassword', e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                  placeholder={t('profile.enterCurrentPassword')}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  {t('profile.newPassword')}
                </label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => handlePasswordInputChange('newPassword', e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                  placeholder={t('profile.enterNewPassword')}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  {t('profile.confirmPassword')}
                </label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => handlePasswordInputChange('confirmPassword', e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground"
                  placeholder={t('profile.confirmNewPassword')}
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handlePasswordCancel}
                className="flex-1 py-2 px-4 bg-muted text-muted-foreground rounded-lg hover:bg-muted/80 transition-colors"
              >
                {t('profile.cancelEdit')}
              </button>
              <button
                onClick={handlePasswordSave}
                className="flex-1 py-2 px-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                {t('profile.saveChanges')}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Loan History Modal */}
      {showLoanHistoryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-40">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-card rounded-2xl p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto border border-border/50"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-foreground flex items-center">
                <History className="w-6 h-6 mr-3 text-primary" />
                {t('profile.loanHistory')}
              </h3>
              <button
                onClick={handleCloseLoanHistory}
                className="p-2 hover:bg-muted rounded-lg transition-colors"
                aria-label="Close loan history"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>
            
            <div className="overflow-y-auto max-h-[60vh]">
              {loadingLoans ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <span className="ml-3 text-muted-foreground">{t('common.loading')}</span>
                </div>
              ) : loans.length === 0 ? (
                <div className="text-center py-8">
                  <History className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">{t('profile.noLoanHistory')}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {loans.map((loan) => (
                    <div key={loan.id} className="bg-background/50 rounded-lg p-4 border border-border/30">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                            <Banknote className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <h4 className="font-medium text-foreground">{loan.purpose}</h4>
                            <p className="text-sm text-muted-foreground">
                              {user?.role === 'lender' ? `Borrower: ${loan.borrowerName}` : `Loan ID: ${loan.id}`}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-foreground">₹{loan.amount.toLocaleString()}</p>
                          <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                            loan.status === 'disbursed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                            loan.status === 'approved' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                            loan.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                            'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          }`}>
                            {t(`common.${loan.status}`)}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">{t('profile.interestRate')}</p>
                          <p className="font-medium text-foreground">{loan.interestRate}%</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">{t('profile.loanTerm')}</p>
                          <p className="font-medium text-foreground">{loan.term} {t('profile.months')}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">{t('profile.appliedDate')}</p>
                          <p className="font-medium text-foreground">{new Date(loan.appliedDate).toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">{t('profile.creditScore')}</p>
                          <p className="font-medium text-foreground">{loan.creditScore}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </Layout>
  );
};

export default Profile;
