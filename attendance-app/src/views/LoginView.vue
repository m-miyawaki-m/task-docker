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
