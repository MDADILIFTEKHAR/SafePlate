import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import BudgetTracker from '../src/components/BudgetTracker';

describe('BudgetTracker Component', () => {
  it('renders daily target budget and current used amount', () => {
    const meals = [
      { id: '1', slot: 'breakfast', estimated_cost: 30 },
      { id: '2', slot: 'lunch', estimated_cost: 52 }
    ];
    render(<BudgetTracker targetBudget={150} currentCost={82} meals={meals} />);

    expect(screen.getByText('₹82')).toBeInTheDocument();
    expect(screen.getByText('/ ₹150')).toBeInTheDocument();
    expect(screen.getByText('₹68 left')).toBeInTheDocument();
  });

  it('renders over-budget warning when cost exceeds target', () => {
    render(<BudgetTracker targetBudget={150} currentCost={170} meals={[]} />);
    expect(screen.getByText('₹20 over budget')).toBeInTheDocument();
  });
});
