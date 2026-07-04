import * as React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModeToggle } from '../components/mode-toggle'

// Mock useTheme hook from next-themes
const setThemeMock = jest.fn()
jest.mock('next-themes', () => ({
  useTheme: () => ({
    theme: 'light',
    setTheme: setThemeMock,
  }),
}))

// Mock Shadcn DropdownMenu components to make them testable in JSDOM
jest.mock('@/components/ui/dropdown-menu', () => {
  return {
    DropdownMenu: ({ children }: any) => <div data-testid="dropdown">{children}</div>,
    DropdownMenuTrigger: ({ children }: any) => <div data-testid="dropdown-trigger">{children}</div>,
    DropdownMenuContent: ({ children }: any) => <div data-testid="dropdown-content">{children}</div>,
    DropdownMenuItem: ({ children, onClick }: any) => (
      <button onClick={onClick}>{children}</button>
    ),
  }
})

describe('ModeToggle Component', () => {
  beforeEach(() => {
    setThemeMock.mockClear()
  })

  test('renders ModeToggle component successfully', () => {
    render(<ModeToggle />)
    const button = screen.getByRole('button', { name: /chuyển giao diện/i })
    expect(button).toBeInTheDocument()
  })

  test('triggers theme change when clicking items', () => {
    render(<ModeToggle />)

    // In mocked dropdown, items are rendered in the DOM directly
    const lightOption = screen.getByRole('button', { name: /Sáng \(Light\)/i })
    const darkOption = screen.getByRole('button', { name: /Tối \(Dark\)/i })
    const systemOption = screen.getByRole('button', { name: /Hệ thống \(System\)/i })

    expect(lightOption).toBeInTheDocument()
    expect(darkOption).toBeInTheDocument()
    expect(systemOption).toBeInTheDocument()

    // Click on the dark mode item
    fireEvent.click(darkOption)
    expect(setThemeMock).toHaveBeenCalledWith('dark')

    // Click on the light mode item
    fireEvent.click(lightOption)
    expect(setThemeMock).toHaveBeenCalledWith('light')

    // Click on the system mode item
    fireEvent.click(systemOption)
    expect(setThemeMock).toHaveBeenCalledWith('system')
  })
})
