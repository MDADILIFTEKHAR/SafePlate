import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MealCard from '../src/components/MealCard';

describe('MealCard Component', () => {
  const sampleMeal = {
    id: 'meal-1',
    slot: 'lunch',
    name: 'Dal Tadka with Steamed Rice',
    description: 'Hearty yellow lentils with cumin and turmeric.',
    cooking_time_minutes: 25,
    estimated_cost: 42,
    safety_status: 'SAFE',
    dietary_tags: ['Vegetarian'],
    ingredients: [
      { name: 'Dal', quantity: '1/2 cup', in_pantry: true, estimated_cost: 15 },
      { name: 'Rice', quantity: '1 cup', in_pantry: true, estimated_cost: 12 }
    ],
    steps: ['Boil dal', 'Steam rice', 'Temper spices'],
    why_recommended: 'High protein and 100% pantry aligned.'
  };

  it('renders meal card with name, cost, time, and safety badge', () => {
    render(<MealCard meal={sampleMeal} slotLabel="lunch" />);
    expect(screen.getByText('Dal Tadka with Steamed Rice')).toBeInTheDocument();
    expect(screen.getByText('25 mins')).toBeInTheDocument();
    expect(screen.getByText('₹42')).toBeInTheDocument();
    expect(screen.getByText('SAFE')).toBeInTheDocument();
  });

  it('expands accordion to reveal ingredients and steps when clicked', () => {
    render(<MealCard meal={sampleMeal} slotLabel="lunch" />);
    const toggleBtn = screen.getByRole('button', { name: /view ingredients/i });
    fireEvent.click(toggleBtn);

    expect(screen.getByText('Dal')).toBeInTheDocument();
    expect(screen.getByText('Boil dal')).toBeInTheDocument();
    expect(screen.getByText(/High protein and 100% pantry aligned/)).toBeInTheDocument();
  });
});
