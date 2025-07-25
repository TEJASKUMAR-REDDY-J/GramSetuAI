import { User, UserRole, LoanApplication, CreditScore, DashboardStats } from '../types';

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const authService = {
  async login(userId: string, password: string, role?: UserRole): Promise<User> {
    await delay(1000);
    
    // Bypass: Accept any userId/password combination
    // Use provided role or default to borrower
    const userRole: UserRole = role ?? 'borrower';
    
    // Generate a more realistic name from userId
    const name = userId.replace(/[^a-zA-Z]/g, '').charAt(0).toUpperCase() + 
                 userId.replace(/[^a-zA-Z]/g, '').slice(1).toLowerCase() || 
                 `User ${userId}`;
    
    const user: User = {
      id: userId, // Use the provided userId instead of generating a random one
      name: name,
      email: `${userId}@gramsetu.com`, // Generate email from userId
      role: userRole,
      avatar: '/api/placeholder/40/40'
    };
    
    return user;
  },

  async register(userData: {
    userId: string;
    name: string;
    password: string;
    role: UserRole;
    phone: string;
    age: string;
    gender: string;
    location: string;
    education: string;
    familyType: string;
    familySize: string;
    occupation: string;
    specificWork: string;
    monthlyIncome: string;
    incomeSeasonality: string;
    houseType: string;
    landHolding: string;
    hasMobile: string;
    hasTwoWheeler: string;
    hasBankAccount: string;
    loanHistory: string;
    digitalLiteracy: string;
  }): Promise<User> {
    await delay(1500);
    
    // Bypass: Accept any registration data
    const user: User = {
      id: userData.userId, // Use the provided userId instead of generating a random one
      name: userData.name,
      email: `${userData.userId}@gramsetu.com`, // Generate email from userId
      role: userData.role,
      avatar: '/api/placeholder/40/40'
    };
    
    return user;
  }
};

export const loanService = {
  async getLoanApplications(userId?: string): Promise<LoanApplication[]> {
    await delay(800);
    
    // Generate some dummy loan applications for demo purposes - Indian context
    const dummyLoans: LoanApplication[] = [
      {
        id: 'loan001',
        borrowerId: userId ?? 'user123',
        borrowerName: 'Rajesh Kumar',
        amount: 150000, // ₹1,50,000 for tractor
        purpose: 'Tractor Purchase',
        term: 24,
        interestRate: 7.5,
        status: 'approved',
        creditScore: 720,
        monthlyIncome: 35000, // ₹35,000 monthly income
        employmentType: 'Farmer',
        appliedDate: '2024-01-15',
        documents: ['aadhar_card.pdf', 'land_records.pdf', 'income_certificate.pdf']
      },
      {
        id: 'loan002',
        borrowerId: userId ?? 'user123',
        borrowerName: 'Priya Sharma',
        amount: 75000, // ₹75,000 for dairy farming
        purpose: 'Dairy Farming Equipment',
        term: 18,
        interestRate: 8.0,
        status: 'pending',
        creditScore: 680,
        monthlyIncome: 28000, // ₹28,000 monthly income
        employmentType: 'Farmer',
        appliedDate: '2024-07-20',
        documents: ['aadhar_card.pdf', 'bank_statement.pdf', 'land_ownership.pdf']
      },
      {
        id: 'loan003',
        borrowerId: userId ?? 'user123',
        borrowerName: 'Suresh Patel',
        amount: 200000, // ₹2,00,000 for crop cultivation
        purpose: 'Crop Cultivation & Seeds',
        term: 12,
        interestRate: 6.5,
        status: 'approved',
        creditScore: 750,
        monthlyIncome: 42000, // ₹42,000 monthly income
        employmentType: 'Farmer',
        appliedDate: '2024-03-10',
        documents: ['aadhar_card.pdf', 'kisan_card.pdf', 'soil_test_report.pdf']
      }
    ];
    
    // Filter by userId if provided
    if (userId) {
      return dummyLoans.filter(loan => loan.borrowerId === userId);
    }
    
    return dummyLoans;
  },

  async createLoanApplication(data: Partial<LoanApplication>): Promise<LoanApplication> {
    await delay(1000);
    
    // Create a new loan application with provided data - Indian context
    const newLoan: LoanApplication = {
      id: `loan${Date.now()}`,
      borrowerId: data.borrowerId ?? `user${Date.now()}`,
      borrowerName: data.borrowerName ?? 'New Farmer',
      amount: data.amount ?? 100000, // Default ₹1,00,000
      purpose: data.purpose ?? 'Agricultural Development',
      term: data.term ?? 18, // 18 months default for farm loans
      interestRate: data.interestRate ?? 7.5, // Better rate for farmers
      status: 'pending',
      creditScore: data.creditScore ?? 680,
      monthlyIncome: data.monthlyIncome ?? 30000, // ₹30,000 default income
      employmentType: data.employmentType ?? 'Farmer',
      appliedDate: new Date().toISOString().split('T')[0],
      documents: data.documents ?? ['aadhar_card.pdf']
    };
    return newLoan;
  },

  async updateLoanStatus(loanId: string, status: LoanApplication['status']): Promise<void> {
    await delay(500);
    console.log(`Loan ${loanId} status updated to ${status}`);
  }
};

export const creditService = {
  async getCreditScore(userId: string): Promise<CreditScore> {
    await delay(600);
    
    // Generate a realistic credit score based on userId
    const hash = userId.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    const baseScore = 650 + (Math.abs(hash) % 200); // Score between 650-850
    
    // Determine grade based on score
    let grade: 'A' | 'B' | 'C' | 'D' | 'E';
    if (baseScore >= 800) grade = 'A';
    else if (baseScore >= 750) grade = 'B';
    else if (baseScore >= 700) grade = 'C';
    else if (baseScore >= 650) grade = 'D';
    else grade = 'E';
    
    return {
      score: baseScore,
      grade,
      factors: {
        paymentHistory: 85 + (Math.abs(hash) % 15),
        creditUtilization: 70 + (Math.abs(hash * 2) % 25),
        creditHistory: 80 + (Math.abs(hash * 3) % 20),
        creditMix: 75 + (Math.abs(hash * 4) % 20),
        newCredit: 85 + (Math.abs(hash * 5) % 10)
      }
    };
  }
};

export const dashboardService = {
  async getDashboardStats(userRole: string): Promise<DashboardStats> {
    await delay(400);
    
    // Generate realistic dummy stats based on user role - Indian context
    if (userRole === 'lender') {
      return {
        totalAmount: 45000000, // ₹4.5 Crore total disbursed
        activeLoans: 128,
        pendingApplications: 23,
        defaultRate: 1.8
      };
    } else {
      // Borrower stats
      return {
        totalAmount: 425000, // ₹4,25,000 total borrowed
        activeLoans: 2,
        pendingApplications: 1,
        defaultRate: 0
      };
    }
  }
};
