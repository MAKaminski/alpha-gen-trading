"use client";

import { useSession, signOut } from 'next-auth/react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { User, Mail, Calendar, Settings, LogOut } from 'lucide-react'

interface UserProfileProps {
  className?: string
}

export default function UserProfile({ className = "" }: UserProfileProps) {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="w-full h-32 bg-gray-200 rounded-lg"></div>
      </div>
    )
  }

  if (!session) {
    return null
  }

  const user = session.user

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center space-x-4">
          {user?.image ? (
            <img
              src={user.image}
              alt={user.name || 'User'}
              className="w-16 h-16 rounded-full"
            />
          ) : (
            <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
          )}
          <div>
            <CardTitle className="text-xl">
              {user?.name || 'User'}
            </CardTitle>
            <CardDescription>
              Alpha-Gen Trading Platform User
            </CardDescription>
            <Badge variant="secondary" className="mt-2">
              Active
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          <div className="flex items-center space-x-3">
            <Mail className="w-4 h-4 text-gray-500" />
            <div>
              <p className="text-sm font-medium text-gray-900">Email</p>
              <p className="text-sm text-gray-600">{user?.email}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Calendar className="w-4 h-4 text-gray-500" />
            <div>
              <p className="text-sm font-medium text-gray-900">Member Since</p>
              <p className="text-sm text-gray-600">
                {new Date().toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t">
          <div className="flex flex-col space-y-2">
            <Button variant="outline" size="sm" className="justify-start">
              <Settings className="w-4 h-4 mr-2" />
              Account Settings
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => signOut()}
              className="justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
