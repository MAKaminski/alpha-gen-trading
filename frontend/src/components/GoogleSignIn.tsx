"use client";

import { Button } from '@/components/ui/button'
import { LogIn } from 'lucide-react'

interface GoogleSignInProps {
  className?: string
}

export default function GoogleSignIn({ className = "" }: GoogleSignInProps) {
  return (
    <Button
      variant="outline"
      className={`flex items-center space-x-2 ${className}`}
      disabled
    >
      <LogIn className="w-4 h-4" />
      <span>Authentication Disabled</span>
    </Button>
  )
}
