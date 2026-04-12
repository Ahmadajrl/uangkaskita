import React from 'react';
import { motion } from 'motion/react';
import { Shield, User, Code, ArrowRight, Wallet } from 'lucide-react';
import { cn } from './lib/utils';

interface RoleSelectionProps {
  onSelect: (role: 'admin' | 'user' | 'developer') => void;
}

export default function RoleSelection({ onSelect }: RoleSelectionProps) {
  const roles = [
    {
      id: 'admin',
      title: 'Admin',
      description: 'Manajemen sistem penuh, kontrol otorisasi, dan audit laporan konsolidasi.',
      icon: Shield,
      color: 'text-primary-neon',
    },
    {
      id: 'user',
      title: 'User',
      description: 'Akses personal untuk mencatat transaksi, memantau saldo, dan laporan individu.',
      icon: User,
      color: 'text-primary-neon',
      highlight: true,
    },
    {
      id: 'developer',
      title: 'Developer',
      description: 'Integrasi API, kustomisasi teknis, dan pemeliharaan struktur basis data.',
      icon: Code,
      color: 'text-primary-neon',
    },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden px-6 py-24">
      {/* Background Decor */}
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-primary-neon/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-5%] w-[400px] h-[400px] bg-primary-neon/5 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <header className="fixed top-0 left-0 w-full flex justify-center py-10 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-neon flex items-center justify-center rounded-xl shadow-[0_0_20px_rgba(47,255,148,0.4)]">
            <Wallet className="text-primary-dark w-6 h-6" />
          </div>
          <h1 className="font-headline font-black text-2xl tracking-tighter text-primary-neon">KAS KITA</h1>
        </div>
      </header>

      <main className="w-full max-w-6xl flex flex-col items-center z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 space-y-4"
        >
          <h2 className="font-headline font-extrabold text-4xl md:text-5xl text-on-background tracking-tight">
            Selamat Datang di Kas Kita
          </h2>
          <p className="text-on-surface-variant text-lg max-w-md mx-auto">
            Tentukan peran Anda untuk mulai mengelola ekosistem finansial digital yang cerdas.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
          {roles.map((role, index) => (
            <motion.button
              key={role.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onSelect(role.id as any)}
              className={cn(
                "group relative flex flex-col items-start p-8 rounded-[2rem] bg-surface-low transition-all duration-300 hover:bg-surface-high border border-primary-neon/5 text-left",
                role.highlight && "md:scale-110 md:z-20 border-primary-neon/20 shadow-[0_0_40px_rgba(47,255,148,0.05)]"
              )}
            >
              <div className={cn(
                "mb-8 p-4 rounded-2xl transition-colors duration-300",
                role.highlight ? "bg-primary-neon shadow-[0_0_30px_rgba(47,255,148,0.3)]" : "bg-surface-high group-hover:bg-primary-neon"
              )}>
                <role.icon className={cn(
                  "w-8 h-8",
                  role.highlight ? "text-primary-dark" : "text-primary-neon group-hover:text-primary-dark"
                )} />
              </div>
              
              <div className="mt-auto">
                <h3 className="font-headline font-bold text-2xl text-on-background mb-2">{role.title}</h3>
                <p className="text-on-surface-variant text-sm leading-relaxed mb-6">{role.description}</p>
                <div className="flex items-center gap-2 text-primary-neon font-bold text-xs uppercase tracking-widest">
                  <span>Pilih Role</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>

              {/* Interactive Overlay */}
              <div className={cn(
                "absolute inset-0 border-2 rounded-[2rem] transition-all duration-300",
                role.highlight ? "border-primary-neon/30" : "border-primary-neon/0 group-hover:border-primary-neon/20"
              )} />
            </motion.button>
          ))}
        </div>

        <div className="mt-20 flex items-center gap-4 text-on-surface-variant/40 text-[10px] uppercase tracking-[0.3em] font-bold">
          <div className="h-px w-12 bg-on-surface-variant/20" />
          <span>Enkripsi Vault 256-Bit</span>
          <div className="h-px w-12 bg-on-surface-variant/20" />
        </div>
      </main>
    </div>
  );
}
