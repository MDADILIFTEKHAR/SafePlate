import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import SafetyBadge from '../src/components/SafetyBadge';

describe('SafetyBadge Component', () => {
  it('renders SAFE badge with accessible label and check icon', () => {
    render(<SafetyBadge status="SAFE" />);
    expect(screen.getByText('SAFE')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Safety status: SAFE');
  });

  it('renders AVOID badge with appropriate styling', () => {
    render(<SafetyBadge status="AVOID" />);
    expect(screen.getByText('AVOID')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Safety status: AVOID');
  });

  it('renders CAUTION badge', () => {
    render(<SafetyBadge status="CAUTION" />);
    expect(screen.getByText('CAUTION')).toBeInTheDocument();
  });

  it('renders UNKNOWN badge for unrecognized status', () => {
    render(<SafetyBadge status="UNKNOWN" />);
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument();
  });
});
