import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { InaraLogo } from '@/components/ui/logo'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-pink-50 via-white to-cyan-50">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-center">
        <div className="flex justify-center mb-8">
          <InaraLogo className="w-32 h-32" />
        </div>
        <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-pink-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
          INARA HRIS
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Comprehensive HR Management System
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <Button size="lg">
              Login
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              Dashboard
            </Button>
          </Link>
        </div>
        
        <div className="mt-16 grid text-center lg:grid-cols-4 lg:text-left gap-4">
          <div className="group rounded-lg border p-5">
            <h2 className="text-2xl font-semibold mb-3">
              Employee Management
            </h2>
            <p className="text-sm text-muted-foreground">
              Comprehensive employee profiles and document management
            </p>
          </div>
          
          <div className="group rounded-lg border p-5">
            <h2 className="text-2xl font-semibold mb-3">
              Leave & Attendance
            </h2>
            <p className="text-sm text-muted-foreground">
              Multi-country leave policies and attendance tracking
            </p>
          </div>
          
          <div className="group rounded-lg border p-5">
            <h2 className="text-2xl font-semibold mb-3">
              Performance
            </h2>
            <p className="text-sm text-muted-foreground">
              Goal setting, reviews, and performance management
            </p>
          </div>
          
          <div className="group rounded-lg border p-5">
            <h2 className="text-2xl font-semibold mb-3">
              Analytics
            </h2>
            <p className="text-sm text-muted-foreground">
              Comprehensive HR metrics and reporting
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
