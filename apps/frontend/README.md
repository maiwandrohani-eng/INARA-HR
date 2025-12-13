# INARA HRIS - Frontend Documentation

## 🎨 Frontend Architecture

Built with **Next.js 14**, **TypeScript**, **TailwindCSS**, and **shadcn/ui**.

```
/apps/frontend
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth pages (login, etc.)
│   ├── dashboard/         # Main application
│   │   ├── employees/
│   │   ├── leave/
│   │   ├── timesheets/
│   │   └── ...
│   ├── layout.tsx
│   ├── page.tsx
│   └── providers.tsx
│
├── components/            # Reusable UI components
│   └── ui/               # shadcn/ui components
│
├── modules/              # Feature modules
│   ├── employees/
│   ├── leave/
│   └── ...
│
├── services/             # API client services
│   ├── auth.service.ts
│   ├── employee.service.ts
│   └── ...
│
├── hooks/                # Custom React hooks
│   ├── use-employees.ts
│   ├── use-leave.ts
│   └── ...
│
├── state/                # State management (Zustand)
│   └── auth.store.ts
│
├── lib/                  # Utilities
│   └── api-client.ts    # Axios instance
│
└── types/                # TypeScript types
```

## 🚀 Getting Started

### Installation

```bash
cd apps/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Edit .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 🔌 API Integration

### API Client Setup

```typescript
// lib/api-client.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Service Layer

```typescript
// services/employee.service.ts
class EmployeeService {
  async getEmployees(): Promise<Employee[]> {
    const response = await apiClient.get('/employees')
    return response.data
  }

  async createEmployee(data: CreateEmployeeData): Promise<Employee> {
    const response = await apiClient.post('/employees', data)
    return response.data
  }
}
```

### React Query Hooks

```typescript
// hooks/use-employees.ts
import { useQuery, useMutation } from '@tanstack/react-query'

export function useEmployees() {
  return useQuery({
    queryKey: ['employees'],
    queryFn: () => employeeService.getEmployees(),
  })
}

export function useCreateEmployee() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: employeeService.createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })
}
```

### Usage in Components

```typescript
'use client'

import { useEmployees, useCreateEmployee } from '@/hooks/use-employees'

export default function EmployeesPage() {
  const { data: employees, isLoading } = useEmployees()
  const createEmployee = useCreateEmployee()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {employees?.map(emp => (
        <div key={emp.id}>{emp.first_name} {emp.last_name}</div>
      ))}
    </div>
  )
}
```

## 🎯 State Management

### Zustand Store (Auth Example)

```typescript
// state/auth.store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      
      login: async (email, password) => {
        const response = await authService.login({ email, password })
        const user = await authService.getCurrentUser()
        set({ user, isAuthenticated: true })
      },
      
      logout: () => {
        authService.logout()
        set({ user: null, isAuthenticated: false })
      },
    }),
    { name: 'auth-storage' }
  )
)
```

### Usage in Components

```typescript
const { user, isAuthenticated, logout } = useAuthStore()
```

## 🎨 UI Components (shadcn/ui)

### Installing Components

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
```

### Usage

```tsx
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export default function Example() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Title</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>Click me</Button>
      </CardContent>
    </Card>
  )
}
```

## 🧭 Routing

Next.js App Router with file-based routing:

```
/app
├── page.tsx                    → /
├── login/page.tsx              → /login
├── dashboard/
│   ├── page.tsx               → /dashboard
│   ├── layout.tsx             → Shared layout
│   ├── employees/
│   │   ├── page.tsx          → /dashboard/employees
│   │   └── [id]/page.tsx     → /dashboard/employees/123
│   └── leave/
│       └── page.tsx          → /dashboard/leave
```

### Navigation

```tsx
import Link from 'next/link'
import { useRouter } from 'next/navigation'

// Link component
<Link href="/dashboard/employees">Employees</Link>

// Programmatic navigation
const router = useRouter()
router.push('/dashboard')
```

## 🔐 Protected Routes

```tsx
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')
  
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```

## 🎨 Styling

### TailwindCSS

```tsx
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h1 className="text-2xl font-bold">Title</h1>
  <Button className="bg-blue-500 hover:bg-blue-600">Action</Button>
</div>
```

### Custom Styles

```css
/* app/globals.css */
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
  }
}
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## 📦 Building for Production

```bash
# Build
npm run build

# Start production server
npm start
```

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t inara-hris-frontend .

# Run container
docker run -p 3000:3000 inara-hris-frontend
```

### Environment Variables

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.inara.org/api/v1
```

## 📝 Development Guidelines

1. **Component Structure:**
   - Keep components small and focused
   - Use TypeScript for type safety
   - Extract reusable logic into custom hooks

2. **Code Organization:**
   - Group by feature, not by type
   - Co-locate related files
   - Use barrel exports (index.ts)

3. **Performance:**
   - Use React Query for data fetching
   - Implement proper loading states
   - Optimize images with next/image

4. **Accessibility:**
   - Use semantic HTML
   - Provide ARIA labels
   - Ensure keyboard navigation

## 🎯 Key Features

- ✅ Server-side rendering (SSR)
- ✅ Client-side navigation
- ✅ Optimized images
- ✅ TypeScript support
- ✅ TailwindCSS styling
- ✅ React Query data fetching
- ✅ Zustand state management
- ✅ Form validation
- ✅ Toast notifications
- ✅ Responsive design
