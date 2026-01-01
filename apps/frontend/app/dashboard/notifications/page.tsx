
/**
 * Notifications Page
 */

'use client'
export const dynamic = "force-dynamic";

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'
import { AnnouncementForm } from '@/components/forms/AnnouncementForm'

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<any[]>([])
  const [announcements, setAnnouncements] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [showAnnouncementForm, setShowAnnouncementForm] = useState(false)

  useEffect(() => {
    fetchNotifications()
    fetchUnreadCount()
    fetchAnnouncements()
  }, [])

  const fetchAnnouncements = async () => {
    try {
      const response = await apiClient.get('/notifications/announcements')
      setAnnouncements(response.data || [])
    } catch (error) {
      console.error('Failed to fetch announcements:', error)
    }
  }

  const fetchNotifications = async () => {
    try {
      const response = await apiClient.get('/notifications/notifications')
      setNotifications(response.data)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await apiClient.get('/notifications/notifications/unread-count')
      setUnreadCount(response.data.unread_count)
    } catch (error) {
      console.error('Failed to fetch unread count:', error)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await apiClient.post(`/notifications/notifications/${notificationId}/read`)
      fetchNotifications()
      fetchUnreadCount()
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-gray-600 mt-2">
            {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
          </p>
        </div>
        <Button onClick={() => setShowAnnouncementForm(true)}>Create Announcement</Button>
      </div>

      <AnnouncementForm 
        open={showAnnouncementForm} 
        onOpenChange={setShowAnnouncementForm}
        onSubmitSuccess={() => {
          fetchAnnouncements()
          fetchNotifications()
        }}
      />

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : notifications.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No notifications yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {notifications.map((notification) => (
            <Card key={notification.id} className={!notification.is_read ? 'border-l-4 border-l-blue-500' : ''}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{notification.title}</CardTitle>
                    <CardDescription>{notification.message}</CardDescription>
                  </div>
                  {!notification.is_read && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => markAsRead(notification.id)}
                    >
                      Mark as read
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500">{notification.created_at}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {announcements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Announcements</CardTitle>
            <CardDescription>Company-wide announcements and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {announcements.map((announcement) => (
                <div key={announcement.id} className={`p-4 border rounded-lg ${announcement.priority === 'urgent' ? 'border-l-4 border-l-red-500' : announcement.priority === 'high' ? 'border-l-4 border-l-orange-500' : ''}`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{announcement.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{announcement.content}</p>
                      <div className="flex gap-2 mt-2">
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">{announcement.announcement_type}</span>
                        {announcement.priority === 'urgent' && (
                          <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded">Urgent</span>
                        )}
                        {announcement.priority === 'high' && (
                          <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded">High Priority</span>
                        )}
                      </div>
                    </div>
                    <span className={`text-xs ${announcement.is_published ? 'text-green-600' : 'text-gray-400'}`}>
                      {announcement.is_published ? 'Published' : 'Draft'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

