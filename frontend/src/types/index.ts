
export type UserRole = 'lender' | 'borrower';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface LoanApplication {
  id: string;
  borrowerId: string;
  borrowerName: string;
  amount: number;
  purpose: string;
  term: number; // in months
  interestRate: number;
  status: 'pending' | 'approved' | 'rejected' | 'disbursed';
  creditScore: number;
  monthlyIncome: number;
  employmentType: string;
  appliedDate: string;
  documents: string[];
}

export interface CreditScore {
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  factors: {
    paymentHistory: number;
    creditUtilization: number;
    creditHistory: number;
    creditMix: number;
    newCredit: number;
  };
}

export interface RepaymentSchedule {
  id: string;
  loanId: string;
  installmentNumber: number;
  dueDate: string;
  amount: number;
  principal: number;
  interest: number;
  status: 'paid' | 'pending' | 'overdue';
}

export interface DashboardStats {
  totalAmount: number;
  activeLoans: number;
  pendingApplications: number;
  defaultRate: number;
}
