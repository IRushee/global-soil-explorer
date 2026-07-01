import React, { createContext, useContext } from 'react'
import { configService } from '../services/config'
import { AppConfiguration } from '../types'

const ConfigurationContext = createContext<AppConfiguration>(configService.get())

export const ConfigurationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ConfigurationContext.Provider value={configService.get()}>
      {children}
    </ConfigurationContext.Provider>
  )
}

export const useAppConfig = () => {
  return useContext(ConfigurationContext)
}
