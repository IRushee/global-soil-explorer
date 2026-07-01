import React from 'react'
import { createBrowserRouter, RouterProvider as ReactRouterProvider } from 'react-router-dom'
import { AppShell } from '../layouts/AppShell'
import { NotFound } from '../layouts/NotFound'

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
])

export const RouterProvider: React.FC = () => {
  return <ReactRouterProvider router={router} />
}
export default router
