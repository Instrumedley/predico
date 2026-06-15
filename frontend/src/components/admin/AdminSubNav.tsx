import React from 'react'
import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
    isActive
      ? 'bg-primary-medium text-white'
      : 'text-neutral-DEFAULT hover:bg-neutral-light'
  }`

export const AdminSubNav: React.FC = () => {
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      <NavLink to="/adm" end className={linkClass}>
        Match Results
      </NavLink>
      <NavLink to="/adm/knockout" className={linkClass}>
        Knockout Bracket
      </NavLink>
      <NavLink to="/adm/users" className={linkClass}>
        User Predictions
      </NavLink>
    </div>
  )
}
