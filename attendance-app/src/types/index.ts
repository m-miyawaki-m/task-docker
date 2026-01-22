export interface User {
  id: string
  email: string
  name: string
  password: string
}

export interface Location {
  latitude: number
  longitude: number
  address: string
}

export interface AttendanceRecord {
  id: string
  userId: string
  type: 'clock-in' | 'clock-out'
  timestamp: string
  location: Location
}
