/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import RoleSelection from './RoleSelection';
import Login from './Login';
import UserDashboard from './UserDashboard';
import AdminDashboard from './AdminDashboard';

type Screen = 'role-selection' | 'login' | 'user-dashboard' | 'admin-dashboard';
type Role = 'admin' | 'user' | 'developer';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('role-selection');
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  const handleRoleSelect = (role: Role) => {
    setSelectedRole(role);
    setCurrentScreen('login');
  };

  const handleLogin = () => {
    if (selectedRole === 'admin') {
      setCurrentScreen('admin-dashboard');
    } else {
      setCurrentScreen('user-dashboard');
    }
  };

  const handleLogout = () => {
    setCurrentScreen('role-selection');
    setSelectedRole(null);
  };

  const handleBack = () => {
    setCurrentScreen('role-selection');
    setSelectedRole(null);
  };

  return (
    <div className="min-h-screen bg-background selection:bg-primary-neon/30">
      <AnimatePresence mode="wait">
        {currentScreen === 'role-selection' && (
          <motion.div
            key="role-selection"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <RoleSelection onSelect={handleRoleSelect} />
          </motion.div>
        )}

        {currentScreen === 'login' && (
          <motion.div
            key="login"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Login onLogin={handleLogin} onBack={handleBack} />
          </motion.div>
        )}

        {currentScreen === 'user-dashboard' && (
          <motion.div
            key="user-dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <UserDashboard onLogout={handleLogout} />
          </motion.div>
        )}

        {currentScreen === 'admin-dashboard' && (
          <motion.div
            key="admin-dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <AdminDashboard onLogout={handleLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
