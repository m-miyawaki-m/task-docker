# 勤怠管理アプリ 設計ドキュメント

HRMOSライクな勤怠管理PWAアプリ（ミニマム版）

## 概要

| 項目 | 選択 |
|------|------|
| プラットフォーム | PWA |
| フロントエンド | Vue + Vite |
| バックエンド | モック（localStorage） |
| UI | Vuetify |
| 位置情報 | 緯度経度 + 住所（Nominatim API） |

## 機能

1. ログイン機能（モック認証）
2. 出勤・退勤ボタン
3. ボタン押下時に現在地を取得・表示

## 画面構成

```
┌─────────────────────────────────────┐
│         ログイン画面                 │
│  ┌─────────────────────────────┐   │
│  │ メールアドレス               │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ パスワード                   │   │
│  └─────────────────────────────┘   │
│       [ ログイン ]                  │
└─────────────────────────────────────┘
              ↓ ログイン成功
┌─────────────────────────────────────┐
│         勤怠画面                     │
│                                     │
│    2026年1月22日 (水) 15:30         │
│                                     │
│    ┌───────────┐ ┌───────────┐     │
│    │   出勤    │ │   退勤    │     │
│    └───────────┘ └───────────┘     │
│                                     │
│    ─────────────────────────────   │
│    本日の記録:                      │
│    出勤: 09:00                      │
│      📍 35.6812, 139.7671           │
│         東京都千代田区丸の内1丁目   │
│    ─────────────────────────────   │
│                          [ログアウト]│
└─────────────────────────────────────┘
```

### 画面一覧

| 画面 | パス | 説明 |
|------|------|------|
| ログイン | `/login` | メール・パスワード入力 |
| 勤怠 | `/` | 出勤・退勤ボタン、記録表示 |

## データ構造

### localStorage に保存するデータ

```typescript
// ユーザー情報 (モック用)
interface User {
  id: string
  email: string
  name: string
}

// 勤怠記録
interface AttendanceRecord {
  id: string
  userId: string
  type: 'clock-in' | 'clock-out'  // 出勤 or 退勤
  timestamp: string               // ISO 8601形式
  location: {
    latitude: number
    longitude: number
    address: string
  }
}

// localStorageキー
{
  "currentUser": User | null,
  "users": User[],                    // モック用ユーザー一覧
  "attendanceRecords": AttendanceRecord[]
}
```

### モックユーザー（初期データ）

```json
{
  "id": "1",
  "email": "test@example.com",
  "name": "テストユーザー",
  "password": "password123"
}
```

### 勤怠記録の例

```json
{
  "id": "rec_001",
  "userId": "1",
  "type": "clock-in",
  "timestamp": "2026-01-22T09:00:00+09:00",
  "location": {
    "latitude": 35.6812,
    "longitude": 139.7671,
    "address": "東京都千代田区丸の内1丁目"
  }
}
```

## プロジェクト構成

```
attendance-app/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── public/
│   ├── manifest.json        # PWA マニフェスト
│   └── icons/               # アプリアイコン
├── src/
│   ├── main.ts              # エントリーポイント
│   ├── App.vue              # ルートコンポーネント
│   ├── router/
│   │   └── index.ts         # Vue Router 設定
│   ├── stores/
│   │   ├── auth.ts          # 認証状態管理 (Pinia)
│   │   └── attendance.ts    # 勤怠記録管理 (Pinia)
│   ├── services/
│   │   ├── storage.ts       # localStorage操作
│   │   └── geolocation.ts   # 位置情報・逆ジオコーディング
│   ├── views/
│   │   ├── LoginView.vue    # ログイン画面
│   │   └── HomeView.vue     # 勤怠画面
│   └── components/
│       ├── ClockButton.vue      # 出勤・退勤ボタン
│       ├── AttendanceRecord.vue # 記録表示
│       └── LocationDisplay.vue  # 位置情報表示
```

### 主要な依存パッケージ

| パッケージ | 用途 |
|------------|------|
| `vue` | フレームワーク |
| `vite` | ビルドツール |
| `vue-router` | ルーティング |
| `pinia` | 状態管理 |
| `vuetify` | UIコンポーネント |
| `vite-plugin-pwa` | PWA対応 |

## 処理フロー

### 出勤・退勤ボタン押下時のフロー

```
ボタン押下
    ↓
位置情報の許可確認
    ↓ 許可
Geolocation API で緯度経度取得
    ↓
Nominatim API で住所取得
    ↓
localStorageに記録保存
    ↓
画面に結果表示
```

### 位置情報取得 (Geolocation API)

```typescript
navigator.geolocation.getCurrentPosition(
  (position) => {
    const { latitude, longitude } = position.coords
    // → Nominatim で住所取得
  },
  (error) => {
    // エラー処理
  },
  { enableHighAccuracy: true, timeout: 10000 }
)
```

### 逆ジオコーディング (Nominatim)

```
GET https://nominatim.openstreetmap.org/reverse
  ?lat=35.6812
  &lon=139.7671
  &format=json
  &accept-language=ja
```

## エラー処理

| ケース | 動作 |
|--------|------|
| 位置情報の権限拒否 | 「位置情報を許可してください」とダイアログ表示 |
| 位置情報取得失敗 | 「位置情報を取得できませんでした」、リトライボタン表示 |
| 住所取得失敗 | 緯度経度のみ保存、住所は「取得できませんでした」と表示 |
| ログイン失敗 | 「メールアドレスまたはパスワードが違います」と表示 |

## PWA設定

| 項目 | 値 |
|------|------|
| アプリ名 | 勤怠くん（仮） |
| テーマカラー | Vuetifyのprimary色 |
| 表示モード | standalone（ブラウザUIなし） |
| キャッシュ戦略 | Network First（オンライン優先） |
