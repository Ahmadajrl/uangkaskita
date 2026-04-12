import React from 'react';
import { motion } from 'motion/react';
import { Wallet, User, Lock, ChevronDown, ArrowRight, EyeOff } from 'lucide-react';
import { cn } from './lib/utils';

interface LoginProps {
  onLogin: () => void;
  onBack: () => void;
}

export default function Login({ onLogin, onBack }: LoginProps) {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-background">
      {/* Background Decor */}
      <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-primary-neon/5 blur-[120px]" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] rounded-full bg-primary-neon/5 blur-[100px]" />
      
      {/* Grid Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-20">
        <div 
          className="absolute inset-0" 
          style={{ 
            backgroundImage: 'radial-gradient(#2fff94 0.5px, transparent 0.5px)', 
            backgroundSize: '32px 32px' 
          }} 
        />
      </div>

      <motion.main 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-[480px] z-10"
      >
        {/* Logo Section */}
        <div className="flex flex-col items-center mb-10 text-center">
          <button 
            onClick={onBack}
            className="w-16 h-16 bg-surface-high rounded-2xl flex items-center justify-center mb-6 neon-shadow hover:scale-105 transition-transform"
          >
            <Wallet className="text-primary-neon w-10 h-10" />
          </button>
          <h1 className="font-headline font-black text-4xl tracking-tighter text-primary-neon mb-2">KAS KITA</h1>
          <p className="text-on-surface-variant font-medium tracking-tight">Manajemen Keuangan Kelas Digital</p>
        </div>

        {/* Login Card */}
        <div className="glass-effect rounded-3xl p-8 md:p-10 border border-on-surface-variant/10 relative">
          <form 
            onSubmit={(e) => { e.preventDefault(); onLogin(); }}
            className="space-y-6"
          >
            {/* Username */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant px-1">Username</label>
              <div className="relative flex items-center">
                <User className="absolute left-4 text-on-surface-variant w-5 h-5" />
                <input 
                  type="text"
                  placeholder="Masukkan username"
                  className="w-full bg-surface-low border-none rounded-xl py-4 pl-12 pr-4 text-on-background placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary-neon/20 transition-all outline-none"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant px-1">Password</label>
              <div className="relative flex items-center">
                <Lock className="absolute left-4 text-on-surface-variant w-5 h-5" />
                <input 
                  type="password"
                  placeholder="••••••••"
                  className="w-full bg-surface-low border-none rounded-xl py-4 pl-12 pr-12 text-on-background placeholder:text-on-surface-variant/40 focus:ring-2 focus:ring-primary-neon/20 transition-all outline-none"
                />
                <EyeOff className="absolute right-4 text-on-surface-variant w-5 h-5 cursor-pointer hover:text-primary-neon transition-colors" />
              </div>
            </div>

            {/* Selection Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant px-1">Kelas</label>
                <div className="relative">
                  <select className="w-full appearance-none bg-surface-low border-none rounded-xl py-4 pl-4 pr-10 text-on-background focus:ring-2 focus:ring-primary-neon/20 transition-all outline-none cursor-pointer">
                    <option disabled selected value="">Pilih</option>
                    <option value="10">Kelas X</option>
                    <option value="11">Kelas XI</option>
                    <option value="12">Kelas XII</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none w-5 h-5" />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant px-1">Jurusan</label>
                <div className="relative">
                  <select className="w-full appearance-none bg-surface-low border-none rounded-xl py-4 pl-4 pr-10 text-on-background focus:ring-2 focus:ring-primary-neon/20 transition-all outline-none cursor-pointer">
                    <option disabled selected value="">Pilih</option>
                    <option value="RPL">RPL</option>
                    <option value="TKJ">TKJ</option>
                    <option value="MM">MM</option>
                    <option value="AKL">AKL</option>
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none w-5 h-5" />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button 
              type="submit"
              className="w-full bg-primary-neon hover:bg-primary-neon/90 text-primary-dark font-black py-4 rounded-3xl transition-all duration-300 transform active:scale-95 shadow-[0_0_20px_rgba(47,255,148,0.2)] mt-4 uppercase tracking-widest text-sm flex items-center justify-center gap-2"
            >
              <span>Masuk Aplikasi</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>

          {/* Bottom Links */}
          <div className="mt-8 flex flex-col items-center gap-4">
            <a href="#" className="text-sm text-on-surface-variant hover:text-primary-neon transition-colors font-medium">Lupa password akun?</a>
            <div className="h-[1px] w-12 bg-on-surface-variant/20" />
            <p className="text-sm text-on-surface-variant/60">
              Belum memiliki akun? <a href="#" className="text-primary-neon font-bold">Daftar</a>
            </p>
          </div>
        </div>

        {/* Footer Note */}
        <p className="mt-8 text-center text-on-surface-variant/40 text-[11px] uppercase tracking-widest font-medium">
          © 2024 KAS KITA. Digital Vault for Students.
        </p>
      </motion.main>
    </div>
  );
}
