import React from 'react';

export default function Header({ title }) {
  return (
    <header className='header'>
      <h1>{title || 'Vibe Coder Template'}</h1>
    </header>
  );
}
