import React from 'react';
import { motion } from 'motion/react';
import { 
  Bell, 
  FileText, 
  PlusCircle, 
  MinusCircle, 
  TrendingUp, 
  Users, 
  LayoutDashboard, 
  History, 
  LogOut,
  ChevronDown
} from 'lucide-react';
import { cn } from './lib/utils';

interface UserDashboardProps {
  onLogout: () => void;
}

export default function UserDashboard({ onLogout }: UserDashboardProps) {
  const transactions = [
    { id: 1, name: 'Andi Pratama', meta: 'XII MIPA 1 • 12 Okt 2023', amount: '+ Rp 50.000', status: 'Berhasil', type: 'in' },
    { id: 2, name: 'Siti Aminah', meta: 'XII MIPA 1 • 11 Okt 2023', amount: '+ Rp 50.000', status: 'Berhasil', type: 'in' },
    { id: 3, name: 'Pengeluaran Lomba', meta: 'Operasional • 08 Okt 2023', amount: '- Rp 250.000', status: 'Keluar', type: 'out' },
    { id: 4, name: 'Budi Sudarsono', meta: 'XII IPS 2 • 05 Okt 2023', amount: '+ Rp 50.000', status: 'Berhasil', type: 'in' },
  ];

  return (
    <div className="bg-background min-h-screen pb-32">
      {/* Top Bar */}
      <header className="fixed top-0 left-0 w-full h-16 bg-background/80 backdrop-blur-xl flex justify-between items-center px-6 z-50 border-b border-primary-neon/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-surface-high flex items-center justify-center overflow-hidden border border-primary-neon/20">
            <img 
              src="https://picsum.photos/seed/user/100/100" 
              alt="User" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
          <span className="text-xl font-black tracking-tighter text-primary-neon font-headline">KAS KITA</span>
        </div>
        <button className="text-on-surface-variant hover:bg-surface-high transition-colors p-2 rounded-xl active:scale-95">
          <Bell className="w-6 h-6" />
        </button>
      </header>

      <main className="pt-24 px-6 max-w-5xl mx-auto space-y-8">
        {/* Total Balance Card */}
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative group"
        >
          <div className="absolute -inset-1 bg-gradient-to-r from-primary-neon/20 to-primary-neon/5 rounded-[2rem] blur opacity-25" />
          <div className="relative glass-effect rounded-[2rem] p-8 overflow-hidden border border-primary-neon/10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
              <div>
                <p className="text-on-surface-variant font-medium tracking-wide uppercase text-xs mb-2">Total Kas Terkumpul</p>
                <h1 className="text-5xl md:text-6xl font-extrabold text-primary-neon font-headline tracking-tighter neon-glow">
                  Rp 14.250.000
                </h1>
              </div>
              <button className="bg-primary-neon text-primary-dark font-bold px-6 py-3 rounded-xl flex items-center gap-2 hover:opacity-90 transition-all active:scale-95 shadow-[0_0_20px_rgba(47,255,148,0.2)]">
                <FileText className="w-5 h-5" />
                Download PDF
              </button>
            </div>
          </div>
        </motion.section>

        {/* Filters */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['Pilih Kelas', 'Semua Jurusan', 'Bulan Ini'].map((filter) => (
            <div key={filter} className="bg-surface-low rounded-xl p-1 relative">
              <select className="w-full bg-transparent border-none text-on-background focus:ring-0 text-sm font-medium p-3 appearance-none cursor-pointer">
                <option value="">{filter}</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none w-4 h-4" />
            </div>
          ))}
        </section>

        {/* Transactions */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold font-headline">Riwayat Transaksi</h2>
            <button className="text-primary-neon text-sm font-medium hover:underline">Lihat Semua</button>
          </div>
          <div className="space-y-3">
            {transactions.map((tx, index) => (
              <motion.div 
                key={tx.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-surface-low hover:bg-surface-high transition-colors p-4 rounded-2xl flex items-center justify-between group cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center",
                    tx.type === 'in' ? "bg-primary-neon/10 text-primary-neon" : "bg-red-500/10 text-red-500"
                  )}>
                    {tx.type === 'in' ? <PlusCircle className="w-6 h-6" /> : <MinusCircle className="w-6 h-6" />}
                  </div>
                  <div>
                    <p className="font-semibold text-on-background">{tx.name}</p>
                    <p className="text-xs text-on-surface-variant">{tx.meta}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={cn(
                    "font-bold",
                    tx.type === 'in' ? "text-primary-neon" : "text-red-500"
                  )}>{tx.amount}</p>
                  <p className={cn(
                    "text-[10px] uppercase tracking-widest font-bold",
                    tx.type === 'in' ? "text-primary-neon/60" : "text-red-500/60"
                  )}>{tx.status}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Stats Bento */}
        <section className="grid grid-cols-2 gap-4">
          <div className="bg-surface-low p-6 rounded-[2rem] flex flex-col justify-between aspect-square border border-primary-neon/5">
            <TrendingUp className="text-primary-neon w-8 h-8" />
            <div>
              <p className="text-3xl font-black font-headline text-on-background">85%</p>
              <p className="text-xs text-on-surface-variant uppercase tracking-tighter font-bold">Ketepatan Bayar</p>
            </div>
          </div>
          <div className="bg-surface-high p-6 rounded-[2rem] flex flex-col justify-between aspect-square border border-primary-neon/10">
            <Users className="text-primary-neon w-8 h-8" />
            <div>
              <p className="text-3xl font-black font-headline text-on-background">240</p>
              <p className="text-xs text-on-surface-variant uppercase tracking-tighter font-bold">Siswa Terdaftar</p>
            </div>
          </div>
        </section>
      </main>

      {/* Bottom Nav */}
      <nav className="fixed bottom-0 w-full z-50 flex justify-around items-center px-4 pb-8 pt-4 bg-background/80 backdrop-blur-xl rounded-t-[2.5rem] border-t border-primary-neon/10 shadow-[0_-8px_40px_rgba(47,255,148,0.08)]">
        <button className="flex flex-col items-center justify-center bg-primary-neon/10 text-primary-neon rounded-2xl px-6 py-2 transition-all active:scale-95">
          <LayoutDashboard className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Dashboard</span>
        </button>
        <button className="flex flex-col items-center justify-center text-on-surface-variant px-6 py-2 hover:text-primary-neon transition-all active:scale-95">
          <History className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">History</span>
        </button>
        <button 
          onClick={onLogout}
          className="flex flex-col items-center justify-center text-on-surface-variant px-6 py-2 hover:text-primary-neon transition-all active:scale-95"
        >
          <LogOut className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Logout</span>
        </button>
      </nav>
    </div>
  );
}
