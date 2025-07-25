
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import Layout from '../components/common/Layout';
import CreditScoreCard from '../components/common/CreditScoreCard';
import LoanApplicationForm from '../components/forms/LoanApplicationForm';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { loanService, creditService, dashboardService } from '../services/api';
import { LoanApplication, CreditScore, DashboardStats } from '../types';
import { Plus, CreditCard, Clock, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const BorrowerDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useSelector((state: RootState) => state.auth);
  const [loans, setLoans] = useState<LoanApplication[]>([]);
  const [creditScore, setCreditScore] = useState<CreditScore | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [loansData, creditData, statsData] = await Promise.all([
          loanService.getLoanApplications(user?.id),
          creditService.getCreditScore(user?.id ?? ''),
          dashboardService.getDashboardStats('borrower')
        ]);
        
        setLoans(loansData);
        setCreditScore(creditData);
        setStats(statsData);
      } catch (error) {
        toast.error('Failed to load dashboard data');
        console.error('Error loading dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.id]);

  const handleLoanApplicationSubmit = (newLoan: LoanApplication) => {
    setLoans(prev => [newLoan, ...prev]);
    setShowApplicationForm(false);
  };

  const getStatusIcon = (status: LoanApplication['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'disbursed':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: LoanApplication['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'disbursed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {t('dashboard.welcome')}, {user?.name}
            </h1>
            <p className="text-muted-foreground mt-1">{t('dashboard.subtitle')}</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowApplicationForm(true)}
            className="bg-sapBlue-600 text-white px-6 py-3 rounded-lg hover:bg-sapBlue-700 transition-colors flex items-center space-x-2 glass"
          >
            <Plus className="w-5 h-5" />
            <span>{t('loans.applyForLoan')}</span>
          </motion.button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{t('dashboard.totalAmount')}</p>
                  <p className="text-2xl font-bold text-foreground">₹{stats.totalAmount.toLocaleString()}</p>
                </div>
                <CreditCard className="w-8 h-8 text-sapBlue-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{t('dashboard.activeLoans')}</p>
                  <p className="text-2xl font-bold text-foreground">{stats.activeLoans}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{t('dashboard.pendingApplications')}</p>
                  <p className="text-2xl font-bold text-foreground">{stats.pendingApplications}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass rounded-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{t('loans.creditScore')}</p>
                  <p className="text-2xl font-bold text-foreground">{creditScore?.score}</p>
                </div>
                <div className="w-8 h-8 bg-gradient-to-r from-sapBlue-500 to-sapBlue-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">{creditScore?.grade}</span>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Credit Score Card */}
        {creditScore && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <CreditScoreCard creditScore={creditScore} />
          </motion.div>
        )}

        {/* Loan Applications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass rounded-lg"
        >
          <div className="p-6 border-b border-border/50">
            <h2 className="text-xl font-semibold text-foreground">{t('loans.loanApplication')}</h2>
          </div>
          
          <div className="p-6">
            {loans.length === 0 ? (
              <div className="text-center py-12">
                <CreditCard className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">{t('loans.noApplications')}</p>
                <button
                  onClick={() => setShowApplicationForm(true)}
                  className="mt-4 text-sapBlue-600 hover:text-sapBlue-700 font-medium"
                >
                  {t('loans.applyForLoan')}
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {loans.map((loan) => (
                  <motion.div
                    key={loan.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-medium text-gray-900">{loan.purpose}</h3>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(loan.status)}
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(loan.status)}`}>
                          {t(`common.${loan.status}`)}
                        </span>
                      </div>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>{t('loans.borrower')}:</span>
                        <span className="font-medium">{user?.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{t('loans.amount')}:</span>
                        <span className="font-medium">₹{loan.amount.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{t('loans.loanPurpose')}:</span>
                        <span>{loan.purpose}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{t('loans.creditScore')}:</span>
                        <span>{creditScore?.score}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{t('common.status')}:</span>
                        <span>{t(`common.${loan.status}`)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{t('common.actions')}:</span>
                        <span>{loan.appliedDate}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>

        {/* Loan Application Form Modal */}
        {showApplicationForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="glass rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <LoanApplicationForm
                onSubmit={handleLoanApplicationSubmit}
                onCancel={() => setShowApplicationForm(false)}
              />
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default BorrowerDashboard;
