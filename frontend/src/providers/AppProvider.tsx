import React from 'react'
import { QueryProvider } from './QueryProvider'
import { ThemeProvider } from './ThemeProvider'
import { ConfigurationProvider } from './ConfigurationProvider'
import { PluginProvider } from './PluginProvider'
import { RouterProvider } from '../routes'

export const AppProvider: React.FC = () => {
  return (
    <ConfigurationProvider>
      <QueryProvider>
        <ThemeProvider>
          <PluginProvider>
            <RouterProvider />
          </PluginProvider>
        </ThemeProvider>
      </QueryProvider>
    </ConfigurationProvider>
  )
}
