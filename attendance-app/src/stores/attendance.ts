import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { storage } from '@/services/storage'
import { getLocationWithAddress, type GeolocationError } from '@/services/geolocation'
import type { AttendanceRecord } from '@/types'

export const useAttendanceStore = defineStore('attendance', () => {
  const records = ref<AttendanceRecord[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const todayRecords = computed(() => {
    const today = new Date().toISOString().split('T')[0] ?? ''
    return records.value.filter((r) => r.timestamp.startsWith(today))
  })

  function loadRecords(userId: string) {
    const allRecords = storage.getAttendanceRecords()
    records.value = allRecords.filter((r) => r.userId === userId)
  }

  async function clockIn(userId: string) {
    isLoading.value = true
    error.value = null

    try {
      const location = await getLocationWithAddress()
      const record: AttendanceRecord = {
        id: `rec_${Date.now()}`,
        userId,
        type: 'clock-in',
        timestamp: new Date().toISOString(),
        location,
      }

      storage.addAttendanceRecord(record)
      records.value.push(record)
    } catch (e) {
      error.value = (e as GeolocationError).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function clockOut(userId: string) {
    isLoading.value = true
    error.value = null

    try {
      const location = await getLocationWithAddress()
      const record: AttendanceRecord = {
        id: `rec_${Date.now()}`,
        userId,
        type: 'clock-out',
        timestamp: new Date().toISOString(),
        location,
      }

      storage.addAttendanceRecord(record)
      records.value.push(record)
    } catch (e) {
      error.value = (e as GeolocationError).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return { records, todayRecords, isLoading, error, loadRecords, clockIn, clockOut }
})
