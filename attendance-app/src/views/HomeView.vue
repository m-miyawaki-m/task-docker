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
