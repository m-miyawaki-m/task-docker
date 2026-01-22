# 勤怠管理アプリ Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Vue + Vite + Vuetify で勤怠管理PWAアプリを構築する

**Architecture:** localStorage をバックエンドモックとして使用し、Pinia で状態管理。Geolocation API と Nominatim で位置情報を取得・住所変換する。

**Tech Stack:** Vue 3, Vite, Vuetify 3, Pinia, Vue Router, vite-plugin-pwa, TypeScript

---

## Task 1: プロジェクト初期化

**Files:**
- Create: `attendance-app/` ディレクトリ全体

**Step 1: Vite + Vue プロジェクト作成**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker
npm create vite@latest attendance-app -- --template vue-ts
```
Expected: `attendance-app/` ディレクトリが作成される

**Step 2: 依存パッケージインストール**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
npm install
npm install vuetify @mdi/font
npm install vue-router pinia
npm install -D vite-plugin-pwa
```
Expected: `node_modules/` にパッケージがインストールされる

**Step 3: 動作確認**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
npm run dev
```
Expected: `http://localhost:5173` でVueアプリが起動

**Step 4: Commit**

```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
git add .
git commit -m "feat: initialize Vue + Vite project with dependencies"
```

---

## Task 2: Vuetify セットアップ

**Files:**
- Create: `attendance-app/src/plugins/vuetify.ts`
- Modify: `attendance-app/src/main.ts`

**Step 1: Vuetify プラグイン作成**

Create `attendance-app/src/plugins/vuetify.ts`:
```typescript
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
        },
      },
    },
  },
})
```

**Step 2: main.ts を更新**

Replace `attendance-app/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import App from './App.vue'

const app = createApp(App)

app.use(createPinia())
app.use(vuetify)

app.mount('#app')
```

**Step 3: App.vue を更新**

Replace `attendance-app/src/App.vue`:
```vue
<template>
  <v-app>
    <v-main>
      <v-container>
        <h1>勤怠くん</h1>
        <p>セットアップ完了</p>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
</script>
```

**Step 4: 動作確認**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
npm run dev
```
Expected: Vuetifyのスタイルが適用された画面が表示される

**Step 5: Commit**

```bash
git add .
git commit -m "feat: setup Vuetify with Material Design theme"
```

---

## Task 3: 型定義とストレージサービス

**Files:**
- Create: `attendance-app/src/types/index.ts`
- Create: `attendance-app/src/services/storage.ts`

**Step 1: 型定義作成**

Create `attendance-app/src/types/index.ts`:
```typescript
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
```

**Step 2: ストレージサービス作成**

Create `attendance-app/src/services/storage.ts`:
```typescript
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
```

**Step 3: Commit**

```bash
git add .
git commit -m "feat: add type definitions and storage service"
```

---

## Task 4: 位置情報サービス

**Files:**
- Create: `attendance-app/src/services/geolocation.ts`

**Step 1: Geolocation サービス作成**

Create `attendance-app/src/services/geolocation.ts`:
```typescript
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
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat: add geolocation service with reverse geocoding"
```

---

## Task 5: 認証ストア (Pinia)

**Files:**
- Create: `attendance-app/src/stores/auth.ts`

**Step 1: 認証ストア作成**

Create `attendance-app/src/stores/auth.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { storage } from '@/services/storage'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)

  const isLoggedIn = computed(() => currentUser.value !== null)

  function init() {
    storage.init()
    currentUser.value = storage.getCurrentUser()
  }

  function login(email: string, password: string): boolean {
    const users = storage.getUsers()
    const user = users.find((u) => u.email === email && u.password === password)

    if (user) {
      currentUser.value = user
      storage.setCurrentUser(user)
      return true
    }
    return false
  }

  function logout() {
    currentUser.value = null
    storage.setCurrentUser(null)
  }

  return { currentUser, isLoggedIn, init, login, logout }
})
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat: add auth store with login/logout"
```

---

## Task 6: 勤怠ストア (Pinia)

**Files:**
- Create: `attendance-app/src/stores/attendance.ts`

**Step 1: 勤怠ストア作成**

Create `attendance-app/src/stores/attendance.ts`:
```typescript
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
    const today = new Date().toISOString().split('T')[0]
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
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat: add attendance store with clock-in/clock-out"
```

---

## Task 7: Vue Router セットアップ

**Files:**
- Create: `attendance-app/src/router/index.ts`
- Modify: `attendance-app/src/main.ts`

**Step 1: ルーター作成**

Create `attendance-app/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: 'login' }
  }

  if (to.name === 'login' && authStore.isLoggedIn) {
    return { name: 'home' }
  }
})

