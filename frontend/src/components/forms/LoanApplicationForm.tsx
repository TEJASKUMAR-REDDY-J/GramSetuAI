
import React from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { LoanApplication } from '../../types';
import { loanService } from '../../services/api';
import { toast } from 'sonner';

interface LoanApplicationFormData {
  amount: number;
  purpose: string;
  term: number;
  monthlyIncome: number;
  employmentType: string;
}

interface LoanApplicationFormProps {
  onSubmit: (data: LoanApplication) => void;
  onCancel: () => void;
}

const LoanApplicationForm: React.FC<LoanApplicationFormProps> = ({ onSubmit, onCancel }) => {
  const { t } = useTranslation();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoanApplicationFormData>();

  const loanPurposes = [
    'Tractor Purchase',
    'Agricultural Equipment',
    'Crop Cultivation & Seeds',
    'Dairy Farming Equipment',
    'Irrigation System',
    'Livestock Purchase',
    'Farm Land Development',
    'Organic Farming Setup',
    'Cold Storage Construction',
    'Rural Business Setup',
    'Solar Panel Installation',
    'Medical Expenses',
    'Education'
  ];

  const employmentTypes = [
    'Farmer',
    'Agricultural Worker',
    'Self-employed',
    'Small Business Owner',
    'Part-time Worker',
    'Government Employee',
    'Private Employee'
  ];

  const onFormSubmit = async (data: LoanApplicationFormData) => {
    try {
      const loanApplication = await loanService.createLoanApplication({
        ...data,
        borrowerId: 'borrower1',
        borrowerName: 'Current User'
      });
      
      toast.success('Loan application submitted successfully!');
      onSubmit(loanApplication);
    } catch (error) {
      toast.error('Failed to submit loan application');
      console.error('Error submitting loan application:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
    >
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">{t('loans.loanApplication')}</h2>
      
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('loans.loanAmount')} (₹)
            </label>
            <input
              type="number"
              {...register('amount', { 
                required: 'Loan amount is required',
                min: { value: 50000, message: 'Minimum amount is ₹50,000' },
                max: { value: 5000000, message: 'Maximum amount is ₹50,00,000' }
              })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:border-transparent"
              placeholder="100000"
            />
            {errors.amount && <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('loans.loanTerm')} ({t('loans.months')})
            </label>
            <select
              {...register('term', { required: 'Loan term is required' })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:border-transparent"
            >
              <option value="">Select term</option>
              <option value={12}>12 months</option>
              <option value={24}>24 months</option>
              <option value={36}>36 months</option>
              <option value={48}>48 months</option>
              <option value={60}>60 months</option>
            </select>
            {errors.term && <p className="mt-1 text-sm text-red-600">{errors.term.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('loans.loanPurpose')}
            </label>
            <select
              {...register('purpose', { required: 'Loan purpose is required' })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:border-transparent"
            >
              <option value="">Select purpose</option>
              {loanPurposes.map(purpose => (
                <option key={purpose} value={purpose}>{purpose}</option>
              ))}
            </select>
            {errors.purpose && <p className="mt-1 text-sm text-red-600">{errors.purpose.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('loans.monthlyIncome')} (₹)
            </label>
            <input
              type="number"
              {...register('monthlyIncome', { 
                required: 'Monthly income is required',
                min: { value: 15000, message: 'Minimum income is ₹15,000' }
              })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:border-transparent"
              placeholder="30000"
            />
            {errors.monthlyIncome && <p className="mt-1 text-sm text-red-600">{errors.monthlyIncome.message}</p>}
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('loans.employmentType')}
            </label>
            <select
              {...register('employmentType', { required: 'Employment type is required' })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:border-transparent"
            >
              <option value="">Select employment type</option>
              {employmentTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            {errors.employmentType && <p className="mt-1 text-sm text-red-600">{errors.employmentType.message}</p>}
          </div>
        </div>

        <div className="flex justify-end space-x-4 pt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            {t('common.cancel')}
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-sapBlue-600 text-white rounded-md hover:bg-sapBlue-700 disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? t('common.loading') : t('common.submit')}
          </button>
        </div>
      </form>
    </motion.div>
  );
};

export default LoanApplicationForm;
