import type { User, AttendanceRecord } from '@/types'

const KEYS = {
  CURRENT_USER: 'currentUser',
  USERS: 'users',
  ATTENDANCE_RECORDS: 'attendanceRecords',
} as const

// モックユーザー初期化
const DEFAULT_USERS: User[] = [
  {
    id: '1',
    email: 'test@example.com',
    name: 'テストユーザー',
    password: 'password123',
  },
]

export const storage = {
  init() {
    if (!localStorage.getItem(KEYS.USERS)) {
      localStorage.setItem(KEYS.USERS, JSON.stringify(DEFAULT_USERS))
    }
    if (!localStorage.getItem(KEYS.ATTENDANCE_RECORDS)) {
      localStorage.setItem(KEYS.ATTENDANCE_RECORDS, JSON.stringify([]))
    }
  },

  getUsers(): User[] {
    const data = localStorage.getItem(KEYS.USERS)
    return data ? JSON.parse(data) : []
  },

  getCurrentUser(): User | null {
    const data = localStorage.getItem(KEYS.CURRENT_USER)
    return data ? JSON.parse(data) : null
  },

  setCurrentUser(user: User | null) {
    if (user) {
      localStorage.setItem(KEYS.CURRENT_USER, JSON.stringify(user))
    } else {
      localStorage.removeItem(KEYS.CURRENT_USER)
    }
  },

  getAttendanceRecords(): AttendanceRecord[] {
    const data = localStorage.getItem(KEYS.ATTENDANCE_RECORDS)
    return data ? JSON.parse(data) : []
  },

  addAttendanceRecord(record: AttendanceRecord) {
    const records = this.getAttendanceRecords()
    records.push(record)
    localStorage.setItem(KEYS.ATTENDANCE_RECORDS, JSON.stringify(records))
  },
}