export default router
```

**Step 2: main.ts にルーター追加**

Replace `attendance-app/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(vuetify)
app.use(router)

// 認証状態を初期化
const authStore = useAuthStore()
authStore.init()

app.mount('#app')
```

**Step 3: Commit**

```bash
git add .
git commit -m "feat: add Vue Router with auth guard"
```

---

## Task 8: ログイン画面

**Files:**
- Create: `attendance-app/src/views/LoginView.vue`

**Step 1: ログイン画面作成**

Create `attendance-app/src/views/LoginView.vue`:
```vue
<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-4">
          <v-card-title class="text-h5 text-center">
            勤怠くん
          </v-card-title>
          <v-card-subtitle class="text-center">
            ログイン
          </v-card-subtitle>

          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="メールアドレス"
                type="email"
                prepend-inner-icon="mdi-email"
                required
                :error-messages="errorMessage ? ' ' : ''"
              />

              <v-text-field
                v-model="password"
                label="パスワード"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                required
                :error-messages="errorMessage"
              />

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                class="mt-4"
                :loading="isLoading"
              >
                ログイン
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-text class="text-caption text-center text-grey">
            テスト用: test@example.com / password123
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  isLoading.value = true
  errorMessage.value = ''

  // 少し遅延を入れてローディング表示
  await new Promise((resolve) => setTimeout(resolve, 500))

  const success = authStore.login(email.value, password.value)

  if (success) {
    router.push({ name: 'home' })
  } else {
    errorMessage.value = 'メールアドレスまたはパスワードが違います'
  }

  isLoading.value = false
}
</script>
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat: add login view"
```

---

## Task 9: 勤怠画面

**Files:**
- Create: `attendance-app/src/views/HomeView.vue`

**Step 1: 勤怠画面作成**

Create `attendance-app/src/views/HomeView.vue`:
```vue
<template>
  <v-container>
    <!-- ヘッダー -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex justify-space-between align-center">
          <h1 class="text-h5">勤怠くん</h1>
          <v-btn variant="text" @click="handleLogout">
            ログアウト
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- 現在時刻 -->
    <v-row>
      <v-col class="text-center">
        <div class="text-h6">{{ currentDate }}</div>
        <div class="text-h3 font-weight-bold">{{ currentTime }}</div>
      </v-col>
    </v-row>

    <!-- 出勤・退勤ボタン -->
    <v-row class="my-6">
      <v-col cols="6">
        <v-btn
          color="primary"
          size="x-large"
          block
          :loading="attendanceStore.isLoading"
          @click="handleClockIn"
        >
          <v-icon start>mdi-login</v-icon>
          出勤
        </v-btn>
      </v-col>
      <v-col cols="6">
        <v-btn
          color="secondary"
          size="x-large"
          block
          :loading="attendanceStore.isLoading"
          @click="handleClockOut"
        >
          <v-icon start>mdi-logout</v-icon>
          退勤
        </v-btn>
      </v-col>
    </v-row>

    <!-- エラー表示 -->
    <v-row v-if="attendanceStore.error">
      <v-col>
        <v-alert type="error" closable @click:close="attendanceStore.error = null">
          {{ attendanceStore.error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- 本日の記録 -->
    <v-row>
      <v-col>
        <v-card>
          <v-card-title>本日の記録</v-card-title>
          <v-card-text>
            <v-list v-if="attendanceStore.todayRecords.length > 0">
              <v-list-item
                v-for="record in attendanceStore.todayRecords"
                :key="record.id"
              >
                <template #prepend>
                  <v-icon :color="record.type === 'clock-in' ? 'primary' : 'secondary'">
                    {{ record.type === 'clock-in' ? 'mdi-login' : 'mdi-logout' }}
                  </v-icon>
                </template>

                <v-list-item-title>
                  {{ record.type === 'clock-in' ? '出勤' : '退勤' }}:
                  {{ formatTime(record.timestamp) }}
                </v-list-item-title>

                <v-list-item-subtitle class="mt-1">
                  <div class="d-flex align-center">
                    <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
                    {{ record.location.latitude.toFixed(6) }},
                    {{ record.location.longitude.toFixed(6) }}
                  </div>
                  <div class="text-caption">
                    {{ record.location.address }}
                  </div>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <div v-else class="text-center text-grey py-4">
              まだ記録がありません
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 成功ダイアログ -->
    <v-dialog v-model="showSuccessDialog" max-width="400">
      <v-card>
        <v-card-title class="text-center">
          <v-icon :color="lastAction === 'clock-in' ? 'primary' : 'secondary'" size="64">
            {{ lastAction === 'clock-in' ? 'mdi-check-circle' : 'mdi-check-circle' }}
          </v-icon>
        </v-card-title>
        <v-card-text class="text-center text-h6">
          {{ lastAction === 'clock-in' ? '出勤' : '退勤' }}しました
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="showSuccessDialog = false">OK</v-btn>
          <v-spacer />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAttendanceStore } from '@/stores/attendance'

const router = useRouter()
const authStore = useAuthStore()
const attendanceStore = useAttendanceStore()

const currentDate = ref('')
const currentTime = ref('')
const showSuccessDialog = ref(false)
const lastAction = ref<'clock-in' | 'clock-out'>('clock-in')

let timer: number

function updateDateTime() {
  const now = new Date()
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  }
  currentDate.value = now.toLocaleDateString('ja-JP', options)
  currentTime.value = now.toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function handleClockIn() {
  if (!authStore.currentUser) return

  try {
    await attendanceStore.clockIn(authStore.currentUser.id)
    lastAction.value = 'clock-in'
    showSuccessDialog.value = true
  } catch {
    // エラーはストアで処理済み
  }
}

async function handleClockOut() {
  if (!authStore.currentUser) return

  try {
    await attendanceStore.clockOut(authStore.currentUser.id)
    lastAction.value = 'clock-out'
    showSuccessDialog.value = true
  } catch {
    // エラーはストアで処理済み
  }
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  updateDateTime()
  timer = window.setInterval(updateDateTime, 1000)

  if (authStore.currentUser) {
    attendanceStore.loadRecords(authStore.currentUser.id)
  }
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>
```

**Step 2: Commit**

```bash
git add .
git commit -m "feat: add home view with clock-in/clock-out"
```

---

## Task 10: App.vue 更新とルーティング

**Files:**
- Modify: `attendance-app/src/App.vue`

**Step 1: App.vue 更新**

Replace `attendance-app/src/App.vue`:
```vue
<template>
  <v-app>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
</script>
```

**Step 2: 動作確認**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
npm run dev
```
Expected:
1. `http://localhost:5173` → ログイン画面にリダイレクト
2. `test@example.com` / `password123` でログイン
3. 勤怠画面で出勤・退勤ボタンが動作

**Step 3: Commit**

```bash
git add .
git commit -m "feat: update App.vue with router-view"
```

---

## Task 11: PWA 設定

**Files:**
- Modify: `attendance-app/vite.config.ts`
- Create: `attendance-app/public/manifest.json`

**Step 1: vite.config.ts 更新**

Replace `attendance-app/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico'],
      manifest: {
        name: '勤怠くん',
        short_name: '勤怠くん',
        description: '勤怠管理アプリ',
        theme_color: '#1976D2',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

**Step 2: アイコン作成（プレースホルダー）**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app/public
# シンプルなSVGアイコンを作成
cat > pwa-192x192.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
  <rect width="192" height="192" fill="#1976D2"/>
  <text x="96" y="110" font-size="80" text-anchor="middle" fill="white">勤</text>
</svg>
EOF
```

Note: 本番では適切なPNGアイコンを用意する

**Step 3: Commit**

```bash
git add .
git commit -m "feat: add PWA configuration"
```

---

## Task 12: ビルドと最終確認

**Step 1: TypeScript エラーチェック**

Run:
```bash
cd /home/m-miyawaki/dev/task-docker/attendance-app
npm run build
```
Expected: エラーなくビルド完了

**Step 2: プレビュー確認**

Run:
```bash
npm run preview
```
Expected: `http://localhost:4173` で本番ビルドが動作

**Step 3: 最終コミット**

```bash
git add .
git commit -m "chore: verify build and PWA setup"
```

---

## 完了チェックリスト

- [ ] Task 1: プロジェクト初期化
- [ ] Task 2: Vuetify セットアップ
- [ ] Task 3: 型定義とストレージサービス
- [ ] Task 4: 位置情報サービス
- [ ] Task 5: 認証ストア
- [ ] Task 6: 勤怠ストア
- [ ] Task 7: Vue Router セットアップ
- [ ] Task 8: ログイン画面
- [ ] Task 9: 勤怠画面
- [ ] Task 10: App.vue 更新
- [ ] Task 11: PWA 設定
- [ ] Task 12: ビルドと最終確認
