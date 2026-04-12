import React from 'react';
import { motion } from 'motion/react';
import { 
  Bell, 
  Wallet, 
  PlusCircle, 
  Trash2, 
  LayoutDashboard, 
  History, 
  LogOut,
  ChevronDown
} from 'lucide-react';
import { cn } from './lib/utils';

interface AdminDashboardProps {
  onLogout: () => void;
}

export default function AdminDashboard({ onLogout }: AdminDashboardProps) {
  const recentData = [
    { id: 1, name: 'Andi Pratama', date: '12 Feb 2024', status: 'Tepat Waktu', amount: 'Rp 20.000', meta: 'Minggu ke-2 Feb' },
    { id: 2, name: 'Budi Santoso', date: '05 Feb 2024', status: 'Telat', amount: 'Rp 20.000', meta: 'Minggu ke-1 Feb' },
    { id: 3, name: 'Citra Kirana', date: '12 Feb 2024', status: 'Tepat Waktu', amount: 'Rp 20.000', meta: 'Minggu ke-2 Feb' },
  ];

  return (
    <div className="bg-background text-on-background min-h-screen pb-32">
      {/* Top Bar */}
      <header className="fixed top-0 left-0 w-full h-16 bg-surface-low/80 backdrop-blur-xl flex justify-between items-center px-6 z-50 border-b border-primary-neon/5">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-surface-high flex items-center justify-center overflow-hidden border border-primary-neon/20">
            <img 
              src="https://picsum.photos/seed/admin/100/100" 
              alt="Admin" 
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
            />
          </div>
          <span className="text-xl font-black tracking-tighter text-primary-neon font-headline uppercase">KAS KITA</span>
        </div>
        <div className="flex items-center gap-4">
          <button className="text-on-surface-variant hover:bg-surface-high transition-colors p-2 rounded-full">
            <Bell className="w-6 h-6" />
          </button>
        </div>
      </header>

      <main className="pt-24 px-4 md:px-8 max-w-7xl mx-auto space-y-8">
        {/* Welcome & Summary */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-2">
            <h1 className="text-3xl md:text-5xl font-headline font-extrabold tracking-tight text-on-background">
              Halo, <span className="text-primary-neon">Admin</span>
            </h1>
            <p className="text-on-surface-variant text-lg">
              Status Keuangan Kelas: <span className="text-primary-neon font-bold">XII RPL 1 - Rekayasa Perangkat Lunak</span>
            </p>
          </div>
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-effect rounded-3xl p-6 neon-shadow flex flex-col justify-between items-start bg-surface-low border border-primary-neon/10"
          >
            <div className="flex justify-between w-full items-start">
              <span className="text-on-surface-variant font-medium uppercase tracking-widest text-[10px]">Total Kas</span>
              <Wallet className="text-primary-neon w-5 h-5" />
            </div>
            <div className="mt-4">
              <h2 className="text-4xl font-headline font-black text-on-background tracking-tighter">Rp 2.450.000</h2>
              <p className="text-primary-neon text-sm font-medium mt-1">↑ 12% dari bulan lalu</p>
            </div>
          </motion.div>
        </section>

        {/* Main Content Grid */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Input Form */}
          <div className="lg:col-span-5">
            <div className="bg-surface-low rounded-[2rem] p-8 border border-on-surface-variant/10">
              <h3 className="text-xl font-headline font-bold text-on-background mb-6 flex items-center gap-2">
                <PlusCircle className="text-primary-neon w-6 h-6" />
                Input Pembayaran
              </h3>
              <form className="space-y-5">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-widest">Nama Siswa</label>
                  <input 
                    type="text"
                    placeholder="Contoh: Ahmad Fauzan"
                    className="w-full bg-background border-none rounded-xl text-on-background placeholder:text-on-surface-variant/30 focus:ring-2 focus:ring-primary-neon/20 py-3 px-4 transition-all outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-widest">Tanggal</label>
                    <input 
                      type="date"
                      className="w-full bg-background border-none rounded-xl text-on-background focus:ring-2 focus:ring-primary-neon/20 py-3 px-4 transition-all outline-none"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-widest">Status</label>
                    <div className="relative">
                      <select className="w-full bg-background border-none rounded-xl text-on-background focus:ring-2 focus:ring-primary-neon/20 py-3 px-4 transition-all outline-none appearance-none cursor-pointer">
                        <option>Tepat Waktu</option>
                        <option>Telat</option>
                      </select>
                      <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none w-4 h-4" />
                    </div>
                  </div>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-widest">Nominal (Rp)</label>
                  <input 
                    type="number"
                    placeholder="20000"
                    className="w-full bg-background border-none rounded-xl text-on-background placeholder:text-on-surface-variant/30 focus:ring-2 focus:ring-primary-neon/20 py-3 px-4 transition-all outline-none"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase ml-1 tracking-widest">Keterangan</label>
                  <textarea 
                    placeholder="Kas Minggu ke-2 Februari"
                    rows={2}
                    className="w-full bg-background border-none rounded-xl text-on-background placeholder:text-on-surface-variant/30 focus:ring-2 focus:ring-primary-neon/20 py-3 px-4 transition-all outline-none resize-none"
                  />
                </div>
                <button 
                  type="submit"
                  className="w-full bg-primary-neon hover:bg-primary-neon/90 text-primary-dark font-bold py-4 rounded-xl transition-all active:scale-95 flex items-center justify-center gap-2 mt-4 shadow-lg shadow-primary-neon/10"
                >
                  Simpan Data
                </button>
              </form>
            </div>
          </div>

          {/* Stats & Table */}
          <div className="lg:col-span-7 space-y-6">
            {/* Chart Placeholder */}
            <div className="bg-surface-low rounded-[2rem] p-6 border border-on-surface-variant/10">
              <h3 className="text-lg font-headline font-bold text-on-background mb-6">Distribusi Status Bayar</h3>
              <div className="flex items-end justify-around h-48 gap-4 px-4">
                <div className="flex flex-col items-center flex-1 max-w-[80px] gap-2">
                  <div className="w-full bg-primary-neon rounded-t-xl relative group" style={{ height: '85%' }}>
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-high px-2 py-1 rounded text-[10px] text-primary-neon font-bold">85%</div>
                  </div>
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase">Tepat Waktu</span>
                </div>
                <div className="flex flex-col items-center flex-1 max-w-[80px] gap-2">
                  <div className="w-full bg-red-500/40 rounded-t-xl relative group" style={{ height: '15%' }}>
                    <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-high px-2 py-1 rounded text-[10px] text-red-500 font-bold">15%</div>
                  </div>
                  <span className="text-[10px] font-bold text-on-surface-variant uppercase">Telat</span>
                </div>
              </div>
            </div>

            {/* Table */}
            <div className="bg-surface-low rounded-[2rem] overflow-hidden border border-on-surface-variant/10">
              <div className="p-6 flex justify-between items-center border-b border-on-surface-variant/5">
                <h3 className="text-lg font-headline font-bold text-on-background">Riwayat Data Kas</h3>
                <button className="text-primary-neon text-[10px] font-bold uppercase tracking-widest hover:underline">Lihat Semua</button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-surface-high/50 text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">
                    <tr>
                      <th className="px-6 py-4">Nama Siswa</th>
                      <th className="px-6 py-4">Tanggal</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Nominal</th>
                      <th className="px-6 py-4 text-center">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-on-surface-variant/5">
                    {recentData.map((row) => (
                      <tr key={row.id} className="hover:bg-surface-high/30 transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-semibold text-on-background">{row.name}</div>
                          <div className="text-[10px] text-on-surface-variant">{row.meta}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-on-surface-variant">{row.date}</td>
                        <td className="px-6 py-4">
                          <span className={cn(
                            "px-2 py-1 rounded-full text-[10px] font-black uppercase",
                            row.status === 'Tepat Waktu' ? "bg-primary-neon/10 text-primary-neon" : "bg-red-500/10 text-red-500"
                          )}>
                            {row.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-bold text-primary-neon">{row.amount}</td>
                        <td className="px-6 py-4 text-center">
                          <button className="text-red-500 hover:bg-red-500/10 p-2 rounded-lg transition-all active:scale-90">
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Bottom Nav (Mobile) */}
      <nav className="fixed bottom-0 w-full z-50 flex justify-around items-center px-4 pb-8 pt-4 bg-background/80 backdrop-blur-xl border-t border-primary-neon/10 md:hidden">
        <button className="flex flex-col items-center justify-center bg-primary-neon/10 text-primary-neon rounded-2xl px-6 py-2 active:scale-95">
          <LayoutDashboard className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Dashboard</span>
        </button>
        <button className="flex flex-col items-center justify-center text-on-surface-variant px-6 py-2 active:scale-95 hover:text-primary-neon transition-all">
          <History className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">History</span>
        </button>
        <button 
          onClick={onLogout}
          className="flex flex-col items-center justify-center text-on-surface-variant px-6 py-2 active:scale-95 hover:text-primary-neon transition-all"
        >
          <LogOut className="w-6 h-6" />
          <span className="text-[10px] font-bold uppercase tracking-wider mt-1">Logout</span>
        </button>
      </nav>
    </div>
  );
}
