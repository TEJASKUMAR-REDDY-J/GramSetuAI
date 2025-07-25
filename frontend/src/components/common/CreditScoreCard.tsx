
import React from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { CreditScore } from '../../types';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface CreditScoreCardProps {
  creditScore: CreditScore;
}

const CreditScoreCard: React.FC<CreditScoreCardProps> = ({ creditScore }) => {
  const { t } = useTranslation();

  // Get current theme for pie chart background
  const isDarkMode = document.documentElement.classList.contains('dark');
  const chartBgColor = isDarkMode ? '#4b5563' : '#e5e7eb'; // gray-600 for dark, gray-200 for light

  const getScoreColor = (score: number) => {
    if (score >= 750) return '#10b981'; // Green
    if (score >= 700) return '#f59e0b'; // Yellow
    if (score >= 650) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getScoreLabel = (score: number) => {
    if (score >= 750) return t('creditScore.excellent');
    if (score >= 700) return t('creditScore.good');
    if (score >= 650) return t('creditScore.fair');
    return t('creditScore.poor');
  };

  const pieData = [
    { name: 'Score', value: creditScore.score, fill: getScoreColor(creditScore.score) },
    { name: 'Remaining', value: 850 - creditScore.score, fill: chartBgColor }
  ];

  const factorsData = [
    { name: t('creditScore.paymentHistory'), value: creditScore.factors.paymentHistory },
    { name: t('creditScore.creditUtilization'), value: creditScore.factors.creditUtilization },
    { name: t('creditScore.creditHistory'), value: creditScore.factors.creditHistory },
    { name: t('creditScore.creditMix'), value: creditScore.factors.creditMix },
    { name: t('creditScore.newCredit'), value: creditScore.factors.newCredit },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">{t('creditScore.title')}</h3>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="text-center">
          <div className="relative w-48 h-48 mx-auto mb-4">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  startAngle={90}
                  endAngle={450}
                  dataKey="value"
                >
                  {pieData.map((entry) => (
                    <Cell key={entry.name} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900 dark:text-white">{creditScore.score}</div>
                <div className="text-sm text-gray-600 dark:text-gray-300">{getScoreLabel(creditScore.score)}</div>
              </div>
            </div>
          </div>
          <div className="text-center">
            <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
              Grade {creditScore.grade}
            </span>
          </div>
        </div>

        <div>
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">{t('creditScore.factors')}</h4>
          <div className="space-y-3">
            {factorsData.map((factor) => (
              <div key={factor.name} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300">{factor.name}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <motion.div
                      className="bg-sapBlue-500 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${factor.value}%` }}
                      transition={{ duration: 0.8, delay: factorsData.indexOf(factor) * 0.1 }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white w-8">{factor.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CreditScoreCard;
