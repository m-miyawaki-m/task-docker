import type { Location } from '@/types'

export interface GeolocationError {
  code: 'PERMISSION_DENIED' | 'POSITION_UNAVAILABLE' | 'TIMEOUT' | 'UNKNOWN'
  message: string
}

export async function getCurrentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject({ code: 'UNKNOWN', message: '位置情報がサポートされていません' })
      return
    }

    navigator.geolocation.getCurrentPosition(
      resolve,
      (error) => {
        const errorMap: Record<number, GeolocationError> = {
          1: { code: 'PERMISSION_DENIED', message: '位置情報の使用が許可されていません' },
          2: { code: 'POSITION_UNAVAILABLE', message: '位置情報を取得できませんでした' },
          3: { code: 'TIMEOUT', message: '位置情報の取得がタイムアウトしました' },
        }
        reject(errorMap[error.code] || { code: 'UNKNOWN', message: '不明なエラー' })
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    )
  })
}

export async function reverseGeocode(lat: number, lon: number): Promise<string> {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json&accept-language=ja`

  try {
    const response = await fetch(url, {
      headers: { 'User-Agent': 'AttendanceApp/1.0' },
    })
    const data = await response.json()
    return data.display_name || '住所を取得できませんでした'
  } catch {
    return '住所を取得できませんでした'
  }
}

export async function getLocationWithAddress(): Promise<Location> {
  const position = await getCurrentPosition()
  const { latitude, longitude } = position.coords
  const address = await reverseGeocode(latitude, longitude)

  return { latitude, longitude, address }
}
