"use client";

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { User, Mail, Calendar, Settings } from 'lucide-react'

interface UserProfileProps {
  className?: string
}

export default function UserProfile({ className = "" }: UserProfileProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
          <div>
            <CardTitle className="text-xl">
              Guest User
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
              <p className="text-sm text-gray-600">guest@example.com</p>
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
              className="justify-start text-gray-600"
              disabled
            >
              Authentication Disabled
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
