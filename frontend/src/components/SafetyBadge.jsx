import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

export default function SafetyBadge({ status = 'SAFE', size = 'md', className = '' }) {
  const normStatus = (status || 'SAFE').toUpperCase();

  const configs = {
    SAFE: {
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      icon: ShieldCheck,
      iconColor: 'text-emerald-600',
      label: 'SAFE'
    },
    CAUTION: {
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      icon: AlertTriangle,
      iconColor: 'text-amber-600',
      label: 'CAUTION'
    },
    AVOID: {
      bg: 'bg-rose-50 text-rose-800 border-rose-200',
      icon: XCircle,
      iconColor: 'text-rose-600',
      label: 'AVOID'
    },
    UNKNOWN: {
      bg: 'bg-slate-100 text-slate-700 border-slate-200',
      icon: HelpCircle,
      iconColor: 'text-slate-500',
      label: 'UNKNOWN'
    }
  };

  const config = configs[normStatus] || configs.UNKNOWN;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold'
  };

  const iconSizes = {
    sm: 13,
    md: 15,
    lg: 18
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-xs transition-colors ${config.bg} ${sizeClasses[size] || sizeClasses.md} ${className}`}
      role="status"
      aria-label={`Safety status: ${config.label}`}
    >
      <Icon size={iconSizes[size] || 15} className={config.iconColor} aria-hidden="true" />
      <span>{config.label}</span>
    </span>
  );
}
